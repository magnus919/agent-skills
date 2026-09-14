# Bus electrical budget

Bus / mode / target speed:

Logic rail(s):


| Device/module | Pull-up present | Leakage/sink limit | Address/strap | Added capacitance |
|---|---|---|---|---|
| | | | | |

Effective parallel pull-up:

`Rp(min)` source and result:

`Cb` estimate and contributors:

`Rp(max) = tr(max)/(0.8473 × Cb)`:

Selected value and speed/power rationale:

Measured SDA/SCL rise/fall time:

Probe model/capacitance/ground attachment:

Scan side effects considered:

Controller timeout and bus-clear owner:


## Verification rows

| Stage | Expected | Observed | Result/inference |
|---|---|---|---|
| idle | SDA/SCL released to logic rail | | |
| scan | documented response only | | clue, not identity |
| identity | known register/bytes | | |
| recovery | bounded clear and known reset | | |

Open unknown, owner, and next measurement:
