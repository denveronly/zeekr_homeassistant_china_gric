# Server-side routes inside the Zeekr App (com.zeekrlife.mobile v5.0.5)

Source: the dex/so/json/xml string tables of the official APK (read-only extraction, nothing executed, nothing modified).
Extraction method: in addition to `tools/inspect_apk.py`, a one-off script was used to scan for the `/ms-…` regex.
These are **facts**, with priority over any inference — before changing an endpoint, check here first.

## Vehicle status
```
/ms-vehicle-status/api/v1.0/vehicle/status/carFridge
/ms-vehicle-status/api/v1.0/vehicle/status/powerMode
/ms-vehicle-status/api/v1.0/vehicle/status/qrvs
/ms-vehicle-status/api/v1.0/vehicle/status/vtm
/ms-vehicle-status/api/v2.0/vehicle/status/latest
/ms-vehicle-status/api/v2.0/vehicle/status/widget
```

## Remote control
```
/ms-remote-control/api/v1.0/remoteControl/aiClimate
/ms-remote-control/api/v1.0/remoteControl/control
/ms-remote-control/api/v1.0/remoteControl/getOxygenSupply
/ms-remote-control/api/v1.0/remoteControl/queryAiClimate
/ms-remote-control/api/v1.0/remoteControl/queryProcessResult
/ms-remote-control/api/v1.0/remoteControl/setOxygenSupply
/ms-remote-control/api/v1.0/remoteControl/setSmartTemp
/ms-remote-control/api/v1.0/remoteControl/temperature/del/pattern
/ms-remote-control/api/v1.0/remoteControl/temperature/get/pattern
/ms-remote-control/api/v1.0/remoteControl/temperature/save/pattern
```

## Charging
```
/ms-charge-manage/api/v1.0/charge/control
/ms-charge-manage/api/v1.0/charge/getBookingVtm
/ms-charge-manage/api/v1.0/charge/getChargingPlanNew
/ms-charge-manage/api/v1.0/charge/getLatestDischargeSoc
/ms-charge-manage/api/v1.0/charge/getLatestSoc
/ms-charge-manage/api/v1.0/charge/getLatestTravelPlanNew
/ms-charge-manage/api/v1.0/charge/setBookingVtm
/ms-charge-manage/api/v1.0/charge/setChargingPlan
/ms-charge-manage/api/v1.0/charge/setTravelPlan
/ms-charge-manage/api/v2.0/charge/getBookingCharge
/ms-charge-manage/api/v2.0/charge/getTravelPlan
/ms-charge-manage/api/v2.0/charge/setBookingCharge
/ms-charge-manage/api/v2.0/charge/setTravelPlan
```

## Authentication / user
```
/ms-user-auth/api/v1.0/account/affection
/ms-user-auth/api/v1.0/account/affection/unbind
/ms-user-auth/api/v1.0/auth/cloud/temp/code
/ms-user-auth/api/v1.0/auth/scanLogin
/ms-user-auth/api/v1.0/csp/relation
/ms-user-auth/api/v1.0/csp/resetPassword
/ms-user-auth/api/v1.0/csp/user
/ms-user-auth/api/v1.0/csp/verification/mobilePhone
/ms-user-auth/api/v1.0/csp/verification/mobilePhone/cspmobile
/ms-user-auth/api/v1.0/face/delete
/ms-user-auth/api/v1.0/face/dhu-wakeup
/ms-user-auth/api/v1.0/face/pictureUpload
/ms-user-auth/api/v1.0/face/registered
```

## Everything else (full list)
```
/ms-ai-cloud/api/v1.0/material/query
/ms-app-bff/api/1.0/permissions
/ms-app-bff/api/v1.0/certificate-center/getVehicleCertificate
/ms-app-bff/api/v1.0/climate/getScheduleList
/ms-app-bff/api/v1.0/mntmode/authCode/ownerAuthorization
/ms-app-bff/api/v1.0/mntmode/authCode/statusAndVehicleInfo
/ms-app-bff/api/v1.0/remoteControl/getSmartTemp
/ms-app-bff/api/v1.0/remoteControl/queryFreezerData
/ms-app-bff/api/v1.0/remoteControl/queryFridgeData
/ms-app-bff/api/v1.0/remoteControl/queryVehicleFragrance
/ms-app-message-center/api/v1.0/device/upload
/ms-app-online-center/api/v2.0/app/hb
/ms-charge-manage/api/v1.0/charge/control
/ms-charge-manage/api/v1.0/charge/getBookingVtm
/ms-charge-manage/api/v1.0/charge/getChargingPlanNew
/ms-charge-manage/api/v1.0/charge/getLatestDischargeSoc
/ms-charge-manage/api/v1.0/charge/getLatestSoc
/ms-charge-manage/api/v1.0/charge/getLatestTravelPlanNew
/ms-charge-manage/api/v1.0/charge/setBookingVtm
/ms-charge-manage/api/v1.0/charge/setChargingPlan
/ms-charge-manage/api/v1.0/charge/setTravelPlan
/ms-charge-manage/api/v2.0/charge/getBookingCharge
/ms-charge-manage/api/v2.0/charge/getTravelPlan
/ms-charge-manage/api/v2.0/charge/setBookingCharge
/ms-charge-manage/api/v2.0/charge/setTravelPlan
/ms-iot-control/api/v1.0/iotControl/downLink
/ms-iot-control/api/v1.0/iotControl/queryProcessResult
/ms-iot-device/api/v1.0/iot/device
/ms-iot-device/api/v1.0/iot/device/unbind
/ms-iot-device/api/v1.0/iot/product
/ms-iot-device/api/v1.0/iot/product/modelProductList
/ms-iot-status/api/v1.0/iotProperty/batchGetDeviceProperty
/ms-lbs-service/api/v2.0/sendToCar
/ms-log/v2.0/log/upload/getossuploadtoken
/ms-midground-user/api/v1.0/user/auth/cancel/login
/ms-midground-user/api/v1.0/user/auth/get/token
/ms-midground-user/api/v1.0/user/auth/hfScanLogin
/ms-midground-user/api/v1.0/user/auth/logout
/ms-midground-user/api/v1.0/user/auth/refresh/token
/ms-remote-control/api/v1.0/remoteControl/aiClimate
/ms-remote-control/api/v1.0/remoteControl/control
/ms-remote-control/api/v1.0/remoteControl/getOxygenSupply
/ms-remote-control/api/v1.0/remoteControl/queryAiClimate
/ms-remote-control/api/v1.0/remoteControl/queryProcessResult
/ms-remote-control/api/v1.0/remoteControl/setOxygenSupply
/ms-remote-control/api/v1.0/remoteControl/setSmartTemp
/ms-remote-control/api/v1.0/remoteControl/temperature/del/pattern
/ms-remote-control/api/v1.0/remoteControl/temperature/get/pattern
/ms-remote-control/api/v1.0/remoteControl/temperature/save/pattern
/ms-tsp-bks-geely/api/v1.5/digital-key-center/active-blu-key
/ms-tsp-bks-geely/api/v1.5/digital-key-center/auth-blu-key
/ms-tsp-bks-geely/api/v1.5/digital-key-center/create-blu-key
/ms-tsp-bks-geely/api/v1.5/digital-key-center/create-share-key
/ms-tsp-bks-geely/api/v1.5/digital-key-center/key-info
/ms-tsp-bks-geely/api/v1.5/digital-key-center/key-list
/ms-tsp-bks-geely/api/v1.5/digital-key-center/loop-active-status
/ms-tsp-bks-geely/api/v1.5/digital-key-center/reset-blu-key
/ms-tsp-bks-geely/api/v1.5/digital-key-center/update-blu-key
/ms-tsp-dkbs-geely/api/v1.0/app/calibration-info/lynkco-custom-calibration-info
/ms-tsp-dkbs-geely/api/v1.0/app/certificatecenter/create-app-certificate
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/activate-owner-fob-key
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/auth-blu-key
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/bind-ccc-id
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/ccc-set-switch-of-approach-unlock
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/ccc-set-switch-of-walk-away-lock
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/create-owner-fob-key
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/create-owner-nfc-key
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/create-share-key
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/destroy-ccc-key
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/get-bind-user-list
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/get-calibration-gears
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/get-remaining-slot-quantity
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/key-info
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/key-linked-share-account
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/key-list
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/key-status
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/loop-ccc-report-status
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/loop-key-status
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/pairing-code
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/phonecoef
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/remove-one-key
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/repush-key-to-vehicle
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/reset-calibration-gears
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/set-calibration-gear
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/set-switch-of-approach-unlock
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/set-switch-of-walk-away-lock
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/share-key
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/sync-key-list
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/unbind-ccc-id
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/unlock-owner-nfc-key
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/unpair-ccc-key
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/upload-mobile-brand
/ms-tsp-dkbs-geely/api/v1.0/app/digital-key-center/write-owner-nfc-key
/ms-tsp-dkbs-geely/api/v1.0/app/icce-key/check-device
/ms-tsp-dkbs-geely/api/v1.0/app/icce-key/create-owner-icce-key
/ms-tsp-dkbs-geely/api/v1.0/app/icce-key/create-share-icce-key
/ms-tsp-dkbs-geely/api/v1.0/app/icce-key/loop-icce-key-status
/ms-tsp-dkbs-geely/api/v1.0/app/icce-key/push-key
/ms-tsp-dkbs-geely/api/v1.0/app/icce-key/remove
/ms-tsp-dkbs-geely/api/v1.0/app/icce-key/upload-calibration-data
/ms-tsp-dkbs-geely/api/v1.0/app/traffic-card/delete
/ms-tsp-dkbs-geely/api/v1.0/app/traffic-card/get-card-status
/ms-tsp-dkbs-geely/api/v1.0/app/traffic-card/get-partner-token
/ms-tsp-dkbs-geely/api/v1.0/app/traffic-card/get-purchase-authority
/ms-tsp-dkbs-geely/api/v1.0/app/traffic-card/key-bind
/ms-tsp-dkbs-geely/api/v1.0/app/traffic-card/set-default-cardface
/ms-tsp-dkbs-geely/api/v1.0/app/traffic-card/traffic-card-list
/ms-tsp-dkbs-geely/api/v2.0/app/digital-key-center/get-ccc-key-list
/ms-tsp-dkbs-geely/api/v2.0/app/digital-key-center/key-list
/ms-tsp-dkbs-geely/api/v2.0/app/digital-key-center/sync-key-list
/ms-tsp-user-setting/api/v1.0/userVeh/setting/query
/ms-tsp-user-setting/api/v1.0/userVeh/setting/save
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/cancel
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/check-share
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/details
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/finish
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/force-cancel
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/force-finish
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/owner/delete
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/owner/share
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/owner/share-histories
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/owner/share-list
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/services
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share-keys
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share-status
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/accept
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/accept-histories
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/accept-list
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/delete
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/reject
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/social-sharing-info
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/upload-base64
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/update-auth
/ms-user-auth/api/v1.0/account/affection
/ms-user-auth/api/v1.0/account/affection/unbind
/ms-user-auth/api/v1.0/auth/cloud/temp/code
/ms-user-auth/api/v1.0/auth/scanLogin
/ms-user-auth/api/v1.0/csp/relation
/ms-user-auth/api/v1.0/csp/resetPassword
/ms-user-auth/api/v1.0/csp/user
/ms-user-auth/api/v1.0/csp/verification/mobilePhone
/ms-user-auth/api/v1.0/csp/verification/mobilePhone/cspmobile
/ms-user-auth/api/v1.0/face/delete
/ms-user-auth/api/v1.0/face/dhu-wakeup
/ms-user-auth/api/v1.0/face/pictureUpload
/ms-user-auth/api/v1.0/face/registered
/ms-user-manager/api/v1.0/user/get/user/info
/ms-vehicle-account/api/v1.0/vehicle-detail
/ms-vehicle-account/api/v2.0/model/series/getAllModelYearStyle
/ms-vehicle-capability-set/api/app/v1/vehicle/capability/available
/ms-vehicle-core/api/v1.0/vehicle/enterprise-vehicles
/ms-vehicle-core/api/v1.0/vehicle/favorite-vehicles
/ms-vehicle-core/api/v1.0/vehicle/set-default-vehicle
/ms-vehicle-core/api/v1.0/vehicle/set-nick-name
/ms-vehicle-core/api/v1.0/vehicle/set-plate-number
/ms-vehicle-defence/api/v1.0/fence/create
/ms-vehicle-defence/api/v1.0/fence/delete
/ms-vehicle-defence/api/v1.0/fence/enable
/ms-vehicle-defence/api/v1.0/fence/page
/ms-vehicle-defence/api/v1.0/fence/update
/ms-vehicle-extend/api/v1.0/car-audit-info/delete-audit-records
/ms-vehicle-guard/api/v1.0/sentinel/queryPhotoList
/ms-vehicle-status/api/v1.0/vehicle/status/carFridge
/ms-vehicle-status/api/v1.0/vehicle/status/powerMode
/ms-vehicle-status/api/v1.0/vehicle/status/qrvs
/ms-vehicle-status/api/v1.0/vehicle/status/vtm
/ms-vehicle-status/api/v2.0/vehicle/status/latest
/ms-vehicle-status/api/v2.0/vehicle/status/widget
/ms-vehicle-trail/api/v1.0/journalLog/delete
/ms-vehicle-trail/api/v1.0/journalLog/mark
/ms-vehicle-trail/api/v1.0/journalLog/onOff
/ms-vehicle-trail/api/v1.0/journalLog/trackpoint/list
/ms-vehicle-trail/api/v1.0/journalLog/trip/listForPage
```

---

# 2026-09-18 addendum: dex hardening conclusions + user/auth service routes + request-Bean field clues

## dex hardening (determines the choice of all later reverse-engineering methods)

The header of `classes.dex` (195 MB) is forged (`endian_tag`/`string_ids_off` etc. are all garbage values,
only the `file_size` field seems real = 175662436; the ~19.5 MB difference from the whole package 195141696 is suspected to be shell/packer data).
androguard can only parse out **45 shell classes**; the real dex's **id tables (string_ids/type_ids/
field_ids/class_defs) are not in plaintext** (confirmed with two methods: "anchor u32 back-lookup" and
"relative base-address Δ scan (including 4096
alignment and a full scan)"). The string **data area is readable in plaintext** ⇒ every conclusion can only come from
the string pool (this tool `tools/inspect_apk.py` and `scratch/dex_grep.py`).
**Structured parsing (field tables/annotations/bytecode) is a dead end, don't try it again.**

## User/auth service routes (verified alive on GW1 `api-gw-toc`)

The service `zeekrlife-app-user` **really exists** on GW1 (the earlier tspCode candidate 404s were just the wrong path).
Verified: `GET /zeekrlife-app-user/v1/user/pub/secretConfig` → `000000`,
returns an RSA **publicKey** (the App's secret is pushed dynamically, not hard-coded in the dex).

Key endpoints (the remaining 61 are in the session log, mostly privacy/profile related):

```
/zeekrlife-app-user/v1/user/pub/sms/authCode           SMS verification code
/zeekrlife-app-user/v1/user/pub/login/mobile           mobile-number login
/zeekrlife-app-user/v1/user/pub/login/mobile/oneClick  one-click login
/zeekrlife-app-user/v1/user/pub/login/platform
/zeekrlife-app-user/v1/user/pub/secretConfig           RSA public-key delivery (probed 000000)
/zeekrlife-app-user/v1/user/toc/authCodeByServiceCode  exchange an authCode by "scene code" (probed POST {} → 000005 场景代码,不为空 (scene code, cannot be empty))
/zeekrlife-app-user/v1/user/toc/validateAuthCode       (probed POST {} → 000005 验证码不为空,场景代码,不为空 (verification code cannot be empty, scene code, cannot be empty))
/zeekrlife-mp-auth2/v1/auth/accessCode                 (GET 400 / POST 405 ⇒ verb unknown, route exists)
```

⇒ There **is a "scene code (scene) → authCode → validate" chain**, the parameter name still has to be dug out (it is not
`serviceCode`). This is the next most likely entry point for exchanging a TSP capability token.

## The closed-loop shape of the control protocol (from toString constants)

- `ControlReqBean(controlType=` / `ControlReqBean15(controlType=` — the control request Bean;
  there is also the constructor signature `(String×9, List, OperationScheduling, TimerEntity, String)`.
- **`RemoteControlRsp(sessionId=`** ⇒ sending a control returns a **sessionId**;
  `ControlResult(sessionId=` / `ControlResultBean(code=` plus the route
  `queryProcessResult` ⇒ the App's flow is **send → get sessionId → poll the execution result**,
  not fire-and-forget. Our integration currently only sends and does not wait; if the GW2 channel has a matching
  result-query interface, the closed-loop verification should prioritize this.
- `OperationScheduling(duration=` (constructor parameters
  `Integer, Long, Boolean, Integer, Integer, Long, Long`);
  `TimerEntity(timers=`, `TimerInfo(timerId=`.
- Climate control: `AiClimateReqBean(dataSource=` (used by GW3 `aiClimate`), 
  `ClimateStatusVo(interiorTemp=`, `SmartTempSettingBean(heat=`.

## serviceId and parameter keys (confirmed from dex strings)

- **All serviceIds are in the dex**: `ZAF`/`RDL`/`RDU`/`RWS`/`RHL`/`RCS`/`RSM`/`PCM`/`RCE`,
  consistent with what the integration currently uses.
- ZAF parameter keys: `AC` (exists), `AC.temp`, `AC.duration` — nothing else.
- **The `rce.*` family**: `rce.conditioner` `rce.heat` `rce.ventilation` `rce.level`
  `rce.temp`, as well as **`rce.heat.{11,19,21,25,29,31,39}`** and
  **`rce.ventilation.{11,19,21,25,29,31,39}`** — the numeric suffixes look like a temperature/gear enum,
  usage still to be determined (they may be the value set of `rce.heat`, or they may be composite keys).

---

# 2026-09-18 late night: GW3 microservice map + the truth about the "SDK gate" + the vehicle-sharing business domain

## One-sentence conclusion

**The truth about `079001` is that it is an "SDK-level interface" gate — it blocks on client/token identity, not on parameters.**
Under the same GW3 token, for the same service the "control" interfaces are rejected while the "query" interfaces are allowed through.
⇒ **Continuing to guess the `serviceParameters` parameter on the GW2 side is a dead end and can be formally stopped.**

## Probe matrix (token: `azp=aud=user_center_client_phone`, `scope=""`)

| Interface | Result | Verdict |
| --- | --- | --- |
| `POST /ms-remote-control/v1.0/remoteControl/control` | `079001 [SDK]此接口未被授权，无法访问!` (interface not authorized, cannot be accessed) | SDK gate |
| `GET /ms-vehicle-status/api/v2.0/vehicle/status/latest` | same as above | SDK gate |
| `ms-vehicle-status/.../qrvs`, `/vtm`, `/widget` | same as above | SDK gate |
| `GET /ms-tsp-user-vehicle/.../vehicle-shares/services`, `/check-share` | same as above | SDK gate |
| `GET /ms-remote-control/v1.0/remoteControl/queryProcessResult` | `000002` sessionId missing | **usable (closed-loop result query!)** |
| `GET ms-tsp-user-vehicle/.../vehicle-shares/{owner/share-list, owner/share-histories, share/accept-list, share/accept-histories}` | `000000 ok` (total=0) | **usable** |
| `POST .../vehicle-shares/{owner/share, update-auth, cancel, share/accept}` | `000002` share type / share primary key cannot be empty | gateway allows through, parameter-level validation |
| `GET /ms-user-auth/api/v1.0/auth/cloud/temp/code` | `000000 ok` | **usable** |
| `POST /ms-user-auth/v1.0/auth/login` | `000000 ok` → 1047-character token | the login we currently use |

Key point: within the same service "control rejected / query allowed" ⇒ the gate is at **interface granularity** (most likely looking at the token azp/scope or the client identity),
unrelated to `X-VIN` or `serviceParameters`.

## GW3 token claims (decoded in practice)

```
iss   = https://snc-api-gw-inner.zeekrlife.com/auth-service/inner/v1/oauth/info
aud   = azp = user_center_client_phone     <- the "mobile-number login" client of the user center
scope = ""                                  <- empty
sub   = openId = 2068684429979209728
userId= 403215671   sid = <uuid>   RS256 / 1047 characters   exp 7 days
```

## Microservice map (55 prefixes enumerated from the full dex)

```
zeekrlife-bbs-theme(158) zeekrlife-mp-order(92) zeekrlife-mp-integral(64)
zeekrlife-app-user(60)   ms-tsp-dkbs-geely(54)  zeekrlife-config-order(26)
ms-tsp-user-vehicle(21)  ms-charge-manage(15)   zeekrlife-mp-mps(13)  ms-user-auth(13)
scenario-personalization(12) ms-remote-control(11) zeekrlife-mp-cmall(10)
map-d2d-auto-service(10) ms-app-bff(9)  ms-tsp-bks-geely(9)  ms-midground-user(6)
ms-vehicle-status(6)     sentinel-monitoring-service(6) zeekrlife-mp-account(6)
zeekrlife-mp-mkt(6)      zeekrlife-dod-search(5) ms-vehicle-defence(5) ms-vehicle-trail(5)
ms-vehicle-core(5)       zeekrlife-mp-sic(5)    ms-iot-device(4) zeekrlife-mp-sconfig(4)
zeekrlife-mp-auth2(3)    zeekrlife-pricing-order(3) zeekr-ud-ota(3) zeekrlife-mp-achieve(3)
ms-tsp-user-setting(2)   ms-user-manager(2)     snc-remote-config(2) file-service(2)
ms-iot-control(2)        scenario-mate-management-service(2) zeekrlife-mp-osp(2)
journey-statistics-service(1) ms-app-online-center(1) map-service(1) ms-lbs-service(1)
ms-vehicle-guard(1)      ms-ai-cloud(1) ms-app-message-center(1) ms-vehicle-account(1)
ms-vehicle-extend(1)     appconfig(1) ms-iot-status(1) ms-log(1) zeekrlife-mp-store(1)
```

### Full routes of the control-related services (dex originals)

```
# ms-remote-control (10)
/ms-remote-control/api/v1.0/remoteControl/aiClimate        <- note the /api/ segment
/ms-remote-control/api/v1.0/remoteControl/control
/ms-remote-control/api/v1.0/remoteControl/getOxygenSupply
/ms-remote-control/api/v1.0/remoteControl/queryAiClimate
/ms-remote-control/api/v1.0/remoteControl/queryProcessResult   <- closed-loop result query (verified usable)
/ms-remote-control/api/v1.0/remoteControl/setOxygenSupply
/ms-remote-control/api/v1.0/remoteControl/setSmartTemp
/ms-remote-control/api/v1.0/remoteControl/temperature/{del,get,save}/pattern

# ms-vehicle-status (6)
/ms-vehicle-status/api/v1.0/vehicle/status/{carFridge,powerMode,qrvs,vtm}
/ms-vehicle-status/api/v2.0/vehicle/status/{latest,widget}

# ms-iot-control (2)  <- 404 on GW1/GW2/GW3, host unknown
/ms-iot-control/api/v1.0/iotControl/downLink
/ms-iot-control/api/v1.0/iotControl/queryProcessResult

# ms-iot-device (4)   /ms-vehicle-core (5, 404 on both GW1/GW3)
/ms-iot-device/api/v1.0/iot/{device,device/unbind,product,product/modelProductList}
/ms-vehicle-core/api/v1.0/vehicle/{favorite-vehicles,enterprise-vehicles,set-default-vehicle,set-nick-name,set-plate-number}

# ms-user-auth (13)
/ms-user-auth/api/v1.0/auth/{scanLogin,cloud/temp/code}      <- temp/code verified 000000
/ms-user-auth/api/v1.0/{account/affection[/unbind],csp/{relation,resetPassword,user,verification/mobilePhone[/cspmobile]}}
/ms-user-auth/api/v1.0/face/{delete,dhu-wakeup,pictureUpload,registered}

# ms-vehicle-defence (geofence) / ms-vehicle-guard
/ms-vehicle-defence/api/v1.0/fence/{create,delete,enable,page,update}
/ms-vehicle-guard/api/v1.0/sentinel/queryPhotoList
```

## Vehicle sharing (CarShare) business domain — a complete "legitimate authorization" channel

The full REST family on `ms-tsp-user-vehicle` (dex originals, 21 routes):

```
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/owner/share          create a share
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/owner/share-list     shares I have sent out
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/owner/share-histories
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/owner/delete
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/accept         accept a share
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/reject
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/delete
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/accept-list    shares I have received
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/accept-histories
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/upload-base64
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share/social-sharing-info
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/share-status
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/details?shareId=
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/services             list of shareable services (SDK gate)
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/check-share          validate the shared-to account (SDK gate)
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/update-auth          set share permissions
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/cancel
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/finish
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/force-cancel
/ms-tsp-user-vehicle/api/v1.0/vehicle-shares/force-finish
```

App-side UI strings (dex): sidebar - vehicle sharing, create car share, accept car share, reject car share, finish car share,
set car share permissions, add share account, validate the shared-to account, cannot share with yourself, car shares received, car share details,
share code copied, maximum number of shares exceeded, shared digital key already exists.

SDK (`com.geely.snc.sdk.carshare`, Geely CarShare SDK):
`IGLCarShareService` / `GLGeelyCarShareService` methods: createCarShare, acceptCarShare, rejectCarShare,
cancelCarShare, finishCarShare, updateCarShare, detailsCarShare, onwerListCarShare,
acceptListCarShare, loopCarShareStatus, forceCancelCarShare, forceFinishCarShare,
ownerDeleteCarShare, acceptDeleteCarShare, uploadBase64CarShare, getUrlCarShare,
**queryVehicleServiceList**.
Request Beans: `GlCarShare{Create,Accept,Reject,Cancel,Finish,Update,Delete,Details,List,Loop,Url,Upload,VerifySharingUser,ForceCancel,ForceFinish}ReqBean`;
responses: `GlCarShare{ServiceList,Condition,Details}RespBean`, `ShareDetailFunctionInfo`, `ServiceListBean`,
`ShareVehVoHF(shareId=`, `VehicleShareBean.kt`.

**Verified (this account 16620192335)**: all four list endpoints return total=0 — this number is **neither a sharer nor a sharee**,
so the "full vehicle control despite not being the owner" does not come from vehicle sharing, but from a direct binding on the TSP side.

## Two candidate "token-exchange" chains (currently the highest priority)

1. **Scene code → authCode → SNC token**
   `POST /zeekrlife-app-user/v1/user/toc/authCodeByServiceCode` (probed, missing the "scene code" parameter, parameter name to be determined)
   → `com.geely.snc.login`'s `AuthLoginReqBean(authCode=)` → `AuthLoginRspBean(accessToken=)`
   (`IGLAuthLoginService` / `GLAuthLoginServiceImpl` / `GLTokenInterceptor`).
   Supporting evidence: `PhoneModifyAuthCodeReq(scene=` ⇒ "scene" is exactly the input concept of authCode;
   `com.geely.snc.action.login.elsewhere` is the "logged in elsewhere / session taken over" broadcast we ran into.
2. **`AccessCodeReq(clientId=)` → `/zeekrlife-mp-auth2/v1/auth/accessCode`** (route exists, verb to be determined).

## Vehicle-control SDK (native layer, SDK-token holder)

`com.zeekr.snc.vehicle`: `core/net/http/VclHttpApi|VclHttpReq|VclHttpRsp|VclHttpUrl|VclHttpParam`,
`core/net/mqtt/VclMqttMsg|VclMqttRsp` (**MQTT channel**), `core/net/wifi/VclWifiSdk`,
`iot/GLIotService`, `iot/utils/IIotTokenHelper`, `log/ITokenHelper`, `dlp/dmc/ZeekrDlcTokenHelper`,
`utils/ZeekrENVKt` (`getVclCtrlApi$module_vehicle_release`).
⇒ The SDK token is most likely delivered via the **IoT token** system.

## Converged request-header clues (dex header-name pool)

`X-TSP-PLATFORM`, `X-REGION-ID`, `X-A-Key`, `X-S-Key`, `X-Key-Token`, `X-APP-KEY`, `X-APIKEY`,
`X-API-SIGNATURE-{NONCE,VERSION}`, `X-HMAC-{ACCESS-KEY,ALGORITHM,DIGEST,SIGNATURE}`,
`X-ENCRYPTION-{KEY,KEY-ID,VERSION}`, `X-Request-CipheredOverlay{Key,IV,Version}`.

## 2026-09-18 late night continued: empty share records vs owner has already shared — needs cross-checking on the App side

### New probes (GW3, token `azp=user_center_client_phone`)

```
GET  /ms-app-bff/api/1.0/permissions?tspPlatform=<n>   the account's permission list for this vehicle
     numbers 0/1/2 → passes param validation but 079001 (SDK gate); strings → 000002 param check failed
     ⇒ tspPlatform is a **numeric enum** (not a platform name), and this interface is behind the SDK gate
POST /ms-app-bff/api/v1.0/mntmode/authCode/ownerAuthorization   owner authorization code → 079001 (SDK gate)
POST /ms-app-bff/api/v1.0/certificate-center/getVehicleCertificate  vehicle certificate → 079001
GET  /ms-vehicle-account/api/v1.0/vehicle-detail               → 079001
POST /ms-tsp-user-setting/api/v1.0/userVeh/setting/query       → 000000 ok (usable)
POST /ms-tsp-user-vehicle/.../vehicle-shares/share-status      unique identifier = **traceId**
     ⇒ the share flow is "create → returns traceId → POST share-status to poll" (matches GlCarShareLoopReqBean(traceId=))
GET  /ms-user-auth/api/v1.0/auth/cloud/temp/code               → data.code = a 32-char hex temporary code (used for QR-scan login)
     POST on the same path → 000010 (GET only); /auth/scanLogin is also POST only
POST /ms-user-auth/v1.0/auth/login (when device fields are missing)  → 000002 [设备ID不能为空 (device ID cannot be empty), 设备类型不能为空 (device type cannot be empty)]
GET  /ms-user-auth/api/v1.0/account/affection (family account)  → 00A01 404 (not on GW3)
GET  /ms-user-middle... /ms-user-manager/api/v1.0/user/get/user/info → 00A01 404
```

### The complete picture of the `[SDK]` gate boundary (as of this round)

**Rejected (079001 `[SDK]此接口未被授权，无法访问!` (interface not authorized, cannot be accessed))**: `remoteControl/control`, `vehicle/status/*`,
`shares/services`, `check-share`, `ms-app-bff/.../permissions`, `mntmode/authCode/ownerAuthorization`,
`certificate-center/getVehicleCertificate`, `ms-vehicle-account/vehicle-detail`.

**Allowed through**: `remoteControl/queryProcessResult`, the 4 query endpoints of `vehicle-shares` and the parameter-validation layer of the write endpoints,
`ms-tsp-user-setting/.../setting/query`, `ms-user-auth/.../temp/code`,
`zeekrlife-app-user/.../{secretConfig, authCodeByServiceCode, validateAuthCode}`.

⇒ The gate presents as an **interface whitelist**, unrelated to `X-VIN`, parameters, or the account's vehicle permissions (the same account can control the vehicle normally inside the App).

### Contradiction to verify (needs confirmation on the App side)

The owner has already shared the vehicle with `16620192335` and it "enjoys all vehicle-control permissions", but on the interface side:

```
GET vehicle-shares/owner/share-list      → 000000 ok, total=0
GET vehicle-shares/share/accept-list     → 000000 ok, total=0
GET vehicle-shares/{owner/share-histories, share/accept-histories} → 000000 ok, total=0
```

That is: **this number is neither a sharer nor a sharee (from the server's point of view)**. Two possibilities:
1. The share record has expired/become invalid (App has strings like "authorization expired", "this share is no longer valid"),
   but the account still keeps the TSP-side binding ⇒ vehicle control works while the share list is empty;
2. The vehicle-control permission comes from **another binding** (family account `account/affection`, family members, enterprise vehicles, etc.),
   rather than vehicle-shares.

Decision criteria: in the owner's App, under "shares I have sent out", the status / validity period / permission items of that record;
and whether that number can still actually control the vehicle inside the App (e.g. flash the lights / honk).
