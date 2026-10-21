# Troubleshooting and internal implementation (for developers)

For people reading the code / working on the protocol. For everyday use, see the [README](../README.md).

## Gateways

| Gateway | Address | Signing | Purpose |
| --- | --- | --- | --- |
| GW1 | `api-gw-toc.zeekrlife.com` | SHA1 sorted signature | SMS verification code, phone-number login (JWT) |
| GW2 | `api.zeekrline.com` | HMAC-SHA1 | Exchange for ecar accessToken, vehicle list/status, command fallback |
| GW3 | `snc-tsp-api.zeekrlife.com` | HMAC-SHA256 + AES-encrypted VIN | Login, vehicle list, latest status, remote control |
| GRIC | `gric-api.geely.com` / `gric-zhf-api.geely.com` | HMAC-SHA256 (18 headers + query string + method + path) | **Independent second channel**: token exchange, vehicle status, remote control |

GRIC and SNC have different field conventions: vehicle status `v2.0` (SNC is `v1.0`), the charge limit is in **tenths of a percent** (`950` = 95%),
coordinates are already in decimal degrees, and the lock field is `0` = unlocked / non-zero = locked — these are all normalized uniformly in the parsing layer.

### GRIC signing

Key `e70024ed24bda3cbd4a6295ed3fac5aa` (the `dkAppSecret` from the App's `mmkv/ble_sdk`),
signing class `com.geely.snc.network.http.biz.interceptor.GLSignInterceptor`. Base string:

```
18 whitelisted headers (sorted ascending by name, "name:value\n")
+ [query string "k=v&…" sorted ascending by key + "\n"]      ← must come before METHOD
+ [base64(md5(body)) + "\n"]               ← only POST / has body
+ METHOD + "\n" + PATH(path only)
→ base64(HMAC-SHA256(key, base))
```

**Putting the query string after the path always returns `00A06`** (an old trap). GET does not include the body-hash line.
The 18-header whitelist: accept-language, authorization, x-api-signature-nonce, x-api-signature-version,
x-app-id, x-app-version, x-device-brand, x-device-id, x-device-model, x-device-os-version,
x-platform, x-sales-platform, x-tenant-id, x-timestamp, x-tsp-platform, x-vehicle-brand,
x-vehicle-identifier, x-vehicle-series (`accept` / `user-agent` are sent but not signed).

### Tokens (GRIC)

`iss=https://gric-mid-inner.geely.com/ms-auth-service/inner/v1.0/oauth/info`,
`aud=azp=auth_client_zeekr_phone`, RS256; access 7 days / refresh 30 days.
`POST gric-api.geely.com/ms-midground-user/api/v1.0/user/auth/refresh/token`
body `{"refreshToken":"…"}` → `code:"0"` + new access **and new refresh** (server-side rotation, `sid` unchanged).
⇒ refreshing at least once every 7 days = unlimited renewal; on the integration side `_REFRESH_MARGIN_SECONDS=24h`, polling acts as the heartbeat.

⚠️ Single session holder: each rotation invalidates other tokens of the same session ⇒ whoever refreshes last owns it, and the other side gets `00A17`.
**Never call `logout` / `cancel/login` again.**

## Remote control

`POST /ms-remote-control/v1.0/remoteControl/control`, with `serviceParameters` **nested inside `setting`**:

```json
{"command": "start", "serviceId": "ZAF",
 "setting": {"serviceParameters": [{"key": "AC", "value": "true"}]}}
```

`serviceId`: air conditioning `ZAF`, lock `RDL`, unlock `RDU`, windows/sunroof/sunshade `RWS`, horn & lights `RHL`,
charging `RCS`, find car `PCM`. When rejected, fall back to GW2 `PUT /remote-control/vehicle/telematics/{VIN}`.
Attempts on both channels are recorded in the diagnostics under `gateways.command_attempts`.

GRIC uses wider retry intervals (10/30/60/120/170 seconds) — the backend wakes the car and reports back in about 120 seconds measured.

## What is in the diagnostics file

- `payload_summary` — the **field provenance** of each key value (`path` being `null` means that alias did not match, add a `_ALIAS`)
- `vehicle_list_raw` — the raw vehicle list entries (compare field names when the vehicle name/plate is picked wrong)
- `config_entries` — all Zeekr config entries in this HA (id, title, `last_update_success`, last four digits of the phone number, VIN)
- `entities` / `devices` — entity/device registry snapshots, including the `restored` flag
- `gateways` — per-channel return codes, `command_attempts`, `gw3_token_source`,
  `gw3_vin_attempts`, `platform_chain`, `status_source`, `vehicle_list_source`, `endpoint_probe`
- `report_age_seconds` — how stale this current status is

## Field calibration conclusions (verified against real payloads, `BX1E` + `DC1E`)

| Field | Conclusion |
| --- | --- |
| Traction battery SOC | `electricVehicleStatus.chargeLevel` (**not** `maintenanceStatus.mainBatteryStatus.chargeLevel`, which is the 12V battery) |
| 12V battery | `maintenanceStatus.mainBatteryStatus.chargeLevel` / `.voltage` |
| Range | `electricVehicleStatus.distanceToEmptyOnBatteryOnly` (measured 321 km, matches the App) |
| Tire pressure | `maintenanceStatus.tyreStatus{Driver,Passenger,DriverRear,PassengerRear}`, kPa |
| Coordinate scale | fixed-point integer, measured as "degrees × 3,600,000"; the parser auto-detects 3.6e6 / 1e7 / 1e6 / already in degrees |
| Position trust | `basicVehicleStatus.position.posCanBeTrusted` (often false when parked and powered off, used only as an attribute) |
| Lock | the `*LockStatus*` family: `0` = unlocked, non-`0` = locked |
| Charge port lid | `chargeLidAcStatus` / `chargeLidDcAcStatus`: `1` = open, `0` / `2` = closed |
| Whether charging | **comes with the main vehicle status**: `chargeSts` / `chargerState` / `statusOfChargerConnection` / `dcChargeSts`; `chargeUAct` (voltage), `chargeIAct` (current) |
| Estimated full | `timeToFullyCharged`, idle sentinel value `2047` → unknown |
| Sunshade / sunroof | `curtainPos` / `sunroofPos` / `sunCurtainRearPos` = `101` ⇒ not equipped on this car (entity shown as unavailable) |
| Model name | the `modelName` in the list is the catalog config name and **unreliable** (a four-seat AWD Zeekr X actually returned `四座后驱版-001` (four-seat RWD version-001)); the display name is instead taken from `seriesCodeVs`: `BX1E` → Zeekr X, `DC1E` → Zeekr 001 |

Still to be measured: the `_CHARGING_ACTIVE` / `_CHARGING_IDLE` code sets (only `chargeSts=0` observed so far),
the sentinel-mode `RSM` switch values, and `relHumSts` (`103` seen once, outside the humidity range, treated as unknown).

The device name takes the first non-empty value in order of nickname → plate → model, falling back to VIN only when all are empty (`"plateNo": ""` is treated as absent).

## `079001 此接口未被授权` (interface not authorized) (SMS channel)

The two generations of login interfaces issue tokens with different permissions: `identityType: 5` + GW1 JWT (old) can only access the vehicle list and similar;
only `identityType: 10` + `tspCode` (new platform) can reach vehicle status and remote control. Since 0.3.21, the integration
automatically performs one extra new-platform login **the first time it hits `079001`** (`/user/tspCode?tspClientId=…` → log in again with
`identityType: 10`), done only once per process. Since 0.3.24 it also tries several identity values
(GW1 JWT / GW2 token / clientId / userId), with the decision criterion being "whether the vehicle interface lets it through".

Already disproven, do not add back: `X-API-SIGNATURE-VERSION: 2.1`, `X-PROJECT-ID: ZEEKR_CN`,
and both at once (a real device returns `079001` for all, showing the decision is not driven by request headers);
hostnames `gateway-pub-hw-em-cn` / `-em` / `-cn` (cannot be resolved at all in the China region).

Meanings of the responses to `X-VIN` encoding candidates: `079001` = wrong token generation or account not authorized;
`079025 Decrypt X-VIN failed` = what was sent is not ciphertext; `00A02 validation failed` = value too short
(the gateway requires ≥17 characters, exactly the VIN length) ⇒ it must carry the **ciphertext of the VIN**, and the `userVehId` route has been ruled out.

In diagnostics, `endpoint_probe` directly asks the gateway two things: where the permission boundary is (recording the response to each of three requests one by one), and
what `X-VIN` should carry (trying in order `aes(vin)`, `aes(userVehId)`, `userVehId`, `aes(temId)`,
`aes-ecb(vin)`, `aes-zeroiv(vin)`, plaintext VIN; an accepted candidate is adopted and
`vehicle_token_source` is written as `probe:...`). Plaintext VIN and the control item `control:zero-ciphertext`
are only used to map the boundary, marked `adopt=False`, and will never be adopted.

## `079025 Signature authentication failed` (GW3)

Three causes that have been fixed: ① wrong `X-APP-ID` (all GW3 endpoints including login must use `ZEEKRCNCH001M0001`);
② the signature must be the **Base64** of HMAC-SHA256 (44 characters), it had once output hex; ③ the request body serialization must be byte-for-byte identical
(`_json_body` compact JSON + `data=`). The request headers have been aligned with the App capture (`X-APP-OS-VERSION`,
`User-Agent`, spacing in `Content-Type`, nonce as a hyphenated UUID, login without `Authorization` but with `X-VIN`,
`*` → `%2A` in the query). When it still fails, check `gateways.gw3_last_rejected` in diagnostics.

## Why the SMS channel cannot control the car (reviewed 2026-10-12)

User's real-world test: **logging in with the owner account + SMS verification code, tapping a switch in HA "does nothing, the car doesn't move"**. Review conclusion —
**this is not an account problem, it is the channel itself**:

| Evidence | Content |
| --- | --- |
| App local storage | Only GRIC tokens (`aud/azp = auth_client_zeekr_phone` in `files/mmkv/MOD_LOGIN`, iss `gric-mid-inner.geely.com`), **no SNC `user_center_client_phone` token at all** ⇒ the new App controls the car via GRIC, and the SNC leg has been abandoned by the vendor |
| GW3 access-control matrix (measured 09-18) | Under the same GW3 token: control-type (`/ms-remote-control/.../control`) and vehicle-status-type (`/ms-vehicle-status/...`) all return `079001 [SDK]此接口未被授权` (interface not authorized); query-type (`.../queryProcessResult`, `/ms-user-auth/...`) is allowed ⇒ **access control is per-interface granularity, it does not look at whether the account is the owner, nor at `X-VIN` / `serviceParameters`** |
| Fallback pipe | GW2 `PUT /remote-control/vehicle/telematics/{VIN}` returns `1000 操作成功` (operation succeeded) but **the car does not move** (this path is marked `degraded` in the integration, see `async_do_remote_control` in `api_sms.py`) |

⇒ the SMS channel's role is **read-only** (vehicle status works fine via GW2); **car control always goes through GRIC**, and there is no difference between an owner account and
a non-owner account: the same account just needs to obtain a `refreshToken` once in the App (`x-vehicle-identifier`
is **per-vehicle**, so when switching accounts keep the original value; the integration verifies it once in real use before creating the config entry).

To reproduce / gather evidence: `tools/zeekr_gate_check.py` (an all-read-only probe that prints the gateway responses one by one,
`--save docs/zeekr_gate_baseline.json` / `--compare` can compare whether access control has changed).

## Where each of the two onboarding values can be obtained (reviewed 2026-10-12)

| Value | Is it in phone storage | Conclusion |
| --- | --- | --- |
| `refreshToken` / `gric_access` | **Yes**: `MODULE_LOGIN_{ACCESS,REFRESH}_TOKEN` in `files/mmkv/MOD_LOGIN` (mmkv is an append log, take the entry with the largest `iat` for the latest) | on a rooted phone, `tools/zeekr_device_pull.py --gric --write-tokens` can read them out read-only → export with `tools/zeekr_gric_token.py form` |
| `x-vehicle-identifier` | **No**: searching the entire App private directory (mmkv / shared_prefs / logs / cache) byte-by-byte for this value, as well as header names like `vehicle-identifier` / `x-vehicle`, yields **0 hits** | computed on the fly only in the App's runtime memory (the key is assembled at runtime in the native library) ⇒ it **can only be copied from a real request header**, or obtained via memory forensics |

`x-vehicle-identifier` structure: 44-character base64 = 32 bytes = the ciphertext of two AES blocks; decrypting it with various derivations of `vin_key`/`vin_iv`,
`prod_secret`, `_SNC_SECRET` (ECB / CBC, various IVs) produces **all garbage** (re-tested 2026-10-12),
so **do not** expect to compute it offline or statically extract it from the APK (the key for `GEELYCNCH001M0001` is not in the package either).

⇒ the README's value-acquisition section is written with "capture once to get both values" as the main line; the root route only promises the `refreshToken`.

## GRIC error codes

| Code | Meaning |
| --- | --- |
| `00A06` | Signature verification failed (query string position / header list) |
| `00A02` | Missing `x-vehicle-identifier` (or `X-VIN` too short) |
| `00A06 Decrypt X-VEHICLE-IDENTIFIER failed` | The identifier value is not the ciphertext for this car |
| `00A17` | Already logged in elsewhere (session was taken over) |
| `1000P001` / `1000P004` | Missing parameter / method not allowed |
| `1018P061` | refreshToken expired or revoked |
| `1051P004` / `1051N001` | Incorrect parameter / internal error (`queryProcessResult` always returns this, not a public path) |
| `000002` | Passed but missing a parameter |
| `code:"0"` | Passed |

## Code structure

- `parser.py` fault-tolerant parsing and field normalization (shared by both channels, outputs a unified structure)
- `api_sms.py` / `api_gric.py` the two channels, exposing **the same set of methods** (`async_get_vehicle_list` /
  `get_vehicle_status` / `async_do_remote_control` / …)
- `coordinator.py` polling (`polling.py` adaptive backoff), command dispatch, optimistic updates
- `entity.py` + `VehicleEntityManager` (auto-creates entities after a vehicle appears)
- `__init__.py` selects the client via an `auth_method` factory ⇒ the coordinator and the platforms do not need to know which channel is used

## Tools (in the repo, not shipped with the integration)

`tools/zeekr_gric_verify.py` read-only probe (prints vehicle list/status) ·
`tools/zeekr_gric_control.py` real car control (run bare, it only lists the command table; has a safety gate) ·
`tools/zeekr_gric_token.py` token `show/refresh/ensure` + `form` (exports the two form values) ·
`tools/zeekr_device_pull.py` read-only pull from a rooted phone (does not trigger a re-login; `--gric` prints the latest pair of GRIC tokens,
`--write-tokens` writes the token file) ·
`tools/hexgrep.sh` memory hex search · `tools/generate_brand_images.py` generates brand icons.
