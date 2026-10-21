# Zeekr 001 dashboard card

A Home Assistant dashboard card for this integration: key numbers at the top, a
top-view photo of the car with door / window / hood / trunk state badges, an
"All windows" control, a trunk open / close button and a charge port lid toggle
(left rear, where the 001's port is), tyre pressures at the wheels, quick
actions (lock, flash, sentry, sunshade), and two drop-downs for **Charging**
and **Climate**.

Two versions, same controls:

- [`zeekr001_card_side.yaml`](zeekr001_card_side.yaml): for a 3/4 front-left studio photo
  (car facing left). Left-side doors, windows, wheels and the charge port flap
  sit on the car; the right side, which isn't visible, is a badge row at the top.
  Photo: `/config/www/zeekr001_side.png`.
- [`zeekr001_card.yaml`](zeekr001_card.yaml): for a top-view photo, front pointing up.
  Photo: `/config/www/zeekr001_top.png`.

## Requirements

- This integration (Zeekr EV, GRIC channel for the controls)
- [Expander Card](https://github.com/MelleD/lovelace-expander-card) from HACS,
  for the Charging / Climate drop-downs
- A photo of your car saved in `/config/www/` under the name the version you
  use expects (see above); restart Home Assistant if the `www` folder is new

## Install

1. Open `zeekr001_card.yaml` and replace every `CAR_` with your car's entity
   prefix. Find it under Settings → Devices & services → Entities, search for
   "battery level": if the entity is `sensor.zeekr_001_battery_level`, replace
   `CAR_` with `zeekr_001_`.
2. Dashboard → Edit → Add card → **Manual** → paste the YAML.
3. Positions on the photo are percentages (`left` / `top`). Nudge them to fit
   your image.

## Notes

- Doors and individual windows report state only (the car has no command to
  open a single door or window); they change colour when open. The window icon
  in the middle controls **all windows**.
- Trunk, charge port lid and door lock ask for confirmation before acting. The
  trunk command toggles the power tailgate; from Home Assistant it closes
  **without** the PIN the app asks for, so only use it when you can see the car.
