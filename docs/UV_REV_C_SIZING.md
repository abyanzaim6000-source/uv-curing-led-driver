# Rev C component sizing and release decisions

Rev C is a design proposal. The active KiCad files are the routed Rev B baseline. Keep the quote archive out of fabrication until the new schematic and layout have passed review.

## Proposed component values

| Circuit | Rev C candidate | Engineering check |
| --- | --- | --- |
| 365 nm switch-current shunt R102 | 0.100 Ω, ±1%, low-inductance 2512, at least 1 W. Vishay WSL2512R1000FEA is a candidate. | Approximately 3.73 A screened threshold at duty 0.60 using 497 mV comparator threshold, typical 200 mV ramp and the high resistor tolerance. At the high comparator threshold, the zero-ramp ceiling is 5.56 A, before delay and overshoot. This choice needs switch fault stress and SEPIC stability review. |
| 405 nm switch-current shunt R202 | 0.120 Ω, ±1%, low-inductance 2512, at least 1 W. Vishay WSL2512R1200FEA is a candidate. | Approximately 2.97 A screened threshold at duty 0.683 under the same assumptions. Zero-ramp ceiling is 4.63 A. Size the eFuse and its clamp for the different steady input and switch-peak currents. |
| Both output capacitor banks | Reserve footprint area for two Panasonic EEHZV1J470P 47 µF/63 V hybrid capacitors per output, the existing local ceramics, and room for extra capacitance if the ripple budget requires it. | Manufacturer lists 22 mΩ ESR at 100 kHz and 8 × 10.2 mm can size. Two give 94 µF nominal and 75.2 µF at initial −20% tolerance. Temperature, aging, impedance at switching frequency and current sharing still need checking. |
| 405 nm COMP | Start design evaluation at 1.0 µF effective integral compensation, R206 shorted and C210 unpopulated. | Meets the revised averaged-model screen at all 96 corners. Validate on the actual PWM burst and startup waveforms before freezing the values. |
| 365 nm COMP | Keep a configurable COMP footprint. Use 1.0 µF effective only as a modeling case. | The averaged model flagged a growing mode in 136 of 256 cases. The current independent-inductor configuration or its damping needs further evaluation before selecting production values. |

The shunt candidates increase separation from the previous ~2.5 A operating-peak estimates. A first-order half-down-slope screen at 165 kHz and minimum inductance requires about 188 mV per cycle for SEPIC and 159 mV for boost. The SEPIC approximation sums both inductor slopes and includes 0.7 V diode allowance. TI specifies its ramp at 200 mV typical, so the SEPIC case has limited unallocated margin. Allow a short optional IS-series resistor footprint for slope adjustment near the controller. Characterize IS-edge noise, current limit, alternating pulses and fault recovery before accepting either shunt. At the high static threshold, instantaneous shunt dissipation is about 3.1 W for SEPIC and 2.5 W for boost. Check pulse ratings, hot saturation, MOSFET and clamp stress, and the 405 nm eFuse trip interaction. [TI TPS92691 datasheet](https://www.ti.com/lit/ds/symlink/tps92691.pdf), [Vishay WSL](https://www.vishay.com/docs/30100/wsl.pdf), [Panasonic ZV series](https://na.industrial.panasonic.com/products/capacitors/polymer-capacitors/polymer-hybrid-aluminum-electrolytic-capacitor/series/150071).

With 75.2 µF, ideal capacitive droop at 165 kHz is about 31 mV for 365 nm and 33 mV for 405 nm at the respective maximum duty estimates. A 2 Ω dynamic LED load and 5% peak-to-peak ripple allow only 65 and 60 mV at the outputs. The remaining ~34 and ~27 mV allowance must cover ESR, ESL and routing. A nominal 11 mΩ parallel hybrid ESR and 2.5 A current step alone give about 28 mV. The ceramic bypass and compact path therefore matter, especially on the boost channel. Treat 56–110 µF as a sensitivity range for loop analysis, not a procurement limit. Recalculate open-load discharge, inrush and soft start because both new banks store substantially more energy than Rev B.

## Reproduce the analysis

Run `python3 scripts/check_uv_rev_c.py` with NumPy available. The boost model reuses the prior TI averaged equations with the new shunt and a 56–110 µF range. The 1.0 µF COMP case gives roughly 105–195 Hz crossover and 49–83° phase margin. The prior 220 nF candidate clears the screen in only 34 of 96 cases with the revised shunt and capacitor bank.

The SEPIC sweep includes two separate inductors, coupling and output capacitors, nominal winding resistance, an averaged summed-current comparator and an outer integrator. The growing mode survived increasing the COMP capacitor, so changing COMP alone has not closed the screen. The model omits switching delay, actual diode and switch losses, capacitor ESR and parasitic damping. Compare against the TPS92691 SEPIC reference circuit and a switching model before deciding between better damping and a coupled inductor. Check how those changes affect the fault and current ripple estimates. [TI TPS92691 SEPIC evaluation board guide](https://www.ti.com/lit/ug/slvual8/slvual8.pdf).

The bundled KiCad ngspice ran both existing diagnostics. The behavioral regression passed. The 405 nm case regulated at about 600 mA steady state and reached 1.64 A at PWM restart in the low-input case. That spike comes from the existing behavioral Rev B model and remains a bring-up risk to investigate. It does not predict the Rev C candidates' transient response.

## 365 nm switched cross-check

Run `python3 scripts/check_uv_sepic_switching.py` with NumPy. This Python model propagates the SEPIC's separate MOSFET-on and diode-on equations each clock cycle. A peak-current comparator ends the on interval. The script solves for each periodic steady state and measures whether small perturbations grow from one switching cycle to the next. It includes a 0.6 V fixed diode drop, 50 mΩ MOSFET resistance, winding DCR, the 0.10 Ω switch shunt and a 1.0 µF effective COMP integrator. It uses symmetric winding tolerance endpoints with the same line, load and capacitor sensitivities as the averaged SEPIC screen.

| Inductor arrangement | Growing cases | Highest modeled on-time end current |
| --- | ---: | ---: |
| Separate 68 µH windings | 92/128 | 2.397 A |
| Separate 68 µH windings with 0.47 Ω in series with the coupling capacitor | 8/128 | 2.427 A |
| Idealized coupled 68 µH windings, k = 0.90 | 0/128 | 2.058 A |
| Coilcraft MSD1583T-473MED candidate, 47 µH per winding | 0/128 | 2.220 A |
| Coilcraft MSD1583T-333MED candidate, 33 µH per winding | 0/128 | 2.468 A |

The largest separate-inductor growth occurred near 10.8 kHz, within the earlier coupling-resonance estimate. The averaged and switched models agreed on the stability classification at 108 of the 128 shared corners. In an additional direct 200-cycle check at low line and high LED voltage, a small perturbation grew to 1.59 times its starting magnitude with separate windings and decayed to 0.26 times with the 47 µH coupled candidate. Changing the numerical perturbation used for the Jacobian by a factor of ten preserved the classification at those test points.

Carry forward a **1:1 coupled-inductor footprint** for the 365 nm Rev C design. The 47 µH candidate gives lower operating peak and better slope-compensation headroom. The 33 µH alternative gives more room against saturation in a fault. Coilcraft lists 5.4 A and 6.4 A at 10% inductance drop in its respective SEPIC table. Compare the winding-current sum at the proposed approximately 5.56 A static shunt ceiling, with propagation-delay overshoot and hot saturation curves, before choosing the population. Recalculate slope margin at minimum inductance and maximum LED voltage for the selected part. Confirm dot polarity, manufacturer pad dimensions and core loss before routing. Series damping alone did not clear the simulated separate-inductor sweep. [Coilcraft MSD1583T specifications](https://www.coilcraft.com/en-us/products/power/coupled-inductors/1-1-shielded-coupled/msd_t/msd1583t/), [TI AN-1484 SEPIC design note](https://www.ti.com/lit/an/snva168e/snva168e.pdf).

This is a local steady-state stability screen. It assumes a stiff input and continuous rectifier conduction around the solved cycle. The modeled controller has a simple comparator and integrator. Switching delays, nonlinear magnetics, startup, open-load behavior, PWM restart and short circuits still need separate validation. No KiCad values, footprint placements or fabrication files were changed.

## Coupled inductor selection for the Rev C draft

Use **Coilcraft MSD1583T-473MED (47 µH per winding)** and **0.120 Ω ±1% for R102** as the draft population. This supersedes the 0.100 Ω SEPIC shunt candidate above. Keep the 33 µH part as a same-series layout option subject to a new slope and fault check. The updated switching sweep used k = 0.98, 0.160 Ω per winding as a 125 °C copper-resistance estimate, and the 0.120 Ω shunt. All 128 modeled corners were locally stable. The highest modeled normal switch peak was 2.22 A. At duty 0.62, the low comparator threshold, maximum shunt resistance and typical ramp give an approximate 3.08 A trip, leaving about 0.86 A above the modeled normal peak.

At 165 kHz, with 37.6 µH minimum initial winding inductance, a further 10% inductance reduction, k = 0.98, and 16.7 V off-state winding voltage, the half-down-slope screen requires about 183 mV per cycle. TI specifies 200 mV typical. The 33 µH alternative would require about 217 mV with the earlier 0.100 Ω shunt under the same assumptions. Retain an IS tuning provision and verify alternate-pulse behavior across temperature and during open-load recovery. The normal-load screen does not establish slope margin at the highest OVP voltage. [TI TPS92691 datasheet](https://www.ti.com/lit/ds/symlink/tps92691.pdf).

The 0.120 Ω shunt gives a 4.63 A upper static threshold at zero ramp. Using 14.5 V per winding during the on interval and the above reduced inductance, the estimated current rises by about 0.04 A over TI's typical 100 ns IS-to-GATE delay or 0.13 A in a 300 ns total turn-off sensitivity case. The resulting 4.76 A is about 0.64 A below Coilcraft's 25 °C typical 5.40 A point for 10% inductance drop. Coilcraft defines this point using the sum of both winding currents. The public sheet gives typical room-temperature saturation data. The hot 10%-drop point would have to stay above 4.76 A to clear this screen, equivalent to retaining about 88% of the room-temperature figure. Hot saturation, effective fall time, shunt pulse heating and repeated faults remain verification gates. The estimate assumes normally precharged C101 and excludes switch ringing and nonlinear saturation dynamics. [Coilcraft MSD1583T datasheet, pages 1–2](https://www.coilcraft.com/getmedia/8d898720-dd5a-438f-9500-665db0e36d7c/msd1583t.pdf).

### Verified winding and footprint handoff

| Coilcraft pin | Rev C net | Winding role |
| --- | --- | --- |
| 1 | VIN_12V | Winding 1 dotted end |
| 3 | U1_SW | Winding 1 undotted end |
| 2 | GND | Winding 2 dotted end |
| 4 | U1_SEP | Winding 2 undotted end |

The pin map matches the manufacturer’s SEPIC application drawing. Preserve the four current-path nets when replacing L101 and L102 with one symbol. In the manufacturer’s recommended PCB land-pattern view, pads read 2–1 across the upper pair and 3–4 across the lower pair. Use the land-pattern view when building the footprint and keep the surrounding exposed areas solder-mask covered as shown. Allow for the 15.5 mm maximum body width and 8.6 mm maximum height. [Coilcraft package and application drawing, page 1](https://www.coilcraft.com/getmedia/8d898720-dd5a-438f-9500-665db0e36d7c/msd1583t.pdf).

The selection and pin map are ready for a Rev C KiCad draft. Rev B remains the routed baseline. The 405 nm startup/PWM overshoot and the prototype release gates remain open.

## KiCad draft handoff

The [Rev C project](../uv_driver/rev_c/UV_DRIVER.kicad_pro) contains the updated 365 nm winding symbol, 0.120 Ω switch shunt and [four-pad Coilcraft footprint](../uv_driver/rev_c/UV_RevC.pretty/L_Coilcraft_MSD1583T.kicad_mod). The footprint has 2.3 × 4.2 mm pads, 3.7 mm column pitch and a 7.9 mm row gap. KiCad ERC returned zero errors and warnings. Netlist comparison against Rev B verified the expected four connections and preserved every other pin-to-net assignment. The next section records the updated output and COMP population. Board layout and release checks remain open. Keep nearby routing masked in the copper areas marked by Coilcraft.


## Output banks and 405 nm restart screen

- C112/C113 and C212/C213 are Panasonic EEHZV1J470P, 47 µF / 63 V each, alongside the existing output ceramics. The local Panasonic F footprint replaces the stock can footprint and uses the verified standard-product land dimensions. Both switch-current shunts now read 0.120 Ω.
- Both COMP networks have 0 Ω series links at R106/R206, 1.5 µF nominal 25 V X7R 0805 placeholders at C109/C209, and 100 pF tuning positions C110/C210 marked DNP. The analysis used 1.0 µF effective capacitance. Check the exact part at COMP bias, temperature, tolerance and aging, then re-run stability with the extracted bounds. The nominal 1.5 µF value is a draft component specification.
- KiCad ERC passed with zero errors and warnings. The exported netlist verified the positive terminal of each new capacitor on the relevant converter output and the negative terminal on GND. All existing pin-to-net assignments were preserved, and both DNP flags were confirmed. [Panasonic EEHZV1J470P specifications](https://na.industrial.panasonic.com/products/capacitors/aluminum-electrolytic-capacitors/lineup/conductive-polymer-hybrid-aluminum-electrolytic/series/150071/model/150082).

Run `python3 scripts/check_sim.py --uv-405-rev-c`. The new screen swaps in the 0.120 Ω shunt and models the output as a bulk branch with 11 mΩ equivalent ESR plus 4.7 µF effective ceramic capacitance. It reuses the original behavioral control law and simplified current limiter. It therefore screens the larger bank and shunt together, with no claim to reproduce the TPS92691 and its new COMP network during PWM transitions.

| Modeled condition | Before restart | First switching cycle peak | Full restart peak |
| --- | ---: | ---: | ---: |
| Rev B reference, 10.8 V input / 34 V load | 36.73 V | 1.642 A | 1.642 A |
| Rev C nominal, 12 V / 33 V | 34.41 V | 0.932 A | 0.946 A |
| Rev C low line, 10.8 V / 34 V | 34.64 V | 0.471 A | 1.031 A |
| Rev C high line, 13.2 V / 32 V | 32.56 V | 0.426 A | 1.176 A |

The Rev B reference peak occurs in the first switching cycle as the charged output is reconnected to the load. In the revised low- and high-line cases, the first-cycle peaks drop below the steady current and the larger peaks occur later in the modeled restart transient. This separates the stored-voltage concern from the later control response. All tested Rev C cases still exceeded the provisional 0.65 A screen during startup or restart. Varying the modeled bulk from 56 to 110 µF at low input left restart peaks near 1.03–1.04 A, so component sizing alone has not cleared the screen.

A 75.2 µF bank stores about 75 mJ at 40 V before the ceramic contribution. Close discharge behavior, safe initial operating current and the TPS92691-specific restart behavior before testing an emitter. On the first dummy-load run, capture VOUT, LED current, PWM, DDRV and COMP with enough time resolution to see the first switching cycle and the later recovery. A controlled restart change must address the measured mechanism. Controller-specific transient validation, PCB placement and fabrication release are pending.


## TPS92691 restart screen and first PCB placement

Run `python3 scripts/check_uv_405_restart.py`. The new switching model holds COMP during PWM-off, parks the clock, and keeps COMP feedback disconnected until sensed switch current reaches the held command on restart. It also models a separate cold-start clamp and an idealized DDRV load connection. These behaviors follow the datasheet sequence. The public TI download SLVMBE8A contains an encrypted PSpice library. The Python model uses first-order device and load equations, with ideal DDRV timing, simplified thresholds, no eFuse model, and no capacitor ESR, MOSFET gate dynamics or PCB parasitics. Absolute peaks require confirmation using the TI model in PSpice or on a dummy-load bench. [TI TPS92691 datasheet, §§7.3.8–7.3.11](https://www.ti.com/lit/ds/symlink/tps92691.pdf), [TI controller model download](https://www.ti.com/product/TPS92691#design-tools-simulation).

| Case with 100 nF soft start | Startup peak | Restart peak |
| --- | ---: | ---: |
| 12 V input / 33 V load / 75.2 µF / 1 ms off | 0.648 A | 0.655 A |
| 10.8 V / 34 V / 75.2 µF / 1 ms off | 0.641 A | 0.669 A |
| 13.2 V / 32 V / 75.2 µF / 1 ms off | 0.650 A | 0.646 A |
| 10.8 V / 34 V / 56 µF / 20 ms off | 0.613 A | 0.624 A |
| 13.2 V / 32 V / 110 µF / 20 ms off | 0.752 A | 0.612 A |

The datasheet-sequenced model settles near 600 mA before restart in all cases. The worst restart in this sweep is 0.669 A, above the provisional 0.65 A screen. At the high-input/high-capacitance startup corner, changing the modeled soft-start capacitor from 100 nF to 150 nF or 220 nF lowered the startup peak from 0.752 A to 0.646 A or 0.604 A. The modeled restart peak stayed at 0.612 A at that corner. Keep 150 nF and 220 nF as bench tuning options. The board retains 100 nF at C207 pending startup timing and eFuse checks with the actual controller.

The 1.5 µF 0805 TDK CGA4J3X7R1E155M125AB is a concrete COMP candidate. Its ±20% initial tolerance and X7R temperature specification can reduce the nominal value to roughly 1.02 µF before DC bias and aging, if both worst-case reductions are applied. Confirm the effective range from TDK characteristic data before treating 1 µF as a guaranteed minimum. [TDK part data](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA4J3X7R1E155M125AB).

The [Rev C PCB](../uv_driver/rev_c/UV_DRIVER.kicad_pcb) now contains 73 footprints and a 110 × 76 mm four-layer outline. The four output hybrids use a local footprint based on Panasonic’s standard size F drawing, with 4.0 × 2.0 mm pads and a 3.1 mm inner gap. The 365 nm coupled inductor, coupling capacitor and rectifier are grouped for shorter top-layer connections. The placement verification found zero DRC violations and zero schematic parity issues, with 156 unconnected items to route. ERC returned zero violations. Route the compact commutation loops, gate and IS paths, then the Kelvin pairs and input protection. Add test access and review thermal vias and mounting before the final DRC and fabrication export. [Panasonic recommended land pattern](https://industrial.panasonic.com/content/data/CP/PDF/Hybrid/Hybrid_landP_e.pdf).

## Fully routed Rev C draft

The [Rev C board](../uv_driver/rev_c/UV_DRIVER.kicad_pcb) uses hand-routed top-layer switching and bulk-capacitor paths, plus separate bottom-layer Kelvin takeoffs at the two LED shunts. Low-current routing was carried forward where pads matched and completed with a local signal router and manual fixes. The 365 nm switch and coupling node route totals are approximately 25.5 mm and 16.5 mm, down from 31.6 mm and 30.8 mm in Rev B. These are segment sums including branches. Both main gate routes retain their Rev B lengths of approximately 29 mm and 22 mm. Check gate ringing and assess shortening where practical before release. [TI layout guidance, §10](https://www.ti.com/lit/ds/symlink/tps92691.pdf).

The ground pours are on F.Cu and In1.Cu. The inner plane is reserved for ground, and 22 ground vias connect the outer pads and plane. The controller exposed pads have two adjacent vias each, with eFuse ground fanned out near its ground pins. Verify copper weight, the pad-to-plane thermal path, stencil apertures, via treatment and temperatures under sustained load. The board uses 0.15 mm minimum signal breakout widths and wider power paths, with the fine trace rule carried forward from Rev B. Confirm this width and drill rules with the selected fabricator. No board mounting holes are assigned.

### First-article probe access

Use these existing pads for controlled dummy-load bring-up. Dedicated test-point footprints and mounting remain optional follow-up layout improvements before release if the assembly or fixture requires them.

| Measure | 365 nm location | 405 nm location |
| --- | --- | --- |
| Raw input and circuit ground | J1 pins 1 and 2 | J1 pins 1 and 2 |
| PWM input | J2 pin 1, ground J2 pin 2 | J2 pin 3, ground J2 pin 2 |
| Protected rail | — | C202 pin 1, local ground C202 pin 2 |
| Converter output | C112 pin 1, local ground C112 pin 2 | C212 pin 1, local ground C212 pin 2 |
| LED current monitor | C108 pin 1 | C208 pin 1 |
| COMP | Unpopulated C110 pin 1 | Unpopulated C210 pin 1 |
| Switch shunt | R102 pin 1, local ground pin 2 | R202 pin 1, local ground pin 2 |

Use short insulated pigtails or a secured probe on small pads. Scope ground belongs on circuit ground. The LED negative terminals are switched. Use a suitable differential measurement for voltages between floating nodes, such as across an LED output or a high-side sense resistor. For switch-node ringing, use the appropriate rated probe with a short local reference.

The [routing report](../results/uv-driver-rev-c-routing-drc.json) records the final KiCad geometry, connection and schematic-parity check. The board remains a prototype draft pending a release review of assembly, probe/mechanical access and electrical margins.
