# Zeekr App dynamic extraction playbook (rooted phone edition)

> Goal: obtain the signing shared secret for `GEELYCNCH001M0001` + the source chain of the `auth_client_zeekr_phone` token.
> Prerequisites: a rooted Android phone with the App in a **logged-in** state, connected to this machine over USB.

## Why this time it is very likely to work

1. **Runtime hooking completely bypasses dex hardening**. Classes that static analysis cannot see are all in plaintext once the App is running —
   the hardening shell only protects the bytes on disk, it cannot protect the classes and methods in memory.
2. **No re-login needed**. The App on the phone is in a logged-in state, the key and tokens are already in memory/the private directory,
   so you just read what is already there, which means **it will not kick the session on your own phone** (`logoutOtherDevices: true` is not triggered).
3. **There is a fallback even on failure**: even if the key cannot be hooked, the private data pulled in stage 1 at least contains the tokens and their storage structure,
   which can directly answer half the question, "where does the GRIC token come from".

---

## 0. Pre-checks

### Phone side
1. Settings → About phone → tap "Build number" 7 times to enable Developer options.
2. Developer options → turn on **USB debugging**.
3. Connect to the computer with a data cable; when the phone shows "Allow USB debugging?" → **Allow** (check "Always allow").
4. Pull down the notification shade and change the USB purpose from "Charging only" to **File transfer / MTP**.
5. **Grant shell authorization in Magisk**: open Magisk → Superuser → check whether `Shell` is in the list;
   if not, allow it at the next prompt. This step is a prerequisite for stages 1 and 2.

### Computer side
```bash
export PATH="/c/Users/rexze/.workbuddy/binaries/PortableGit/versions/1.2.0/cmd:/c/Users/rexze/.workbuddy/binaries/PortableGit/versions/1.2.0/usr/bin:/usr/bin:/bin:$PATH"
cd /d/zeekr_ha
PY="C:/Users/rexze/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
/c/ADB/adb devices -l      # should show a line <serial>  device
```

Dependencies already in place (no need to reinstall): `adb 35.0.1` (`C:\ADB\adb.exe`),
`frida 17.18.0` + `frida-tools 14.10.4` (this machine's default venv),
`frida-server 17.18.0 android-arm64` already cached (`%TEMP%\frida_server_cache\`, 58.8 MB).

---

## Stage 1: pull the private data first (no frida needed, the easiest)

```bash
$PY tools/zeekr_device_pull.py
```

The script will: identify the device and architecture → elevate privileges (try `adb root` first, otherwise fall back to `su -c`) →
tar up `/data/data/com.zeekrlife.mobile` and pull it locally → unpack → scan and output a report.

The output is in `%TEMP%\zeekr_device\<timestamp>\`:
- `data/` — the full App private directory (shared_prefs / databases / files / no_backup)
- `scan_report.txt` — JWT tokens (including `azp`/`iss`/`scope`/validity, the token itself redacted),
  32/40-digit hex key candidates, and the hit locations of keywords like `GEELYCNCH` / `gric-` / `SecretKey` / `auth_client_zeekr_phone`

**Interpretation points**:
- If a JWT with `azp = auth_client_zeekr_phone` appears in the report ⇒ we have directly obtained the very token the App uses,
  and all that remains is to copy its exchange method.
- If some 32-digit hex string appears in `shared_prefs` with `SecretKey` nearby ⇒ it is very likely the signing key,
  go straight to stage 3 to verify.

Clean up the device's temporary files: `$PY tools/zeekr_device_pull.py --clean`

---

## Stage 2: frida dynamic hooking

### 2.1 Deploy frida-server (must be rerun each time the phone reboots)
```bash
$PY tools/zeekr_frida.py --setup
```
Downloads/pushes/authorizes/starts frida-server in the background, and sets up `adb forward tcp:27042`.
It uses **remote mode rather than USB mode**, avoiding the old trap of frida's USB driver on Windows.

### 2.2 Confirm it connects and can see the App
```bash
$PY tools/zeekr_frida.py --list
```

### 2.3 Cold-start the App with hooks (recommended)
```bash
$PY tools/zeekr_frida.py --spawn
```
A cold start can catch one-time writes at startup like `setSecretKey` — this is the best moment to grab the key.
Restarting the App does not affect the logged-in state (the session is on disk), **nor does it cause a kick-out**.

If the App has anti-frida detection (crashes on launch, or no output at all after hooking), switch to an obscure port and filename:
```bash
$PY tools/zeekr_frida.py --setup  --port 8899 --device-path /data/local/tmp/fsd
$PY tools/zeekr_frida.py --spawn  --port 8899 --device-path /data/local/tmp/fsd
```

### 2.4 Operate on the phone as prompted
```
① Open the App, enter the vehicle page, wait for it to finish loading
② Do one car-control action, the lightest one is fine (flash lights / honk)
③ Go back to the computer and press Ctrl+C
```
The log is printed in real time and written to `%TEMP%\zeekr_hook_<timestamp>.log`.

### Key markers in the output
| Marker | Meaning |
| --- | --- |
| `KEY-CANDIDATE` | **A suspected key has appeared** — the thing we most want |
| `class-found` / `class-hits` | Signing/encryption-related classes discovered at runtime (invisible statically) |
| `AUTH-HEADER` | The token identity the App actually uses (azp/iss/scope, token body redacted) |
| `AUTH-URL` | Authentication-type request URL — used to locate the token-source endpoint |
| `SIGN-HEADER` | Live signing headers (x-signature / nonce / timestamp / app-id) |
| `native-hits` | Exported functions in the native library bearing SecretKey/Sign strings |
| `hook-miss` | A hook did not get installed (not fatal, keep watching the other markers) |

---

## Stage 3: verify the key (the critical step)

Once you have a candidate key, verify it immediately against a real request from the capture — a hit **simultaneously** proves the key is correct and the algorithm is correct:

```bash
$PY tools/zeekr_sig_verify.py --key <candidate key>
# Or feed the candidates from the frida log in a batch
$PY tools/zeekr_sig_verify.py --keys-file candidates.txt --all
```

The tool iterates over 4 header sets × 12 canonical-string variants, printing the full canonical string on a hit.
It has been round-trip tested with self-made requests (the hit path works normally), and negative-tested against real samples.

**Once there is a hit, there is no more suspense**: the GRIC call chain is understood byte-for-byte (gateway, path, all request headers, request body,
the `x-vehicle-identifier` generation method, the `sessionId` + `queryProcessResult` loop),
and all that remains is the engineering work of swapping the signing implementation in `api_sms.py` for a new set of key/header parameters.

---

## Common failures

| Symptom | Cause and fix |
| --- | --- |
| `adb devices` empty | USB debugging not enabled / not tapped Allow on the phone / the cable is charge-only without data |
| `--setup` reports "device not rooted" | Magisk did not grant Shell authorization; or the model restricts `adb root`, the script falls back to `su -c` automatically |
| frida-server won't start | Blocked by SELinux or a vendor security center. Run `su -c '/data/local/tmp/frida-server -l 0.0.0.0:27042'` manually in a phone terminal to see the error |
| `--list` can't connect | Port forwarding not set up, rerun `--setup`; or change the port to avoid 27042 |
| No output at all after hooking | The App has anti-debugging. Try different `--port`/`--device-path`; if still no good, switch to `--attach` to attach to an already-running App |
| Output flooding the screen | `class-hits` is already rate-limited by logic beyond `class-count`; if still too much, use `--out` to write to a file and then filter |

## Red lines

- The whole process is **read-only**, does not modify App data, and does not touch car-control write operations (except for the one you manually tap in stage 2).
- **Do not log out** during the process. When you really need to re-login, first confirm on the computer side that no probe script is running,
  otherwise the two sides will kick each other (`079021`).
- The pulled data contains complete tokens, **never commit it to the repo** (both `%TEMP%` and `capture/` are within the gitignore coverage).
