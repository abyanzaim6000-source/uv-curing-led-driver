# Three-minute interview walkthrough

## 0:00–0:40 · Describe the design

“I designed a four-layer 12 V UV curing driver PCB with independent PWM and current control for 365 nm and 405 nm outputs. The lower-voltage channel uses a SEPIC. The higher-voltage channel uses a boost stage with an input eFuse.”

Open the [schematic](uv_driver/rev_c/UV_DRIVER.kicad_sch) and show the two TI TPS92691 controller ICs and current-sense shunts.

## 0:40–1:45 · Explain one design decision

The [SEPIC simulation](docs/UV_REV_C_SIZING.md#365-nm-switched-cross-check) reproduced a growing oscillation with separate inductors. Explain how switching to a coupled part cleared the 128 modeled conditions and what faults and thermal limits would still need testing. Show how the [C1 prototype analysis](docs/UV_REV_C1_PROTOTYPE.md) led to reduced current and a slower 405 nm soft start.

## 1:45–3:00 · Show the verification evidence

Open the [routed PCB](uv_driver/rev_c/UV_DRIVER.kicad_pcb), point out the power loops and Kelvin sense routing, and show the KiCad reports in the [quote package](results/UV_DRIVER_RevC1_QUOTE_ONLY.zip). Explain how you would test it first on dummy loads. Present the current and stability results as simulations.

## Résumé bullet

Designed and simulation-verified a four-layer dual-channel UV LED driver PCB in KiCad using TPS92691-based SEPIC and boost converters. Modeled switching stability and PWM transients and produced fabrication files with clean ERC, DRC, and schematic-to-PCB checks.
