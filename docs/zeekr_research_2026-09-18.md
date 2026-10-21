# Zeekr HA Deep-Dive Research Log — night of 2026-09-18

> This document is the structured output of an all-night autonomous research session on 2026-09-18, meant to let us jump straight into testing the next day.
> Source tags: **[measured]** = raw return code obtained by this machine issuing a request to a real gateway;
> **[dex]** = plaintext string pool in APK v5.0.5 `classes.dex`; **[inferred]** = derived from evidence, not directly verified.

---

## 0. One-sentence conclusion

**`079001 [SDK]此接口未被授权，无法访问!` (this interface is not authorized, access denied) is not a parameter problem, nor an account/vehicle-permission problem, but an "interface-level SDK allowlist" — within the same service, control-type interfaces are denied while query-type ones are let through. Therefore the route pursued on 2026-09-16/17, poking at the `serviceParameters` parameter on the GW2 side, is worthless. The only effective direction is to obtain a "token with SDK identity."**

---

## 1. Core mechanism: the `[SDK]` gate

### 1.1 Observations ([measured], using the same GW3 token)

| Interface | Return | Classification |
| --- | --- | --- |
| `POST /ms-remote-control/v1.0/remoteControl/control` | `079001 [SDK]…` | gated |
| `GET /ms-vehicle-status/api/v2.0/vehicle/status/latest` | `079001 [SDK]…` | gated |
| `GET /ms-vehicle-status/api/v1.0/vehicle/status/{qrvs,vtm}` | `079001 [SDK]…` | gated |
| `GET /ms-vehicle-account/api/v1.0/vehicle-detail` | `079001 [SDK]…` | gated |
| `GET /ms-app-bff/api/1.0/permissions` | `079001 [SDK]…` | gated |
| `POST /ms-app-bff/.../mntmode/authCode/ownerAuthorization` | `079001 [SDK]…` | gated |
| `POST /ms-app-bff/.../certificate-center/getVehicleCertificate` | `079001 [SDK]…` | gated |
| `GET .../vehicle-shares/{services,check-share}` | `079001 [SDK]…` | gated |
| `POST /ms-vehicle-trail/.../journalLog/trip/listForPage` | `079001 [SDK]…` | gated |
| `GET .../journalLog/trackpoint/list?tripReportTime=20260917` | `079001 [SDK]…` | gated |
| `POST /ms-vehicle-defence/api/v1.0/fence/page` | `079001 [SDK]…` | gated |
| `POST .../digital-key-center/{get-bind-user-list,get-remaining-slot-quantity}` | `079001 [SDK]…` | gated |
| `GET /ms-charge-manage/api/v1.0/charge/getLatestSoc` | `079001 [SDK]…` | gated |
| `GET /ms-user-auth/api/v1.0/face/registered` | `079001 [SDK]…` | gated |
| —— | —— | —— |
| `GET /ms-remote-control/v1.0/remoteControl/queryProcessResult` | `000002 sessionId 缺失` (sessionId missing) | **let through** |
| `GET .../vehicle-shares/{owner/share-list,owner/share-histories,share/accept-list,share/accept-histories}` | `000000 ok` | **usable** |
| `POST /ms-tsp-user-setting/api/v1.0/userVeh/setting/query` | `000000 ok` | **usable** |
| `GET /ms-user-auth/api/v1.0/auth/cloud/temp/code` | `000000 ok` | **usable** |
| `GET /sentinel-monitoring-service/api/v2.0/pic/list` | `0 success` | **usable** |
| `GET /map-d2d-auto-service/api/v1/app/preciseMap/city/getAll` | `000000` | **usable** |
| `GET /scenario-mate-management-service/api/v1.0/mate/query/app/all/icon` | `000000` | **usable** |
| `POST /ms-tsp-dkbs-geely/.../digital-key-center/key-list` | `000002 signature/deviceid 不能为空` (signature/deviceid must not be empty) | let through |
| `POST /ms-user-auth/api/v1.0/auth/scanLogin` | `000002 登录数据不能为空` (login data must not be empty) | let through |

### 1.2 Where the gate decides ([measured], important)

- For the **same route**: `GET /ms-vehicle-trail/.../trip/listForPage` → `000010 method not allowed`;
  `POST` to the same path → `079001 [SDK]`.
- `GET .../trackpoint/list` (missing parameter) → `000002 The request parameter tripReportTime is missing`;
  switching to a valid format `20260917` → `079001 [SDK]`.

⇒ **The order is "route → parameter validation → SDK allowlist", and the gate is decided inside the microservice**, not at the gateway layer.
Side effect: **`079001` can be used as an oracle for "the parameters are correct"** (getting it means the parameters were accepted).

### 1.3 Explanations already ruled out

| Hypothesis | Conclusion |
| --- | --- |
| The way the `serviceParameters` parameter is written is wrong | Ruled out. The gate is unrelated to parameters (§1.2). |
| The `X-VIN` encoding/content is wrong | Ruled out. A prior comparison experiment confirmed enc/plaintext/content are all correct. |
| The account has no vehicle-control permission | **Open question.** Vehicle control works in the App with the same account, yet the interface still refuses it; see hypothesis B in §5. |
| A specific request header is needed | Not exhausted; the literal `[SDK]` reads more like "caller identity" than "request header". See hypothesis A in §5. |

---

## 2. Gateway and service map ([measured] + [dex])

### 2.1 Division of labor among the three gateways ([measured], **confirmed for the first time** this round)

- **GW1 `api-gw-toc.zeekrlife.com`**: only carries services with the `/zeekrlife-*` prefix.
  This round all 203 `ms-*`/`scenario-*` routes were fired at GW1 — **all 404**.
- **GW2 `api.zeekrline.com`**: only the old `/remote-control/` family (`no Route matched` for `ms-*`).
- **GW3 `snc-tsp-api.zeekrlife.com`**: **all `ms-*` / `scenario-*` / `sentinel-*` / `map-*` microservices**.

### 2.2 Microservice inventory ([dex], 54 prefixes / 660 routes, see `docs/zeekr_endpoints_full.md`)

The full routes of the control-related services are on file, including `ms-remote-control`(10), `ms-vehicle-status`(6),
`ms-charge-manage`(12), `ms-tsp-dkbs-geely`(52, digital key), `ms-vehicle-defence`(5, geofence),
`ms-vehicle-trail`(5, trip trajectory), `sentinel-monitoring-service`(6, sentinel),
`map-d2d-auto-service`(10, high-definition map/AVP), `scenario-personalization`(12, scenario orchestration),
`scenario-mate-management-service`(2), `ms-app-bff`(8).

### 2.3 Still unlocated hosts ([measured] all 404 on GW1/GW2/GW3)

`ms-vehicle-core`(5), `ms-iot-control`(2), `ms-tsp-bks-geely`(9), `ms-midground-user`(5),
`snc-remote-config`(2), `ms-lbs-service`(1), `ms-user-manager`(1), `ms-vehicle-guard`(1),
`ms-vehicle-extend`(1), `ms-app-online-center`, `ms-app-message-center`, `ms-ai-cloud`,
`ms-iot-status`, `map-service`.

Candidate hosts ([dex], host table in `docs/zeekr_endpoints_full.md`):
`gateway-pub.zeekrlife.com`, `gateway-int-test.zeekrlife.com`, `zeekr-m.zeekrlife.com`,
`galaxy-api-gw-toc.geely.com`, `gric-api.geely.com`, `galaxy-user-api.geely.com`, `galaxy-vc.geely.com`.
This round the first few were tried: `gateway-pub` returned an envelope with no `code`; `m./app.zeekrlife.com` returned a web page (not an API);
`zeekrgo-api` returned `-1`. ⇒ **Not found.**

### 2.4 Interfaces newly confirmed usable this round ([measured])

- `POST /ms-tsp-user-setting/api/v1.0/userVeh/setting/query`
  → `{"setting":[{"carName":"小粉","vin":"L6T77HCE9PF081833"}], ...}`
  **Value: gets the vehicle nickname on the App side, usable for entity naming.**
- `GET /ms-user-auth/api/v1.0/auth/cloud/temp/code` → `{"code":"<32-char hex>"}` (QR / temporary code).
- `GET /map-d2d-auto-service/api/v1/app/preciseMap/city/getAll` → full list of cities covered by the HD map.
- `GET /scenario-mate-management-service/api/v1.0/mate/query/app/all/icon` → scenario icon list (with CDN url + md5).
- `GET /sentinel-monitoring-service/api/v2.0/pic/list` → `0 success` (sentinel pictures, parameters still to be filled in).
- `POST /ms-vehicle-shares/share-status`, **the "unique identifier" parameter name = `traceId`**
  (tried 14 candidates; only it does not report "唯一标识不可为空" (unique identifier must not be empty)). Corresponds to `GlCarShareLoopReqBean(traceId=)`.

### 2.5 Parameter-name / format oracles ([measured])

| Interface | Known parameter | Notes |
| --- | --- | --- |
| `/zeekrlife-app-user/v1/user/toc/authCodeByServiceCode` | **`scene`** | `{"scene":"1"}` → `300035 不在业务范围!` (not within business scope); scene values 0–60 and keywords all give 300035 ([measured], no valid value found) |
| `/zeekrlife-app-user/v1/user/toc/validateAuthCode` | **`authCode`** + **`scene`** | once `scene` is accepted, all that remains is "验证码不为空" (verification code must not be empty); the verification-code field name is still TBD |
| `.../vehicle-shares/share-status` | **`traceId`** | |
| `.../journalLog/trackpoint/list` | **`tripReportTime`**, format **`yyyyMMdd`** | wrong format → `param check failed`; right format → `079001` (gated) |
| `/sentinel-monitoring-service/.../alarm/event/query` | **`alarmEndTime`** confirmed; the start-time parameter name is TBD | `alarmBeginTime` is not recognized (still reports "告警开始时间不能为空" (alarm start time must not be empty)) |
| `/ms-app-bff/api/1.0/permissions` | **`tspPlatform`**, **numeric enum** (`0/1/2` pass validation) | string → `param check failed` |
| `/ms-tsp-dkbs-geely/.../key-list` etc. | `signature` + `deviceid` (+`type`) | the digital-key family needs an App-side signature |

**Pitfall hit**: query values containing a space are rejected by `urllib` (`InvalidURL`), so `quote` them first.

---

## 3. Token status and the candidate "token swap" chains

### 3.1 Current token ([measured], decoded JWT)

```
iss    = https://snc-api-gw-inner.zeekrlife.com/auth-service/inner/v1/oauth/info
aud    = azp = user_center_client_phone      <- the user-center "phone-number login" client
scope  = ""                                   <- empty
sub    = openId = 2068684429979209728
userId = 403215671     sid = <uuid>     RS256 / 1047 chars / exp 7 days
source = POST /ms-user-auth/v1.0/auth/login (body carries the GW1 JWT)
```

### 3.2 Candidate chains ([dex])

```
scene code scene ──(zeekrlife-app-user/.../authCodeByServiceCode)──> authCode
        └──> com.geely.snc.login: AuthLoginReqBean(authCode=) ──> AuthLoginRspBean(accessToken=)
                implementation: IGLAuthLoginService / GLAuthLoginServiceImpl / GLTokenInterceptor
                companions: RefreshTokenReqBean/RspBean, HFScanLoginReqBean, ScanCodeLoginReqBean
                broadcast: com.geely.snc.action.login.elsewhere (i.e. "logged in elsewhere / session kicked")
another path: AccessCodeReq(clientId=) ──> /zeekrlife-mp-auth2/v1/auth/accessCode (verb unknown)
vehicle-control SDK (holder of the SDK token, [dex]): com.zeekr.snc.vehicle
        core/net/http/{VclHttpApi,VclHttpUrl,VclHttpUrl$Builder,VclHttpReq,VclHttpParam,VclHttpHeader}
        core/net/mqtt/{VclMqttMsg,VclMqttRsp,VclMqttClient}   <- there's also an MQTT channel
        iot/GLIotService, iot/utils/IIotTokenHelper, log/ITokenHelper, dlp/dmc/ZeekrDlcTokenHelper
```

**Unresolved**: the HTTP endpoint path for `AuthLoginReqBean` was not found (`VclHttpUrl` is a Java builder; the URL is not a plaintext constant).

---

## 4. Vehicle sharing (CarShare) status — a contradiction exists, to be cross-checked on the App side

[measured] (`16620192335`; the owner has stated they shared it):

```
GET vehicle-shares/owner/share-list       -> 000000 ok, total=0
GET vehicle-shares/share/accept-list      -> 000000 ok, total=0
GET vehicle-shares/owner/share-histories  -> 000000 ok, total=0
GET vehicle-shares/share/accept-histories -> 000000 ok, total=0
```

⇒ From the server's point of view this number is **neither a sharer nor a sharee**. Two explanations:

1. **[inferred] the share has expired / lapsed** (App copy includes "授权已过期" (authorization expired), "该分享已经失效" (this share is no longer valid), "超过最大分享次数" (maximum number of shares exceeded)),
   but the TSP-side binding is still present ⇒ vehicle control works while the share list is empty;
2. **[inferred] vehicle control comes from a different binding** (family account `account/affection`, enterprise vehicles `enterprise-vehicles`,
   family members), not vehicle-shares.

**Deciding criterion (first action tomorrow)**: a screenshot of the owner's App → "我分享出去的" (the ones I shared out) record's **status / validity period / permission items**.

---

## 5. Two competing hypotheses still to be verified

**Hypothesis A (token-identity theory, the one I currently lean toward)**
The `[SDK]` allowlist compares against the token's client identity (`azp`/`aud`).
The current token is `user_center_client_phone` with `scope=""`, inherently not on the allowlist.
⇒ We need to go through the SDK login in §3.2 to swap in a token whose `azp` is the SDK client.
Supporting evidence: within the same service, query interfaces are let through while control interfaces are refused, which has nothing to do with "account permission" (permission is at the account level and would not be split per interface).

**Hypothesis B (account-permission theory)**
`[SDK]` is actually just another way of stating "whether this account has vehicle-control permission for this car",
and the current account's permission has lapsed due to **share expiry**, so all control-type interfaces are refused.
⇒ After the owner re-shares (and accepts in the App) it should unlock.

**How to tell them apart (tomorrow, in one shot)**: among the 22 gated items in `tools/zeekr_gate_check.py`,
**if any single one changes from `079001` to a different code**, it's hypothesis B; **if all remain `079001`** it's hypothesis A.
This test is **entirely read-only** and will not actuate the car.

---

## 6. Tomorrow's (2026-09-19) test plan

### Step 0 — environment self-check (1 minute, no prerequisite action needed)

```bash
PY=C:/Users/rexze/.workbuddy/binaries/python/envs/default/Scripts/python.exe
CREDS=C:/Users/rexze/AppData/Local/Temp/zeekr_bak/tokens.json
cd /d/zeekr_ha
$PY tools/zeekr_gate_check.py --creds "$CREDS"          # just view the decision table, write no files
```

### Step 1 — owner re-shares (requires user/owner action)

- Owner App → vehicle sharing → share to `16620192335`, **check all permissions (including remote control)**;
- Record and screenshot: status / validity period / permission items;
- Log in as `16620192335` in the App and **accept** the share (the share flow is `create → traceId → poll`,
  see §2.4 where `share-status` uses `traceId`).

### Step 2 — is the gate lifted (key decision, read-only)

```bash
$PY tools/zeekr_gate_check.py --creds "$CREDS" \
    --compare docs/zeekr_gate_baseline.json
```

Reading (the script prints automatically):

| Result | Meaning | Next step |
| --- | --- | --- |
| Some gated item becomes "let through / usable" | Hypothesis B holds, permission was unlocked | Go straight to step 3 |
| All 22 items are still `079001` | Hypothesis A holds | Switch to the token-swap chain in §3.2 |
| Baseline items (prefix `基线:` / "baseline:") are unavailable | Token/session is broken | Re-login by SMS, then rerun |

The baseline is ready: `docs/zeekr_gate_baseline.json` (28 items: 22 gated / 5 usable / 1 let through).

### Step 3 — if the gate is lifted: verify vehicle-status reading (read-only)

```bash
$PY tools/zeekr_route_sweep.py --creds "$CREDS" \
    --routes C:/Users/rexze/AppData/Local/Temp/zeekr_ctrl_routes.txt \
    --out docs/zeekr_route_probe_results_after.md --gateways gw3
```

Compare with tonight's results `docs/zeekr_route_probe_results.md` to see all the newly unlocked interfaces in one pass.

### Step 4 — if status is readable: closed-loop verification of a command (**will actuate the car, requires in-person confirmation**)

- Start with the most harmless command (e.g. flash lights / honk, if wired up), then verify the `queryProcessResult(sessionId)` polling closed loop;
- Note the integration currently "assumes success as soon as the command is sent" and lacks the closed loop ([prior conclusion]).

### Environment and dependency readiness (confirmed tonight)

| Item | Status |
| --- | --- |
| Python venv (pycryptodome 3.23.0, androguard 4.1.4) | ready |
| Probe tool (reuses the integration's signing/encryption code) | `tools/zeekr_probe.py` ready |
| Credentials file `tokens.json` | ready (4459 B) |
| dex string-pool cache (32 MB, every search in milliseconds) | ready `%TEMP%\zeekr_strings.txt` |
| Gate baseline snapshot | ready `docs/zeekr_gate_baseline.json` |
| Full route inventory | ready `docs/zeekr_endpoints_full.md` |
| Control-plane route measured table | ready `docs/zeekr_route_probe_results.md` |
| APK original | ready (597 MB) |
| SMS verification code | **needs real-time user cooperation** (very short validity) |

> Note: while writing this log, one network-probe command's authorization prompt timed out (no one to confirm), and its output was withheld;
> the product of that command, `docs/zeekr_gate_baseline.json`, was verified complete and usable (28 items, internally consistent).
> Subsequent network-type commands may need re-authorization. **Suggestion: run step 0 first tomorrow to confirm the authorization chain is healthy.**

---

## 7. New tools added this round (all reusable)

| Tool | Purpose |
| --- | --- |
| `scratch/dex_strings.py` | Exports the hardened dex's string pool to text (handles the uleb128 length prefix); 40 seconds once, then every search is in milliseconds |
| `scratch/s.py` | Does regex search + neighbor context over that text (exploiting the ordering of the string pool) |
| `scratch/route_inventory.py` | Generates the full service-route / host / ARouter page inventory |
| `tools/zeekr_route_sweep.py` | Full route × multi-gateway scan (**sends GET only**), produces a markdown comparison table |
| `tools/zeekr_gate_check.py` | One-shot gate detection + comparison with baseline; signals via exit code 1 when the gate is lifted |

---

## 8. Source list

- **[measured]** Real requests from this machine's `tools/zeekr_probe.py` / `zeekr_route_sweep.py` / `zeekr_gate_check.py`
  to `snc-tsp-api.zeekrlife.com`, `api-gw-toc.zeekrlife.com`, `api.zeekrline.com`.
- **[dex]** APK `com.zeekrlife.mobile.apk` v5.0.5 `classes.dex` string pool
  (the id table was removed by the `libconch` hardening; only the plaintext string data region is present; structured parsing is infeasible).
- **[prior]** `.workbuddy/memory/MEMORY.md`, `.workbuddy/memory/2026-09-1[678].md`,
  `docs/zeekr_app_endpoints.md`.

## 9. Summary of uncertainties (each independently verifiable)

1. Whether `16620192335` really once received a vehicle share, and whether it has expired — needs an App-side screenshot (**highest priority**).
2. What the `[SDK]` allowlist actually compares against (client identity vs account permission) — step 2 decides in one go.
3. The HTTP endpoint path for `AuthLoginReqBean` — not found, needs continued reverse engineering (`VclHttpUrl` is a builder, not plaintext).
4. The valid range of `scene` for `authCodeByServiceCode` — 0–60 and keywords were all refused (`300035`),
   possibly the interface is entirely unavailable to this client.
5. The "verification code" field name for `validateAuthCode` — `authCode`/`scene` are known, the third field is TBD.
6. The "start time" parameter name for the sentinel-alarm query — `alarmEndTime` is known, the start time is TBD.
7. The real hosts of 14 services (`ms-vehicle-core`, `ms-iot-control`, `ms-tsp-bks-geely`, etc.) — not found.
8. The algorithm and origin of the `signature` / `deviceid` required by the digital-key family — suspected to be an SDK-internal signature.
9. Whether `/ms-remote-control/api/v1.0/...` (with `api`) and the path the integration currently uses (without `api`) are equivalent —
   the two return the same code in testing, **inconclusive**; confirm before wiring up.

---

# 2026-09-18 morning: App-side evidence in hand; two key facts overturned/established

## Two App screenshots the user provided (decisive evidence)

### Screenshot B: `收到的车辆分享` (vehicle shares received)
```
车辆 (vehicle)              小粉 / 1833            <- tail 1833 = L6T77HCE9PF081833, matches this project's VIN
分享来自账号 (shared from account)   酒酿澜澜圆子 / 13874333029   <- owner account
分享状态 (share status)      已接受 (accepted)
分享时间 (share time)        2026/09/16 01:35
接受时间 (accept time)       2026/09/16 01:35
底部按钮 (bottom button)     结束用车 (end using the vehicle)
```

**⇒ The vehicle share really exists and has been accepted** (created 2026-09-16). This **contradicts** the interface side where
`vehicle-shares/{share/accept-list, accept-histories}` return `total=0`;
see the reasoning in the next section.

### Screenshot A: `爱车提醒` (my-car reminders / alarm list)
```
[小粉]执行失败，请重试。请确认车端软件和手机APP版本为最新，若问题仍存在，请联系售后服务
([Xiaofen] execution failed, please retry. Please make sure the vehicle-side software and phone App version are the latest; if the problem persists, contact after-sales service)
2026-09-17 02:10 / 02:08 / 02:08 / 01:04 / 01:03
```

**⇒ The command really was delivered to the vehicle, and the vehicle attempted to execute and failed.** The time window (09-17 01:03–02:10)
matches the period recorded in the project for "testing 5 parameter variants against GW2 `PUT /remote-control/vehicle/telematics/{VIN}`".
Fully consistent with the prior conclusion "GW2 returns `1000` but the car does not move ⇒ the root cause is on the vehicle-side execution".
The prompt "请确认车端软件和手机APP版本为最新" (make sure the vehicle-side software and phone App version are the latest) hints at a **protocol version mismatch**.

## GW1 JWT decode (local credentials file, no network needed)

```
iss=prod   aud=app   exp=1821127660
sub = { accountInfoDTO: { accountId 2068684429979209728, mobile 16620192335,
                          nickname 极氪用户_M1ZT6LbH (Zeekr user_M1ZT6LbH), city 广州市 (Guangzhou), 海珠区 (Haizhu district),
                          buSite 1, channel 3, tenantId 0, registerBusinessType 8352008 },
        accountLoginInfoDTO: {
          agoLoginDeviceName  "iPhone13",  agoLoginAt  1789585388891,
          lastLoginDeviceName "Android SDK built for arm64",
          lastLoginDeviceId   299c9bc6ebe34c8994def00068988006,
          logoutOtherDevices  true            <- single-device policy, hence the session kicking
        } }
client_id = APPLE0000APP00IPHONE266M14110026      <- 32 chars, iOS client identifier
user_id   = 403215671
```

**⇒ `logoutOtherDevices: true` is confirmed by the server**, which explains all the 079021 "session kicked / logged in elsewhere" phenomena.
**⇒ My `client_id` is iOS's**; `iPhone13` appeared in the account login history, suggesting the user's phone
is very likely logging in with `16620192335` (needs user confirmation).

## dex structure corrections (important)

- **`ControlReqBean(controlType=` / `ControlReqBean15(controlType=` belong to the digital-key Bluetooth protocol**
  (`com/geely/snc/digitalkey/base/dk/business/protocol/dk{15,20}/bean/`),
  **not the HTTP control request body**. Treating them as the HTTP request Bean earlier was a misjudgment.
- The HTTP control family is actually: `RemoteControlReq` / **`RemoteControlSetting(serviceParameters=`** /
  `RemoteControlParams(qrInfo=` / `EnergyBaseRequest(serviceId=` /
  `EnergyBaseRequestSetting(serviceParameters=` / **`ControlResult(sessionId=`,
  `ControlResult(iotRemoteControlType=`** / `OperationScheduling(duration=`.
- The dex **does not contain** an Android-form client_id (of the form `XXXX0000APP...`); the iOS one is not in the dex either
  ⇒ the client_id is issued by the server (`/zeekrlife-app-user/v1/user/pub/secretConfig` etc.).

## Chain of reasoning (the most likely complete explanation at present)

1. The account `16620192335` has an **accepted vehicle share** (including vehicle-control permission) for the vehicle `小粉` (Xiaofen);
2. In the App, this account can normally enter the vehicle page and shows "结束用车" (end using the vehicle), which means **the account permission is present**;
3. But the GW3 token this integration gets via `/ms-user-auth/v1.0/auth/login`
   (`azp=user_center_client_phone`, `scope=""`) is refused by 21 control-type interfaces with
   `079001 [SDK]此接口未被授权` (this interface is not authorized);
4. ⇒ **The gate decides based on "client identity" (the token's azp/aud/scope), independent of account/vehicle permission.**
   Hypothesis A is essentially confirmed; hypothesis B is directly weakened by screenshot B.

## Still needs user confirmation (a single either/or settles it)

- **Does tapping vehicle control (flash lights / lock) in the App actually succeed?**
  - Succeeds ⇒ same account, same phone number, App can but the API cannot ⇒ **purely a client-identity problem**,
    we must capture traffic to get the token the App uses (`docs/zeekr_capture_playbook.md`).
  - Also fails (same "execution failed") ⇒ the root cause is **vehicle-side execution / protocol version**,
    unrelated to the token; the direction shifts to "find the command format the vehicle accepts", and traffic capture is still the first step.
- Which number was used to log in when viewing the screenshots? (`16620192335` or the user's usual number?)

---

# 2026-09-18 morning (continued): key inference — our GW3 login flow is not the App's flow

## Inference and evidence

List **all 13 routes** of `ms-user-auth` from the dex:

```
/ms-user-auth/api/v1.0/account/affection[/unbind]
/ms-user-auth/api/v1.0/auth/cloud/temp/code
/ms-user-auth/api/v1.0/auth/scanLogin
/ms-user-auth/api/v1.0/csp/{relation,resetPassword,user,verification/mobilePhone[/cspmobile]}
/ms-user-auth/api/v1.0/face/{delete,dhu-wakeup,pictureUpload,registered}
```

**There is no `/auth/login` among them.** Yet what this integration uses to get the GW3 token is precisely
`POST /ms-user-auth/v1.0/auth/login` (body carries the GW1 JWT, `identityType: 5`).

⇒ **That endpoint "works" but is not the path the App uses.** Its token
(`azp=user_center_client_phone`, `scope=""`) is inherently not on the `[SDK]` allowlist.

In the same family the name that most resembles "App token retrieval" is:

```
/ms-midground-user/api/v1.0/user/auth/{get/token, refresh/token, hfScanLogin, cancel/login, logout}
```

This round a **multi-path × multi-gateway** matrix was tested against it (`/api/v1.0/`, `/v1.0/`, with `ms-` prefix removed;
GW1 / GW2 / GW3 / `gateway-pub` / `gateway-int-test`) — **all 404 / no route**.
⇒ The host is still unlocated (suspected to be an H5 / mid-platform host; no match in the dex host table for now).

## Therefore the conclusion

**Traffic capture is upgraded from a "speedup" to the "only viable path"**: only by seeing the App's one real control request
can we know (a) which host/path it hits, (b) which `Authorization` it carries, (c) which `X-*` headers it carries, (d) what the request body looks like.
Static means (string-pool archaeology + endpoint carpet-bombing) are essentially exhausted.

## Preparations completed during the wait

- `tools/zeekr_capture_start.py`: auto-detects this machine's LAN IP, starts mitmdump, and prints the phone-side steps (including the IP);
  supports `--zeekr-only` to proxy only Zeekr domains.
- `docs/zeekr_capture_playbook.md` gains a new **§0.5 Plan 0**: a phone-native capture App (Reqable etc.) in VPN mode,
  **no computer needed, no same network needed**, doable even away from home; just screenshot the request headers + body + path for me.
- Explicit prohibition: **do not log the account into an emulator** (`logoutOtherDevices: true` would kick the user's phone).

---

# 2026-09-18 evening: capture succeeded — found the App's real call chain (major breakthrough)

The user's phone capture succeeded (`capture/zeekr-20260918-1925.flow`, 54 requests, 1 MB),
the operation being "turn on the AC". **The entire chain is now completely clear.**

## 1. The gateway the App hits is not the one we use

```
gric-zhf-api.geely.com      <- vehicle control / vehicle status / permissions / vehicle detail / capability set (main)
gric-api.geely.com          <- vehicle core (favorite vehicles, etc.)
gric-aic-api.geely.com      <- /think/app/v3/car/function/push
```

**Our integration hits `snc-tsp-api.zeekrlife.com` (GW3)** — the paths are almost identical, but the gateway differs,
so that side uniformly returns `079001 [SDK]此接口未被授权` (this interface is not authorized).

## 2. The App's vehicle-control request (byte by byte)

```
POST https://gric-zhf-api.geely.com/ms-remote-control/api/v1.0/remoteControl/control

x-tenant-id: ZEEKR
x-platform: Android
x-sales-platform: ZEEKR
x-device-brand: OPPO
x-device-model: PLJ110
x-device-os-version: Android 16 (API 36)
x-app-version: v1.0.0
x-app-id: GEELYCNCH001M0001              <- note: not ZEEKRCNCH001M0001
accept: application/json; charset=UTF-8
accept-language: zh_CN
authorization: <JWT, azp=auth_client_zeekr_phone>
x-api-signature-version: 2.1
x-api-signature-nonce: 8f2e46d7-9f75-4882-baeb-ea7a2f98a34b
x-timestamp: 1789731095309
x-device-id: 291d2cec-c5c0-43b9-b7f8-8fba770f04ce
x-vehicle-identifier: l1oQt6DQLAWGk8VKjbFBdxXaNr6FhF1h6obO8pgzLw4=     (base64, 32B = AES-encrypted VIN)
x-vehicle-brand: ZEEKR
x-vehicle-series: QlgxRQ==               (base64 "BX1E" = vehicle series code)
x-tsp-platform: 4                        <- we only ever tried 0/1/2
x-signature: 05yFNewzZJvAl1n8eYtVwUdDGNTHrETRozJ8OWpQf2Y=
content-type: application/json; charset=UTF-8
user-agent: okhttp/4.12.0

request body (158 B):
{"command":"","serviceId":"ZAF",
 "setting":{"serviceParameters":[
   {"key":"AC","value":true},
   {"key":"AC.temp","value":"18.0"},
   {"key":"AC.duration","value":20}]}}

response 200:
{"code":"0","data":{"sessionId":"PF081833000000013109515333902410"},
 "debug":{"bizName":"ms-mobile-adapter-service",...},"msg":"操作成功"}   (operation successful)
```

Key points:
- The request body has the **empty field `command: ""`**;
- `serviceParameters` is a **`{key,value}` list**, where `value`'s type varies with the key (bool / string / number);
- The response returns a **`sessionId`** (of the form `PF0818330000000131...`), which is then polled to the closed loop with
  `queryProcessResult` — consistent with our earlier inference.

## 3. The App's token differs from ours

```
aud = azp = auth_client_zeekr_phone          <- ours is user_center_client_phone
iss = https://gric-mid-inner.geely.com/ms-auth-service/inner/v1.0/oauth/info
                                                <- ours is snc-api-gw-inner.../auth-service/...
sub = openId = 2068684429979209728            <- the same account (same as ours)
userId = 403215671   brand = ZEEKR   env = PROD
deviceId = 291d2cec-c5c0-43b9-b7f8-8fba770f04ce
```

⇒ **Same account, two tokens of different client identity.** Our GW3 login
(`/ms-user-auth/v1.0/auth/login`, a route that simply does not exist in the dex) yields a token that is inherently not on the GRIC/SNC allowlist.

## 4. We are only "two things" away from success

**[measured] Our existing signing implementation (`_sign_gw3` + `_SNC_SECRET`) is valid on GRIC!**

| Combination | Result | Meaning |
| --- | --- | --- |
| `x-app-id: ZEEKRCNCH001M0001` + our signature | `00A02 header property 'X-VEHICLE-SERIES' is required` → after adding the header becomes `00A22 The app information does not exist.` | **signature passes**, it's just that this app-id is not registered on GRIC |
| `x-app-id: GEELYCNCH001M0001` + our signature | `00A06 Signature verification failed.` | this app-id exists, but **the key differs from ours** |

⇒ The two missing things: **① the signing key for `GEELYCNCH001M0001`; ② the source of the `auth_client_zeekr_phone` token.**
(We can generate `x-vehicle-identifier` too: `_encrypt_vin` likewise outputs 44-char base64 / 32 bytes.)

## 5. The key is not in the APK we hold

- The dex only has **`ZEEKRCNCH001M0000` / `ZEEKRCNCH001M0001` / `ZEEKERCNCH001M0001`**,
  **no `GEELYCNCH001M0001`**;
- `_SNC_SECRET` is also not simply derived from the app-id (all md5/sha1/sha256 spellings exhausted, none match);
- `secretConfig` only returns an RSA public key, no signing key;
- In the capture `x-app-version: v1.0.0`, whereas the APK we reversed is **v5.0.5**.

⇒ **The App on the user's phone is very likely not the version we hold**
(`x-app-version: v1.0.0` may also be the version number of the GRIC SDK itself, to be confirmed).

## Next steps (needs the user)

1. **The Zeekr App's version number** (App → Mine → Settings → About).
2. **Ideally export that APK to me** (on OPPO use "App management → Share/extract install package", or any APK extractor).
   I'll search the new APK's string pool for `GEELYCNCH001M0001`; its neighbors very likely contain that 32-char key;
   at the same time I'll find the login/token-swap endpoint corresponding to `auth_client_zeekr_phone`.
3. Alternative: **do another capture that includes "log out → log back in"**,
   which would let us see the full token-acquisition chain (in the current capture the token is cached; the acquisition process did not appear).

---

# 2026-09-18 evening (continued): the only gap is locked to "the shared key for `GEELYCNCH001M0001`"

## Measured matrix (GRIC gateway, `gric-zhf-api.geely.com/ms-app-bff/api/1.0/permissions?tspPlatform=4`)

| Condition | Return | Reading |
| --- | --- | --- |
| No Authorization | `00A02 header 'AUTHORIZATION' is required` | header validation is **before** signature validation |
| Any made-up app-id + our signature | `00A22 The app information does not exist.` | **signature is not the deciding factor** (the gateway doesn't know this app), it's just that the app is unregistered |
| `GEELYCNCH001M0001` + our signature | `00A06 Signature authentication failed.` | this app is **registered** ⇒ the gateway validates with **its own key**, ours doesn't match |
| Same, signature version changed to 1.0 | `00A02 Unsupported signature version` | only 2.0 / 2.1 are supported |

⇒ The conclusion is rock-solid: **the signing algorithm is already implemented correctly** (proven by the ZEEKR app-id passing signature validation on GRIC earlier),
**the only thing missing is the one shared key for `GEELYCNCH001M0001`**.

## The key is not in the client's static data (exhausted)

- **Whole-package byte-by-byte scan** (597 MB, all zip entries): `GEELYCNCH001M0001` appears **0 times**;
  `CNCH` has only three variants: `ZEEKRCNCH001M0000` / `ZEEKRCNCH001M0001` / `ZEEKERCNCH001M0001`.
- **All 97 .so files scanned**: only `libfq.so` / `libnative-lib.so` contain `ZEEKR` (face SDK `ZEEKR_FaceID*`), no app-id and no key.
- `libHttpSecretKey.so` only exposes
  `Java_com_haohan_module_http_encrypt_HttpSecretKey_{get,set}SecretKey` ⇒ **the key is set in at runtime from the Java side**.
- The APK the user provided (`C:/Users/rexze/Documents/OPPO 互联/极氪.apk`) is **identical** to the `Downloads` APK outside the repo
  (both 597 MB, same dex, same so manifest, likewise only ZEEKR variants) ⇒ the version is indeed v5.0.5, not a version-difference issue.
- `_SNC_SECRET` is not app-id-derived (all md5/sha1/sha256 spellings exhausted).
- The `x-app-version: v1.0.0` in the capture should be the **GRIC SDK's own version number**, not the App version.

## The second capture (log out) did not get anything

- The user reported "退出登录网络报错" (logout gave a network error); in the capture file `capture/zeekr-20260918-1942.flow` there are
  **no logout / login / token requests at all**, only heartbeats and vehicle-status polling (all 200).
  ⇒ The error occurred inside the App; the request was not sent out (suspected to use HTTP/3, which the proxy cannot intercept).
- But even if the login flow is captured, **the shared key will never appear in the traffic** (it is a local constant / runtime-issued; only the signature result travels with the request).
  ⇒ Capturing the login is of limited help for "getting the key", only valuable for "the token-acquisition chain".

## Two viable routes (needs user decision)

**Route A (low cost, uncertain): capture a cold start after clearing App data**
`Settings → App management → Zeekr → clear data`, then capture and log back in. If the key is **server-issued**,
the issuing request will appear this time; if it's a local constant, nothing will be visible.
⚠️ Risk: this clears the App's local state, and **if there's a Bluetooth digital key on the phone it may need to be recreated**; it also logs you out.

**Route B (high cost, high certainty): frida dynamic extraction**
In an Android emulator (rootable) install the App + frida-server and hook
`HttpSecretKey.getSecretKey` or the signing function to dump the key directly.
No login is needed to get a client constant; if the key is issued at login, then login is needed (which kicks the phone and requires re-login afterward).
Output: **one key + a fully reproducible signature.**

**Infeasible**: replaying the captured requests — `x-timestamp` has a validity window, only valid for that one time, cannot support long-term HA use.

## The part already known and directly deployable (unrelated to the key)

The App's full call chain is mastered byte-by-byte (gateway, path, all request headers, the way `x-vehicle-identifier` is generated which we already have,
request body structure, the response `sessionId` and the `queryProcessResult` closed loop). **Once we have the key, wiring it up is pure engineering.**

---

# 2026-09-18 evening (three): important correction + the road narrows

## Correction: `00A22` is not "signature passed" but "app unregistered, signature not validated"

Using "the ZEEKR app-id (whose key is known)" as a control, varying one by one the **set of headers that participate in signing** (6 variants) × signature version (2.0/2.1):

```
base / base+all-extra / base+tenant+tsp / base+vehicle / base+tenant+tsp+vehicle / all_minus_meta
× ver 2.0 / 2.1   →  all 12 combinations return 00A22
```

**12 mutually exclusive canonical strings cannot all be accepted at once** ⇒ the gateway returns `00A22` **before** validating the signature.
⇒ The earlier judgment that "our signature is valid on GRIC" is **void**. The true semantics:

| Return | Meaning |
| --- | --- |
| `00A02` | missing header / unsupported signature version (pre-check) |
| `00A22` | **app unregistered** → returned directly, **signature not validated** |
| `00A06` | app registered → **signature validation failed** |

## The key is not in the string pool (offline brute force done)

`scratch/key_hunt.py`: targeting the App's `x-signature` from the capture, using
`_sign_gw3`'s canonical-string construction + HMAC-SHA256, verifying one by one over the dex string pool **848,708 candidates × 3 case variants**
(including the logic of double-checking with the second request) → **no hit**.

⇒ Combined with the fact that "the app-id `GEELYCNCH001M0001` itself has 0 hits in the whole package",
**the App's string constants are stored encrypted (`libEncryptorP.so`)**, and the signing key is very likely encrypted too
⇒ **unobtainable by pure static analysis**.

## The road narrows (two important conclusions)

1. **Emulator + frida is basically infeasible**: the APK is **arm64-v8a single-architecture** (all 93 native libs are arm64,
   including video/face SDKs), an x86_64 emulator cannot run it natively; domestic Apps also have emulator detection.
2. **Login with a proxy will fail**: the user measured "with a proxy the network errors out, can't log in".
   ⇒ The login chain differs from the vehicle-control chain, suspected to be one of **certificate pinning / proxy detection / HTTP/2 negotiation**.
   `--no-http2` is worth a try (HTTP/2 negotiation failure is a common failure point in proxy scenarios).

## Current status and available routes

- **Confirmed usable**: the App's full call chain on the GRIC gateway (gateway/path/all request headers/request body/signing algorithm framework).
- **Gap**: the shared key for `GEELYCNCH001M0001` (an encrypted constant).
- Routes:
  - **① Try logging in with a proxy once more** (`--no-http2`) → if it works, we may see login/token/possibly the key issuance;
  - **② Capture the App on the phone side (Reqable etc., VPN mode)** → switch to a different capture implementation to dodge mitmproxy being detected / negotiation failure;
  - **③ If neither works**: the vehicle-control route is **unobtainable** under current conditions (unless a rooted device or ARM environment is available for dynamic extraction).
    At that point effort should turn back to delivering the "already-working read-only capabilities".

---

# 2026-09-18 evening: open-source ecosystem breakthrough — static extraction of 6 keys + found the overseas version's full auth chain

## 1. Decisive discovery: the community has already solved this problem

After searching public resources I found three directly relevant projects (**meaning our direction shifts from "reverse-engineering guesswork" to "copying a verified implementation"**):

| Project | Value |
| --- | --- |
| **`wysie/zeekr_key_extractor`** | A mature tool that **statically extracts 6 keys** from the Zeekr APK; **supports `--region CN`**; the new-version keys are in the **`libenv.so` plaintext table** (purely static, no root/emulator/frida needed) |
| **`sunshijiang/zeekr_homeassistant_sun`** | An HA integration that **already supports mainland-China SMS login**; uses `hmac_access_key`+`hmac_secret_key`, `X-API-SIGNATURE-VERSION: 2.1`, host `api-gw-toc.zeekrlife.com` |
| **`nikagl/zeekr_ev_api`** | An overseas-version API library (PyPI `zeekr-ev-api`); contains **`zeekr_app_sig.py` (the authoritative X-SIGNATURE implementation)** and **`zeekr_hmac.py` (the X-HMAC implementation)** |

## 2. The 6 keys have been extracted successfully (no root, no emulator)

Run on **the China-version APK we hold** (`--region CN`):

```bash
python zeekr_extract_secrets.py "C:/Users/rexze/Documents/OPPO 互联/极氪.apk" --region CN
# => All 6 secrets extracted successfully!
```

The result lands on disk at `C:/Users/rexze/Documents/OPPO 互联/zeekr_secrets.json`:

```
hmac_access_key    = 7dbae691d53f4f3c9fab905368370d80
hmac_secret_key    = hnpigl1f13fcb6a3ac834895b9e403c08cd895ce
password_public_key= MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDENksAVqDoz5SMCZq0bsZwE+I3NjrANyTTwUVSf1+...
prod_secret        = 03d1cd020062469e90ed63416c5c0fda   (plus ~120 other candidates)
vin_key            = 2014052600006128
vin_iv             = aebd1811194e82d9
```

Compared with the integration's existing constants (**all different**):

| Purpose | Integration's current | Extracted value |
| --- | --- | --- |
| X-SIGNATURE key | `_SNC_SECRET = 890efe3207af95348b95f66b2ee7da04` | `prod_secret = 03d1cd020062469e90ed63416c5c0fda` |
| VIN encryption | `_AES_KEY=a01a6db985a2f5d4` / `_AES_IV=ed446b8b8845013d` | `vin_key=2014052600006128` / `vin_iv=aebd1811194e82d9` |

Dependencies: `capstone 5.0.7` + `pyelftools` (already installed into the default venv).

## 3. Found the overseas version's full auth chain (demonstrated by `zeekr_ev_api`)

```
1) email + password login     → user-center token
2) GET  user/tspCode                     → tspCode
3) POST ms-user-auth/v1.0/auth/login     → bearer accessToken
        {identifier: tspCode, identityType: 10, loginDeviceId, ...}
4) use the bearer token to call ms-vehicle-status / ms-remote-control / ms-charge-manage ...
```

Key point: **the China-region integration uses `identityType: 5`, which is the "user-center phone-number" token, whereas what can call `ms-*` is the `identityType: 10` bearer token** (swapped using tspCode).
And the overseas version's business-call headers are `X-APP-ID: ZEEKRCNCH001M0001` + `X-PROJECT-ID: ZEEKR_SEA` + `X-API-SIGNATURE-VERSION: 2.0`;
**login uses a separate set of `DEFAULT_HEADERS`**: `app-code: 32816dbd-...`, `client-id: 1JwLroFkFFIpgFGdTRrm4_nzkkwDkfHj7RxJQb7J8tc`, `appsecret: zeekr_tis`, `appid: TSP`, `msgappid: 11002`.

## 4. This round's measurements (all read-only, no vehicle-control write operations performed)

| Test | Result | Conclusion |
| --- | --- | --- |
| **`GET /zeekrlife-app-user/v1/user/tspCode` (GW1)** | **`000009 检测到您的账号在多个设备登录，请重新登录`** (detected that your account is logged in on multiple devices, please log in again) | **The route really exists!** (The earlier belief that "the China region has no such route" was a **wrong conclusion**; we were trying a different prefix then.) 000009 means the session was kicked |
| `user/tspCode` and 5 other candidates on `snc-tsp-api` | `00A01 404` | not on GW3 |
| `/ms-user-auth/v1.0/user/tspCode` (GW3) | `079026 请求不在可访问地址范围` (request is not within the accessible address range) | route exists, region-restricted |
| `identityType=10` + identifier∈{empty, JWT, openId, phone number, GW3 token} | **all `015013 登录权限校验不正确`** (login permission check incorrect) | 10 needs a **real tspCode**, not just anything (the earlier conclusion "only identityType 5 works" should be corrected to "**5 works because its parameters are complete, 10 lacks tspCode**") |
| Control `identityType=5` | `000000 ok` + token obtained | baseline normal |
| HMAC headers (`X-HMAC-*`) + CN keys hitting GRIC / GW1 | GRIC `404`; `api-gw-toc` **`401`** | **the HMAC system is not the signing method of these two gateways** |
| Use `vin_key/vin_iv` and `_AES_KEY/_AES_IV` to **decrypt** the App's `x-vehicle-identifier` | both sets give garbage (CBC/ECB/swapped all tried) | `x-vehicle-identifier` is **not a simple AES(VIN)** (may contain salt / a composite string, or a third set of keys) |
| `x-signature` 2.1 **all-day brute force** | `ALLOWED_HEADERS` / `+CN extensions` / `x_only` / `CN_only` × 12 variants × **786,079** candidates ≈ all misses | GRIC's signing key is **not in the APK plaintext string pool** (`libEncryptorP.so` encrypted wrapper), unobtainable statically |
| DNS: China-region gateway candidates | `cn-snc-tsp-api-gw.*` / `cn-snc-tsp-api.*` **both do not resolve**; `snc-tsp-api.zeekrlife.com` = 121.43.28.50 normal | **the China region is just the prefix-less `snc-tsp-api.zeekrlife.com`** |

## 5. Next step (requires a valid session, hence needs user cooperation)

Added the one-shot script `tools/zeekr_bearer_chain.py`:

```bash
# 1) send verification code (user receives SMS)
python tools/zeekr_bearer_chain.py --send-sms --phone 16620192335
# 2) run the full chain with the code
python tools/zeekr_bearer_chain.py --phone 16620192335 --code <6-digit code>
```

The script executes in order: GW1 phone login → extract JWT → `tspCode` → `identityType:10` swap for bearer → use bearer to probe 5 read-only interfaces,
and prints each step's raw return. **Criterion: any interface changing from `079001` to `000000`/a parameter-level error ⇒ the chain holds.**

⚠️ **Constraint**: an account can be online on only one device. **Do not open the Zeekr App on the phone** while running the script (they kick each other), or the chain will break midway.

## 6. Items still to verify (updated)

1. **Whether obtaining `tspCode` needs only the GW1 JWT**: needs one valid login to verify (the current 000009 is due to the session being kicked).
2. Whether `identityType: 10` in the China region needs **extra client headers** (`app-code`/`client-id`/`appsecret`) — the overseas version carries them, we never have.
3. The China-region value of `X-PROJECT-ID` (`ZEEKR` / `ZEEKR_CN` / `ZEEKR_SEA`) is unknown.
4. The real construction of `x-vehicle-identifier` (not a simple AES(VIN)).
5. GRIC's `x-signature` key (unobtainable statically; if the GW3+bearer chain holds it's **no longer needed**).
6. If the GW3+bearer chain still doesn't work, the fallback is `sunshijiang`'s HMAC route (first confirm whether its endpoints are really usable — that project's CN endpoint paths are **guessed**, hit by a 3×3 brute-force).

---

# 2026-09-18 night (user cooperated with a live run): three disproofs + full decryption of libenv.so

## 1. Assets successfully obtained

- **GW1 phone verification-code login succeeded** (the verification code is **4 digits**, not 6).
- **The JWT is cached** to `C:/Users/rexze/AppData/Local/Temp/zeekr_jwt.txt` (1842 chars, with the `Bearer …` prefix already included),
  written and reused by `tools/zeekr_bearer_chain.py` ⇒ **subsequent probing no longer needs the user to provide a verification code.**

## 2. Three disproofs (all important, to avoid backtracking)

### 1) The `tspCode` China-region route **does not exist** (correcting the earlier "major discovery")

With a **valid JWT**, 11 candidate paths were tested; all are native Spring 404s:

```
{"timestamp":"2026-09-18 20:56:52","status":404,"error":"Not Found","path":"/v1/user/tspCode"}
```

The `path` field shows the gateway stripped the `/zeekrlife-app-user` prefix ⇒ the service is there, the route is not.
**Conclusion**: the `000009 多设备登录` (multi-device login) seen earlier was merely a **gateway-layer session-invalidation interception** (happening before route resolution),
**and cannot be used as evidence that "the route exists".** The "tspCode route exists" conclusion drawn last round from this is a **misjudgment, now void.**

### 2) `identityType: 10` **does not work** in the China region, and it's unrelated to client headers

Full matrix (3 client-header sets × identityType 1–12 × 3 identifiers = 108 runs):

| Result | Explanation |
| --- | --- |
| `identityType=5` → **`000000` + token** | the only one that works (any identifier is fine) |
| `identityType=2` → `015000 参数错误` (parameter error) | another branch |
| **everything else all `015013 登录权限校验不正确`** (login permission check incorrect) | includes 10 |

The three client-header sets (none / minimal / **the overseas version's full `DEFAULT_HEADERS`**) gave **byte-identical** results.
⇒ **The overseas version's `tspCode + identityType:10` auth chain does not apply in the China region**; it's not a "missing client headers" issue.

### 3) The `x-signature` key is **unobtainable statically** (both brute-force rounds scored zero)

| Round | Candidate source | Scale | Result |
| --- | --- | --- | --- |
| 1 | dex plaintext string pool | **786,079** × 48 variants | 0 hits |
| 2 | **`libenv.so` decrypted strings** | 215 × 48 variants | 0 hits |

Variant coverage: 4 header sets (`ALLOWED` / `+CN extensions` / all `x-*` / CN headers only) × 3 query variants × 2 tail variants × 2 body variants.
⇒ The key is neither in the dex plaintext pool nor in the decrypted region of `libenv.so` ⇒ **encrypted wrapper** (`libEncryptorP.so` / iWall whitebox),
**unobtainable by pure static analysis.**

## 3. Full decryption of `libenv.so` (new asset this round)

`libenv.so` (133 KB, ARM64) is an **OLLVM-encrypted** layout (`EnvTableResolver.looks_like_new_format=False`,
the plaintext strings are only 165, all JNI names). Using the extractor's `NativeLibAnalyzer.decrypt_strings()`
(after `extended = data + 0x10000`, XOR by vaddr) **decrypted 91 strings**:

**(a) Gateway host table — 15 environments × 4 stages** (note: **all `zeekrlife*` / `zeekr.eu` / `zeekr.co.il`,
no `geely.com` / `gric` at all**):

```
f2e-sit / f2e-uat / f2e
gateway-int-test / gateway-int-dev / gateway-int-uat / gateway-pub-uat / gateway-pub
gateway-pub-azure.zeekr.eu / gateway-pub-em / gateway-pub-em.zeekrlife-test
gateway-int-uae-dev / gateway-int-uae-test / gateway-pub-uae-uat
gateway-pub-aws-em-ae / gateway-pub-hw-em-sg(-uat) / gateway-pub-hw-em-mx(-uat)
gateway-pub-*/zom-pay-gateway/zom-pay-core-service/
overseas-dev / overseas-sit / website-eu-uat / www.zeekr.eu / website-em-* / www.zeekr.co.il
```

**(b) Key table**: 22 32-hex values + a dozen or so 40-char values + 2 special-character long strings, of which already confirmed:

```
7dbae691d53f4f3c9fab905368370d80        = hmac_access_key (CN row)
hnpigl1f13fcb6a3ac834895b9e403c08cd895ce = hmac_secret_key (CN row)
```

**Inference**: `libenv.so` is the **overseas environment table**; the China-region / GRIC configuration is not here ⇒ confirming that GRIC belongs to **Geely's mid-platform** as an independent system.

## 4. Current conclusions (settled)

1. **What the App uses to control the car is the GRIC system** (`gric-zhf-api.geely.com` + `GEELYCNCH001M0001` + `x-signature` 2.1 +
   the `auth_client_zeekr_phone` token), **completely parallel to our GW3 `ZEEKR` system.**
2. **GRIC's signing key is unobtainable statically** (two brute-force rounds + whole-package + full .so scan + libenv decryption region).
3. **The China region has no `identityType:10` channel** (measured), so the "token swap" shortcut is closed.
4. ⇒ To get vehicle control working, **only two roads remain**:
   - **(A) Dynamic extraction**: a real rooted device + frida hook (following `wysie/zeekr_key_extractor`'s `vin_hook.js` idea;
     the APK is **arm64-v8a single-architecture**, an x86 emulator can't run it, so a real device or ARM environment is needed).
   - **(B) Full traffic capture**: capture one **App cold-start/login full process** and see directly where the GRIC token comes from
     (the earlier obstacle was "with a proxy you can't log in"; switch to a phone-side NIC-level capture App or VPN mode).

## 5. Parts that can be done autonomously next (no user needed)

Use the cached JWT to keep probing the China-region interface surface (the full `zeekrlife-*` family, the `ms-user-auth` China-region branches),
looking for an entry point that can swap for a GRIC/mid-platform token. Commands:

```bash
python tools/zeekr_bearer_chain.py            # reuse the cached JWT, run [2]→[4] directly
python tools/zeekr_probe.py --creds <tokens.json> gw1 GET <path>
```
