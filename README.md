# Zeekr EV · Home Assistant integration (China / GRIC)

> **English fork** of [RexzeLu/zeekr_ha](https://github.com/RexzeLu/zeekr_ha) for Zeekr cars on the
> **Chinese app / mainland China backend**. Entity names, select options, error messages and this README
> are translated to English. Strings that are matched against the car's or server's Chinese replies are
> intentionally left unchanged. Original Chinese README: [`README.zh-CN.md`](README.zh-CN.md).

Brings your Zeekr into Home Assistant. The integration has two login channels, and **which one you
pick decides whether you can control the car**.

## Which channel should I use? (This decides whether you get control)

| Channel | What it can do | What you need |
| --- | --- | --- |
| **SMS code (+86)** | **Status only**: battery, range, location, odometer, lock/window/trunk state, tire pressure, last report time… **No control** (see below) | Phone number + one SMS code |
| **GRIC token** | **Status + control**: climate, locks, windows and sunshade, flash/horn, charging, seats… The same channel the phone app uses | `refreshToken` + `x-vehicle-identifier` taken from the app |

> **Control only works over GRIC, also for the owner account.**
> The SMS channel goes through the old SNC gateway. **Reading status works**, but the gateway
> **rejects every command endpoint** (`079001 [SDK] interface not authorized`), and the legacy
> fallback pipe answers "success" **without executing anything**: you tap, nothing happens, no error.
> This has nothing to do with being the owner: **the current app itself no longer uses that channel**
> (it only stores GRIC tokens and sends commands over GRIC).

> E-mail / password login is not available in mainland China and is not supported.

## Features

| Platform | Entities |
| --- | --- |
| `device_tracker` | Vehicle location (GPS) |
| `sensor` | Battery level, range, odometer, speed, average consumption, interior/exterior temperature, climate set temperature, charging power/voltage/current, estimated full-charge time, charge limit, 12V battery, service distance/days remaining, tire pressure and tire temperature (×4), last status report |
| `binary_sensor` | Charging, charger plugged in, 4 doors / trunk / hood, 4 windows, tire pressure warnings |
| `lock` | Door lock, charge port lid |
| `switch` | Charging, windshield defrost, steering wheel heating, sentry mode, charging schedule, departure schedule, departure climate |
| `climate` | Climate (on/off + temperature + presets "standard / rapid cooling / rapid heating" + run duration) |
| `cover` | Sunshade, all windows |
| `select` | Seat heating (driver, passenger, rear), seat ventilation (driver, passenger): Off / Level 1–3 |
| `number` | Charge limit (50–100 %), climate run duration (1–60 min) |
| `button` | Flash lights, horn and flash, trunk open / close (toggle), turn off parking comfort, rapid cooling, rapid heating, refresh now |
| `time` / `datetime` | Charging schedule start / end, scheduled departure time |

> **On the SMS channel only the status entities work.** `sensor` / `binary_sensor` / `device_tracker`
> show data; the **control** entities (`lock` / `switch` / `climate` / `cover` / `select` / `number` /
> `button` / `time` / `datetime`) do nothing (the gateway rejects them, see above). Use GRIC for control.

## Installation

**HACS**: HACS → ⋮ → Custom repositories → `https://github.com/denveronly/zeekr_homeassistant_china_gric`,
type **Integration** → search "Zeekr EV" → Download → restart Home Assistant.

**Manual**: copy the whole `custom_components/zeekr_ev` folder into your HA `config/custom_components/`
→ restart Home Assistant.

Requires `pycryptodome>=3.20.0` (declared; HA installs it automatically).
The integration icon only shows on **HA ≥ 2026.3**; older versions work fine without it.

## Configuration

Settings → Devices & services → Add integration → search **Zeekr EV** → pick a channel.

### SMS code (read-only)

Choose the country code (default `+86`) → enter the phone number → enter the SMS code → done.
Credentials are stored in the config entry and renewed automatically; no further SMS codes needed.

⚠️ **This channel can only read status, it cannot control the car** (see above). Use GRIC for control.

> Use a **separate Zeekr account** and share the car to it, so HA and the phone app don't keep
> logging each other out.

### GRIC token (status + control)

You need two values, both from **the same app session on one device that can control the car**:

| Value | What it is | Where to get it |
| --- | --- | --- |
| **`refreshToken`** | A long JWT (~900 characters, three parts separated by `.`, starts with `eyJ`). GRIC can keep issuing new tokens from it, so it is effectively access to the account. | Response body of the app's login / token request (see below) |
| **`x-vehicle-identifier`** | A 44-character base64 value (ends with `=` or `_`), the encrypted identifier of **this car**. Needed for reading status and sending commands. | Request headers of any GRIC request that involves the car (see below) |

> `x-vehicle-identifier` is **computed in the app's memory at runtime**: it is not in the phone's
> storage (mmkv / shared_prefs / logs) and cannot be derived offline (the key is assembled inside the
> app's native library). ⇒ **You can only copy it from a real captured request.** Copy it once and it
> keeps working (it belongs to the car and never changes). It also stays valid if you switch accounts.

#### How to get both values

> **Tip:** use a **second Zeekr account** that the car is shared to, and capture from that one.
> After setup, Home Assistant owns that account's session, so don't log into it anywhere else.

**Method A: capture app on Android (phone or emulator, no root needed)**

1. Install a capture app with a **VPN mode**: **Reqable** (or HttpCanary and similar).
2. Install its **CA certificate** as a user certificate ("VPN and apps"). If Reqable's "save to
   Downloads" doesn't show the file, it is in `Download/Reqable/` as `<hash>.0`. Copy it to
   `Download/reqable-ca.crt` and install it via Settings → Security → Encryption & credentials →
   Install a certificate → CA certificate.
3. **Important:** the Zeekr app pins certificates on `*.zeekrlife.com`, so login fails with
   "network busy" while capture is on. In Reqable add an **SSL Proxying** rule in **Bypass Mode** for
   `*.zeekrlife.com`. Only `*.geely.com` needs to be decrypted.
4. Start capture → open the Zeekr app → go to the car page and **send one command** (flash lights or lock).
5. In the capture list filter on **`gric`**:
   - **`x-vehicle-identifier`**: open any request to a `gric-*.geely.com` host that involves the car
     (status, heartbeat `app/hb`, command), find `x-vehicle-identifier` in the **request headers**,
     copy the value → field 2 of the setup form.
   - **`refreshToken`**: **log out of the app and log in again** while capturing. Then find
     `POST https://gric-api.geely.com/ms-midground-user/api/v1.0/user/auth/get/token`
     (or `.../auth/refresh/token`) and copy `data.refreshToken` from the **response body**
     → field 1 of the form. Don't copy the `accessToken` next to it, and don't copy `authCode`
     from the request body.
6. **Close the Zeekr app right away** (or `adb shell am force-stop com.zeekrlife.mobile`) so it
   doesn't rotate the token before Home Assistant uses it.

Easy ways to force a fresh login on an emulator: `adb shell pm clear com.zeekrlife.mobile`
(wipes the app's data in the emulator only).

**Method B: computer + mitmproxy (phone and computer on the same Wi-Fi)**

The steps (install mitmproxy → set the proxy on the phone → install the CA → do one action in the app
→ read the traffic) are in [`docs/zeekr_capture_playbook.md`](docs/zeekr_capture_playbook.md)
(Chinese). It gets you the same values as method A.

**Method C: rooted phone (gets only the `refreshToken`)**

```bash
python tools/zeekr_device_pull.py --gric --write-tokens
```

Reads the app's data read-only over adb and writes the **latest** GRIC token pair into the local token
file (without triggering a new login). As noted above, **`x-vehicle-identifier` is not in the phone's
storage**, so you still need method A or B once to capture the request header.

#### If you captured them before and still have them locally

One command exports them again into a file ready for pasting (written to the desktop):

```bash
python tools/zeekr_gric_token.py form          # export
python tools/zeekr_gric_token.py form --print  # also print in plain text in the terminal
```

#### After you submit the form

> ⚠️ **Tokens are single-session**: HA follows whichever account you captured. Right after saving, HA
> exchanges the token for a new pair and the old one becomes invalid; the app's session for that
> account is signed out too. That is expected. Log in by SMS again only if you need to.
> ⚠️ **One car can only have one config entry in HA.** Delete the old entry before switching accounts
> (the integration refuses two entries for the same car).

If one account has several cars, **add one config entry per car** (each identifier belongs to one car).

### Do the tokens expire? (GRIC)

Normally no action needed: access token 7 days, refresh token 30 days. The integration renews the
access token 24 hours early, and the server extends the refresh token to 30 days each time, so
**as long as HA stays online it never expires**.

It only breaks in two cases: **HA is offline for more than 30 days in a row**, or **the same account
logs in on the phone app again** (only one holder per session, so HA gets kicked out). Then the
entities become unavailable and HA shows "Reconfigure / re-authentication required". Click it and
paste the values again; no need to delete the integration.

## Options (Configure → Options)

- **Polling interval (adaptive)**: default **1 minute**, which is the **fastest** step, not a fixed
  value. When the status doesn't change, the interval doubles (1 → 2 → 4 → 8 → max 15 min, never
  slower than what you set). As soon as something changes, the car is charging / driving / running
  climate, or you just sent a command, it returns to the fastest step. It reads the values cached on
  the server and **does not wake the car**, so a short interval doesn't drain the battery.
- **Allow control commands**: master switch. When off, every write is refused (read-only).
  ⚠️ Has no effect on the SMS channel, which cannot send commands anyway.
- **Seat heating / ventilation, climate, steering wheel heating duration**: default 15 minutes. The
  "Climate run duration" entity sets how long the **next** climate start lasts; changing it does not
  send anything to the car.
- **Features this car doesn't have**: ticked features **won't be created** (takes effect after
  reloading the integration). The gateway only says "this car supports seat heating", not whether the
  rear seats have it, so you have to tell the integration. For example, a 4-seat version without rear
  seat heating: tick "Seat heating rear left / rear right".
  ⚠️ Entities that already exist don't disappear automatically; delete them under
  Settings → Devices & services → Entities.

## Dashboard card

A ready-made Zeekr 001 card (top-view photo with door / window / trunk / charge
port controls, plus Charging and Climate drop-downs) is in
[`dashboard/`](dashboard/README.md).

## Actions

| Action | Description |
| --- | --- |
| `zeekr_ev.refresh` | Re-read the vehicle list and status now |
| `zeekr_ev.set_climate` | Turn climate on/off with duration and temperature (GRIC channel only) |
| `zeekr_ev.dump_raw_status` | Dump the raw gateway payload (without tokens) for troubleshooting |

```yaml
action: zeekr_ev.set_climate
data:
  duration: 10      # minutes, 1–60; defaults to the current entity value
  temperature: 24   # optional; defaults to the car's last setting
  enabled: true     # false = climate off
```

## FAQ

**Entities show "unavailable".** First make sure there is **only one** Zeekr entry under
Settings → Devices & services. Unique IDs are generated per car, not per account, so two entries fight
over the same IDs: HA keeps the first one and the rest become "restored" and unavailable. Delete the
extra entry → remove leftovers on the Entities page → restart HA.

**I press a switch / button and nothing happens.** Check the channel first: **the SMS channel can't
send commands** (the gateway rejects them with `079001`, the legacy pipe answers "success" but does
nothing). Switch to **GRIC**, also for the owner account (see the top). If you're already on GRIC,
see the next items: the car didn't confirm the command.

**I changed something in the phone app and HA shows it much later.** Delay = car reporting + HA
polling. A parked, sleeping car may report only every few hours to save power; a shorter poll interval
doesn't help. Look at the **Last status report** sensor: if it changes right after your action, the car
reported quickly and you wait at most one poll cycle; if it's much older than your action, the car
hasn't reported yet.

**The climate temperature differs from what I set in the app.** **HA cannot read the temperature set
in the phone app; that's a car limitation.** A remotely set temperature is written to the car only and
not returned by the status API; the value in the status is the **head unit's** setting. The integration
follows the head unit value until you set a temperature in HA; **after that HA's value wins** and isn't
overwritten. The app's range is `LO` — 16…28 — `HI`; the entity allows 15–30 to cover both ends.

**Are "Rapid cooling / Rapid heating" the real fast modes?** They're an **approximation**. The car does
have such a mode, but the command parameters for it have never been captured; the known climate command
only has on/off, temperature and duration. So these buttons **set the temperature to the ends of the
scale** (15 / 30 °C). "Max fan" and similar can't be expressed, and HA can't show whether the mode is
running.

**The state changes after pressing a switch and then jumps back.** The car is woken up via the cloud;
a command takes 10–30 seconds to take effect (GRIC can take longer). The integration shows the target
state immediately, then re-checks after 10 / 30 / 60 seconds; **if the car hasn't confirmed within 90
seconds it gives up and shows the real state**. So jumping back = the command didn't take effect.
If it keeps failing, check that "Allow control commands" is enabled in the options, then look for
errors from `custom_components.zeekr_ev` in the log.

**What if `x-vehicle-identifier` is wrong?** The form tells you right away with a vehicle identifier
validation error (the integration tests reading the car status before creating the entry), not at the
first poll. If it says the identifier is not this car's ciphertext
(`00A06 Decrypt X-VEHICLE-IDENTIFIER failed`), you copied a value that belongs to another car.

**Opening "Configure" says "Config flow could not be loaded / 500".** Update to **0.4.7 or newer**
(older versions' options form always crashed: `config_flow.py` used `cv` without importing it). If it
still fails, search the log under Settings → System → Logs for `zeekr` and post the traceback in an
issue.

**When reporting a problem, attach diagnostics**: Settings → Devices & services → Zeekr → Download
diagnostics, or Developer tools → Actions → `zeekr_ev.dump_raw_status`. Mask the VIN and plate number.

## License

MIT

> Protocol details, gateways and signing, field calibration and error codes (developer docs, Chinese)
> are in [`docs/troubleshooting.md`](docs/troubleshooting.md); detailed capture steps are in
> [`docs/zeekr_capture_playbook.md`](docs/zeekr_capture_playbook.md).
