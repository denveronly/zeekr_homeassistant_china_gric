# Capture playbook — get the token the App actually uses

> Goal: the `[SDK]` access control decides by the **token's client identity**; our token (`azp=user_center_client_phone`, `scope=""`)
> is rejected, while the same account can control the car normally in the App. So the App must be carrying **another credential**.
> Static reverse engineering has reached a dead end (there are no plaintext SDK paths like `/snc/`, `/vcl/` in the dex; the URLs are assembled in code),
> **the only way to get a definitive answer is to capture one real control request from the App.**

---

## 0. Prerequisites (once chosen, do not keep second-guessing)

> **⚠️ Absolutely do not log the account into an emulator**: `accountLoginInfoDTO.logoutOtherDevices = true` in the GW1 JWT
> has been confirmed by testing ⇒ **the moment the emulator logs in, the App on the user's phone is immediately kicked offline**.
> In this scenario you must **capture the traffic directly on the user's own phone**.
>
> **Good news**: the SNC SDK ships its own `TrustAllCerts`
> (`com/geely/snc/network/http/auth/TrustAllCerts`,
> `com/zeekr/snc/vehicle/core/net/http/auth/TrustAllCerts`, both confirmed **[dex]**)
> ⇒ the car-control request **very likely does not validate the certificate**, so **neither root nor certificate unpinning is needed**.
> A user-level CA is most likely enough.

| Item | Description |
| --- | --- |
| Which account to use | **`16620192335`** (the one HA uses). It is **not** the account on your main phone ⇒ capturing will not disturb your daily use; the cost is that HA's car-control session gets kicked during this time, recoverable at any point. |
| What to capture | **one of the simplest car-control actions**: flash lights / honk / toggle AC, any one. A single successful/failed request is enough. |
| What to deliver | the capture file (`.har` or `.flow`) **or** a screenshot of that request's URL / headers / body. I will parse it directly with `tools/zeekr_capture_triage.py`. |

---

## 0.5 Option 0 (can be done even when away from home): a phone capture App, **no computer and no shared network needed**

For the "user is not home / only wants to use the phone" scenario. Using VPN mode, **the phone can capture even on its own cellular data**.

1. Install a capture App that supports VPN mode on the phone (**Reqable**, HttpCanary/小黄鸟 (Little Yellow Bird) and similar all work).
2. On first launch it will guide you to **install its CA certificate** (install it as a "VPN and apps" / user certificate) —
   this App is most likely sufficient, because the car-control segment goes through the SNC SDK's `TrustAllCerts`.
3. Start capturing → open the Zeekr App → **do one car-control action (flash lights / lock)**.
4. In the capture list find the request to **`snc-tsp-api.zeekrlife.com`** (the car-control one) and tap into it.
5. **Screenshot these three things for me**:
   - the **request headers** (I need to see the full `Authorization`, `X-APP-ID`, `X-VIN` and the other `X-*`);
   - the **request body** (that JSON);
   - the request line (`POST` + full path).

> What I need is "what the App actually carried". Once I have the `Authorization` I can decode its `azp`/`scope`,
> compare it with our `user_center_client_phone` / `""`, and the answer comes out immediately.

---

## 1. Option A (recommended, use when at home): capture the user's own phone traffic (no root)

**One-command start (recommended)**:

```bash
cd /d/zeekr_ha
C:/Users/rexze/.workbuddy/binaries/python/versions/3.13.12/python.exe tools/zeekr_capture_start.py
# If other App modules strictly validate certificates, switch to proxying only the Zeekr domains:  ... --zeekr-only
```

The script automatically detects the local LAN IP, binds and starts the proxy, and prints the phone-side steps with the IP filled in.
The parameter table below is for reference when operating by hand:

| Item | Value |
| --- | --- |
| Capture host IP | **192.168.6.21** |
| Proxy port | **8080** |
| CA certificate (to install on Android) | `C:\Users\rexze\.mitmproxy\mitmproxy-ca-cert.cer` |
| Capture output | `D:/zeekr_ha/capture/zeekr.flow` |
| mitmdump executable | `C:/Users/rexze/.workbuddy/binaries/python/envs/mitm/Scripts/mitmdump.exe` |

Steps:

1. **Connect the phone and computer to the same WiFi** (subnet `192.168.6.x`).
2. **Set the proxy on the phone**: WLAN → current network → proxy → manual
   - hostname `192.168.6.21`, port `8080`, save.
3. **Install the CA on the phone**: open **`http://mitm.it`** in the phone browser → choose Android →
   download the certificate (or just transfer `mitmproxy-ca-cert.cer` to the phone and install it) →
   Settings → Security → Install from storage device → choose **`VPN and apps`** (a user certificate is fine).
4. Open the Zeekr App and confirm the car works normally (this shows the proxy path is through).
5. **Do one car-control action** (flash lights / lock).
6. Stop capturing (on my side I just stop mitmdump), then I parse it with
   `tools/zeekr_capture_triage.py`.

> If in step 4 the App reports a network error: it means it really does validate that domain.
> First try **proxying only `snc-tsp-api.zeekrlife.com`** (with mitmproxy's `--allow-hosts`),
> because the car-control segment is sent by the SNC SDK (TrustAllCerts), while other App modules may validate strictly.

---

### Archived: Android emulator approach (**not applicable to this scenario**)

An emulator is inherently rootable and its system partition is writable, so you can install mitmproxy's CA as a **system-level certificate**
(`-writable-system` + `adb root` + `adb remount` + push it in named as `<hash>.0` into
`/system/etc/security/cacerts`). But as noted in §0, **logging into the emulator kicks out the user's phone**,
so use it only when "the account can be freely kicked".

### 1.1 Start the emulator (Windows)

```bash
# Use Android Studio's avdmanager to create a Pixel system image (API 30+ is fine)
# Key: -writable-system makes /system writable
emulator -avd Pixel_API34 -writable-system -no-snapshot-load
```

### 1.2 Install the system-level CA

```bash
adb root
adb remount

# mitmproxy generates mitmproxy-ca-cert.pem in confdir on first run
MITM=C:/Users/rexze/.workbuddy/binaries/python/envs/mitm
"$MITM/Scripts/mitmdump.exe" --version          # trigger CA generation
# Default CA location: %USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.pem

# Compute the <hash>.0 filename Android needs
HASH=$(openssl x509 -inform PEM -subject_hash_old -in "$USERPROFILE/.mitmproxy/mitmproxy-ca-cert.pem" | head -1)
adb push "$USERPROFILE/.mitmproxy/mitmproxy-ca-cert.pem" /sdcard/
adb shell "mkdir -p /system/etc/security/cacerts"
adb shell "cp /sdcard/mitmproxy-ca-cert.pem /system/etc/security/cacerts/$HASH.0"
adb shell "chmod 644 /system/etc/security/cacerts/$HASH.0"
adb shell "ls -l /system/etc/security/cacerts/$HASH.0"     # confirm it exists
adb reboot                                                  # system certificate takes effect after reboot
```

### 1.3 Start the proxy and make the emulator use it

```bash
# Terminal 1: capture (-w writes to a file, convenient for sending back for analysis)
"$MITM/Scripts/mitmdump.exe" -p 8080 -w D:/zeekr_ha/capture/zeekr.flow \
    --set block_global=false

# Terminal 2: point the emulator's proxy at the host machine (10.0.2.2 is the host address as seen from inside the emulator)
adb shell settings put global http_proxy 10.0.2.2:8080
```

### 1.4 Operation and acceptance

1. Install the Zeekr App in the emulator (adb install the APK directly, or via the app store).
2. **Log in with `16620192335` + SMS verification code** (I cannot receive the code on my side, you need to provide it or receive it on this number).
3. Confirm you can enter the vehicle page normally (this shows the network is through).
4. **Do one car-control action** (flash lights / honk).
5. Back in the terminal press `Ctrl+C` to stop capturing, and give me `capture/zeekr.flow`.

### 1.5 If the App does certificate pinning

Symptom: you can see the connection in mitmproxy, but the App reports a network error / no HTTPS content is visible.

```bash
# Use frida to disable pinning on the emulator (the emulator is rootable, just run frida-server directly)
adb push frida-server-<ver>-android-x86_64 /data/local/tmp/frida-server
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"
# Install frida-tools on the host (the same mitm venv works), hook with a generic unpinning script
objection -g com.zeekrlife.mobile explore --startup-command "android sslpinning disable"
```

---

## 2. Option B (easier, but may fail): real device + a no-root capture App

- Install **Reqable** (the mobile version of the former Charles) or a HttpCanary-like app, and capture using its **VPN mode**;
- the phone must install and trust its certificate (a user-level certificate);
- **precondition for success**: the App does not pin the certificate chain. The Zeekr App might pin ⇒ if it fails, switch to Option A.

Advantage: can be tried in 5 minutes; disadvantage: very likely will not capture the HTTPS content.

---

## 3. What I do after the capture (you just need to give me the file)

```bash
PY=C:/Users/rexze/.workbuddy/binaries/python/envs/default/Scripts/python.exe
cd /d/zeekr_ha

# .flow (mitmproxy native, analysis must use the mitm venv's python)
C:/Users/rexze/.workbuddy/binaries/python/envs/mitm/Scripts/python.exe \
    tools/zeekr_capture_triage.py capture/zeekr.flow --filter remoteControl

# .har (Reqable / Charles / mitmproxy can all export it)
$PY tools/zeekr_capture_triage.py capture/zeekr.har
```

The tool **automatically prints**:

- the `method / host / path` of each Zeekr gateway request;
- all identity-type request headers (`Authorization`, `X-APP-ID`, `app_code`, `X-VIN`, `sign` …);
- the **`azp` / `aud` / `scope` of the JWT in `Authorization`**;
- and finally a "**token identity distribution table**".

### Interpretation

| Capture result | Conclusion | Next step |
| --- | --- | --- |
| A token with `azp != user_center_client_phone` appears | Found the SDK client identity, the problem is characterized | Reverse engineer "how to obtain that token" (the starting point is now locked to that client) |
| Only `user_center_client_phone`, but it carried some header we don't send | The access control recognizes the header | Just add that header to the request |
| Only `user_center_client_phone`, and the headers match too | The access control recognizes some other dimension (e.g. X-VIN derivation, body signature) | Compare the body field by field for differences |

---

## 4. Directory convention

```
D:/zeekr_ha/capture/          <- put capture files here (.flow / .har)
```

`capture/` is for local use only, outside `.gitignore`; **it contains tokens, never commit it to the repo.**
