# UV driver PCB · first power-stage design pass

## Design inputs

- **Source:** 12 V nominal. Use 10.8–13.2 V at the driver connector for the first analysis. This ±10% window is an assumption pending the supply specification and motor transient data.
- **365 nm output:** Four Broadcom AUV3-SQ62-0RT0K emitters in series, 650 mA nominal. Use 13.6–16.0 V for the first calculation, based on the 25 °C datasheet voltage range at 700 mA. Verify the hot/cold load bounds separately. Include current regulation tolerance and ripple in the LED current and thermal budget.
- **405 nm output:** One TaoYuan TY-405nm20W specimen, supplier-listed at 32–34 V and 600 mA. Use 600 mA for power sizing. Start bench testing at reduced current and finalize the current limit when the supplier confirms the allowable current and thermal limits.
- **Control:** Two independent enable/PWM inputs with hardware default-off. Use an external controller interface for the first schematic. Motor current is outside the driver-board load estimate and its effect on the shared source still needs review.

## Selected topology for the first schematic

Use one **TPS92691** constant-current controller per wavelength. Use a **SEPIC for 365 nm** so the smaller voltage difference between the string and the source does not make the stage dependent on the output always being higher than the input. Use a **boost for 405 nm**, where the normal load voltage is well above the assumed input range. Both stages use a series LED-current shunt, their own switch-current limit and output-overvoltage network. The 405 nm boost stage also needs a way to interrupt the LED or input path during faults because the inductor and diode can still conduct from input to output after switching stops.

Start the circuit from TI's reference schematics. The examples establish topology, controller wiring and component roles. Current, compensation, operating limits and component values must be recalculated for these UV loads. [TPS92691 datasheet](https://www.ti.com/lit/ds/symlink/tps92691.pdf) · [TI SEPIC reference board](https://www.ti.com/tool/TPS92691EVM-001) · [TI boost reference board](https://www.ti.com/tool/TPS92691EVM-752)

## Initial sizing

Use 200 kHz nominal (40 kΩ at RT/SYNC, 165–230 kHz datasheet range). Use 85% efficiency for preliminary input current, and use the datasheet's 165 kHz low end and 80% of nominal inductance for ripple screening. These are first-order continuous-conduction estimates.

| Parameter | 365 nm SEPIC | 405 nm boost |
| --- | ---: | ---: |
| Nominal LED current | 0.650 A | 0.600 A |
| Maximum LED power in first load range | 10.4 W | 20.4 W |
| Ideal duty over input and load endpoints | 51–60% | 59–68% |
| Estimated maximum average input current | 1.13 A | 2.22 A |
| Inductance candidate | 2 × 68 µH, uncoupled for first analysis | 82 µH |
| Maximum estimated inductor ripple | 0.81 A p-p per inductor | 0.75 A p-p |
| Maximum first-order switch peak | 2.50 A | 2.56 A |
| LED sense resistor candidate | 0.22 Ω, 1%, ≥0.5 W | 0.22 Ω, 1%, ≥0.5 W |
| Nominal IADJ voltage with that shunt | 2.002 V | 1.848 V |
| Open-load OVP analysis target | 22 V output | 40 V output |

The TPS92691 nominal current equation is I_LED = V_IADJ / (14 × R_CS). Use Kelvin connections for the LED shunts. Tolerance analysis must include the IADJ network, current-sense offset and shunt. The switch-current shunt is a separate part and remains to be sized with slope compensation and comparator limits. The OVP numbers are starting targets. Verify the divider threshold, hysteresis, restart behavior and overshoot before finalizing ratings. [TPS92691 datasheet](https://www.ti.com/lit/ds/symlink/tps92691.pdf)

With both channels at the maximum preliminary load, the LED stages deliver 30.8 W and draw an estimated 3.36 A at 10.8 V and 85% efficiency. Reserve a 12 V, 5 A class source for LED-only development and measure shared-source behavior before adding the motor. Confirm wire, connector, protection and supply ratings separately.

## Schematic work now queued

1. Draw the two TPS92691 sheets, with their own magnetics, MOSFET, diode, LED shunt and connector. Rate the SEPIC switch and diode for input plus output voltage, and the boost switch and diode for the output voltage, in both cases with headroom for OVP and ringing.
2. Size input/output and SEPIC coupling capacitors for effective capacitance and RMS current. Compute current limit, slope compensation, soft start and loop compensation from the selected components.
3. Design the default-off control and boost output disconnect/fault path. Add LED thermal monitoring or a defined external interlock interface. Verify startup, open/short, PWM, and concurrent operation under current-limited conditions.
4. Review ERC, footprints and estimated component temperature before making the first layout. Keep the hardware release gate open until the 405 nm sample and thermal information are confirmed.

## Rev A schematic draft

Open [UV_DRIVER.kicad_pro](../uv_driver/UV_DRIVER.kicad_pro) in KiCad and select the schematic editor. The project-local symbol table resolves the bundled controller and voltage-reference symbols. The original PT4115 project remains a reference.

- J1 supplies nominal 12 V and ground. J2 carries PWM_365, ground, and PWM_405. The PWM controller must meet the TPS92691 2.7 V maximum high threshold with margin. Both schematic inputs have 10 kΩ pulldowns and each DDRV drives a series return-path FET.
- Each local LM4040 generates 2.5 V. The divider and 0.22 Ω shunt give nominal setpoints of approximately 650 mA and 598 mA. The 0.15 Ω switch-current shunts and both OVP dividers are provisional. Open-load nominal trip estimates are approximately 21.8 V and 39.5 V before tolerance and hysteresis.
- KiCad 10.0.3 ERC reported zero errors and warnings. The exported XML netlist was checked against all TPS92691 pins, both switching and LED return paths, both sense circuits, both OVP dividers, and the external connectors. ERC and connectivity checks do not establish stable operation or fault protection.
- Complete parts and footprints, compensation, switch-current limit and startup/fault validation before layout. The boost return FET disconnects the intended load path. A direct output-to-ground short can bypass it and still needs an upstream protection decision. Thermal shutdown/interlock implementation and the exact 405 nm module information remain open.

## Rev A static protection screening

Using the TPS92691 datasheet limits and assuming 1% tolerance for the protection resistors, the draft values give the following first-order thresholds. These estimates exclude transient overshoot, propagation delay and ringing. The OVP values are rising trip thresholds; restart also depends on hysteresis and discharge behavior. [TPS92691 datasheet](https://www.ti.com/lit/ds/symlink/tps92691.pdf), electrical characteristics and section 8.1.11.

| Check | Low | Typical | High |
| --- | ---: | ---: | ---: |
| Switch-current comparator trip with 0.15 Ω, either channel | 3.28 A | 3.50 A | 3.70 A |
| 365 nm output OVP with 100 kΩ / 6.04 kΩ | 20.33 V | 21.77 V | 23.44 V |
| 405 nm output OVP with 100 kΩ / 3.24 kΩ | 36.88 V | 39.51 V | 42.56 V |

The provisional switch-current trip has headroom over the first-pass normal switching peaks of 2.50 A and 2.56 A. Screen each component against the high fault trip and its own current path. The boost inductor carries the full switch current; in the SEPIC the switch current is the sum of the two inductor currents during the on interval. The 405 nm output-capacitor review must use the actual capacitance after DC bias at the working voltage, maximum OVP tolerance and observed overshoot.

Next schematic review: choose the MOSFETs, rectifiers, inductors, and exact capacitors; design the input fault disconnect for the boost feed-through path; then size and verify the compensation against the effective output capacitance and LED dynamic resistance. Run startup, open-load, PWM restart, and short-circuit checks on the design before committing to layout.

## Rev B · Component candidates and input protection

The active [KiCad schematic](../uv_driver/UV_DRIVER.kicad_sch) records candidate part numbers and footprints for the principal switching components. The selections are for a prototype review and still need sourcing, thermal and electrical signoff.

| References | Part | Role and remaining validation |
| --- | --- | --- |
| Q101, Q102, Q201, Q202 | Infineon IRLR3410TRPBF, 100 V logic-level DPAK | Main switches and series LED-return disconnects. Validate gate switching loss at the available drive voltage and measured ringing. [Datasheet](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlr3410-datasheet-en.pdf) |
| D101, D201, D301 | Diodes Inc. B5100C, 100 V/5 A, SMC | Rectifiers and protected boost input negative transient clamp. Verify diode loss and clamp envelope. [Datasheet](https://www.diodes.com/datasheet/download/B5100C.pdf) |
| L101, L102, L201 | Bourns SRP1770TA-680M (68 µH) on SEPIC; SRP1770TA-101M (100 µH) on boost | Same land pattern. The boost is revised from 82 µH to 100 µH. At 165 kHz and −20% inductance the first-order boost estimate is 0.61 A maximum p-p ripple and about 2.50 A maximum switch peak across the input and LED endpoints. [Datasheet](https://www.bourns.com/docs/Product-Datasheets/SRP1770TA.pdf) |
| C101, C103, C104, C203, C204 | Murata GRM32ER71H475KA88L (SEPIC), GRM31CC72A475ME11L (boost) | Both are 4.7 µF nominal. Boost uses 100 V rated capacitors. Confirm effective capacitance under bias and temperature and coupling-capacitor RMS current. [Murata component data](https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/dynamic-model/component-list-d-mlcc-2608.ashx) |
| C102, C202 | Panasonic EEU-FR1V101 | 100 µF/35 V radial input bulk. Check ripple and add local switching bypass as required. [Datasheet and dimensions](https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1V101) |

U3 (TPS26630RGER) interrupts the 405 nm input upstream of the inductor and rectifier. MODE is open for latch-off. The 6.04 kΩ ILIM setting targets approximately 3 A, with a 47 nF slew capacitor. The 365 nm stage stays on the raw input rail. Confirm the shared 12 V source rating and polarity before connecting either stage. Verify boost startup with PWM asserted or held low, and test short-circuit trip timing, input clamp and component thermal stress. Reset follows a power cycle or a valid shutdown reset. [TI TPS2663 datasheet](https://www.ti.com/lit/ds/symlink/tps2663.pdf)

### Verification and remaining compensation work

- KiCad 10.0.3 gave [zero errors and warnings for Rev B](../results/uv-driver-rev-b-erc.rpt). The exported netlist independently confirms the eFuse pin connections, isolation between the raw and protected rails, and clamp orientation. See the [Rev B schematic preview](../results/uv-driver-rev-b-schematic.png).
- [The ngspice boost feed-through diagnostic](../spice/uv_boost_feedthrough.cir) disables the main switching MOSFET and applies a 2.7 Ω fault load. The unprotected supply still provided 4.16 A. The protected branch provided 4.11 A before its idealized switch was commanded open, then averaged 0.12 µA of source current afterward. This checks the circuit path. The model deliberately does not represent eFuse trip timing, internal current limiting, or electrical overstress.
- TI's downloaded TPS92691 PSpice library is encrypted. KiCad's local ngspice cannot run that model. Closed-loop startup, compensation, PWM and fault transients remain unverified. The COMP network in Rev B remains provisional. Recalculate it with effective biased capacitance and the LED incremental resistance at the operating point, then verify loop stability and transients with compatible PSpice or a current-limited bench prototype. The fault-path test is independent of that work.

## Placement and electrical release checklist

The [four-layer placement draft](../uv_driver/UV_DRIVER.kicad_pcb) has a provisional 110 × 76 mm outline with 70 footprints. KiCad 10.0.3 reported zero placement violations, zero schematic parity issues and 148 unrouted connections. Connector choices are Phoenix Contact MKDS 1,5/2-5,08 for input and LED outputs and a provisional 2.54 mm three-pin PWM header. IC footprints use exposed pads without prebuilt via-in-pad holes while the fabrication process is open. Thermal connections and via treatment belong in the routing and fabrication review. [Connector datasheet](https://www.phoenixcontact.com/en-pc/products/pcb-terminal-block-mkds-15-2-508-1715721) · [Placement DRC](../results/uv-driver-placement-drc.json)

| Former “open before layout” item | Status and evidence needed for release |
| --- | --- |
| Component selections and footprints | Main parts and connectors assigned; dimensions, enclosure clearance, supply harness, and fab stackup are provisional. Review voltage-dependent capacitance and dissipation before finalizing compensation and copper. |
| Boost eFuse and inrush | Feed-through isolation checked with an idealized switch. The [passive precharge run](../spice/uv_boost_inrush.cir) used 13.2 V, 1368 V/s commanded ramp and high capacitor values. It measured 0.182 A peak with boost switching disabled and reached 99% of input in 9.55 ms. Verify real inrush with PWM low and asserted at power-up, and verify trip, latch-off and reset with a current-limited source. This run does not establish real eFuse timing or stress. |
| Loop compensation and electrical tests | Open. Obtain effective output capacitance and LED incremental resistance, set COMP values, then verify loop stability and load transients at low and high input. Use compatible PSpice for the encrypted TI controller model or a controlled bench setup. Perform enable/PWM startup and open-load tests before stressing a prototype. |
| Thermal and fault behavior | Open. Confirm 405 nm module dimensions, cooling and derating. Verify boost short protection and temperature with dummy loads first. Confirm the shutdown/interlock interface before UV emitter testing. |
| Routing and release | Placement done. Still route the power paths and Kelvin sense pairs, add planes and thermal vias per the fab rules, rerun full DRC, and review the fabrication package. |

For the first 405 nm bench test, use an available TPS92691 boost reference or controlled prototype. Use dummy loads with a distinct constant-voltage mode if available to exercise 32–34 V at about 600 mA. Measure input current, output voltage, current ripple, switch-node overshoot and temperatures. Begin with PWM low, then test startup and PWM step response. Verify open-load OVP and short-circuit eFuse behavior separately with current limiting and an appropriate test fixture. Use a shielded setup for tests with the actual UV emitters.

## 405 nm dummy-load validation

Run `python3 scripts/check_sim.py --uv-405` from the project root. The diagnostic uses a switched 200 kHz boost power stage with behavioral current feedback and a one-way voltage-offset load. It varies input voltage, dummy-load voltage and effective output capacitance, and measures steady current, DIM-off leakage and restart peaks. It also runs a modeled open-load cutoff and repeats the feed-through disconnect diagnostic.

The controller, loop compensation and eFuse dynamics remain separate hardware signoff items. A high transient peak in this test is a prompt for a real waveform check. The 0.65 A screening threshold is a development flag, not a manufacturer-approved pulse rating. Obtain the module pulse limit before attaching the real emitter.

Bench order for the 405 nm stage:

1. Use a current-limited 12 V supply and a suitably rated constant-voltage dummy load or LED simulator. Hold PWM low during connection. Monitor the input, boost output, LED current and eFuse output at power-up before enabling the channel.
2. Capture the first enable and a representative off/on restart at the target load. Compare peak, settling and steady current across the input range. Determine actual peak limits from the emitter's thermal and pulse ratings before using it. Check whether the controller can be enabled before the eFuse output reaches its operating rail and whether an enable interlock is needed.
3. Verify open-load OVP separately, then the physical eFuse fault path with a protected, current-limited fixture. Record clamp voltage, supply current and latch-off/reset behavior. The diagnostic's resistive fault and ideal disconnect do not substitute for a hardware short-circuit test.

### Switched-model results

Verified with ngspice 44.2. Input is held fixed and output voltage/capacitance are scenario assumptions. The dummy load stays attached until the modeled DIM or open-fault switch opens.

| Source / dummy load / effective capacitance | Steady mean | Mean after PWM restart | Startup peak | PWM restart peak |
| --- | ---: | ---: | ---: | ---: |
| 12 V / 33 V / 6.8 µF | 0.601 A | 0.600 A | 1.151 A | 1.207 A |
| 10.8 V / 34 V / 4.7 µF | 0.600 A | 0.599 A | 1.121 A | 1.642 A |
| 13.2 V / 32 V / 9.4 µF | 0.599 A | 0.600 A | 1.216 A | 1.187 A |

All cases met the 0.57–0.63 A steady/recovered band and the 10 µA RMS DIM-off check. The circuit model reached 40.32 V on open load and disabled switching in the checked interval. The feed-through diagnostic measured 4.16 A without interruption and 0.12 µA after a commanded disconnect. All modeled startup and restart peaks exceeded the development screening level, so transient validation remains open. These peaks depend on the assumed load and controller implementation and cannot be used as predictions for the TPS92691. No schematic compensation values were changed on the basis of this model.

## Prototype routing draft

The [native PCB](../uv_driver/UV_DRIVER.kicad_pcb) contains the first pass of both converter power paths, the 405 nm eFuse feed, the inner ground plane, and two bottom-layer Kelvin sense pairs that branch at the LED shunt pads. The [layer preview](../results/uv-driver-routing-preview.svg) is for design review. The [first routing-pass DRC report](../results/uv-driver-routing-drc.json) has zero rule violations, zero schematic parity issues, and 97 unrouted connections. Versioned evidence for the prior placement state remains separate.

Before releasing Gerbers, complete the controller gate drives, IS and OVP routes, references, PWM, protection housekeeping and ground stitching. After those connections are available, review the switch-loop perimeter, especially the SEPIC transfer loop, against the TI reference layout. Keep switch copper and the gate loops compact, inspect the return path for current-sense routing, and separately review copper width, current handling, exposed-pad heat paths and fabrication constraints. DRC geometry passing does not establish electrical or thermal performance.

### Prototype fabrication and assembly quote inputs

- **Physical drawing:** provisional 110 × 76 mm, four-layer, 1.6 mm board. Confirm enclosure, mounting points, connector wire access, and the manufacturer's stackup and copper options before release.
- **Fabrication files:** release Gerbers, drill files and fabrication notes only after final routing and a review of DRC, schematic parity, every copper layer and drill geometry.
- **Assembly files:** provide the approved BOM with manufacturer part numbers and do-not-fit markings, top/bottom placement files as applicable, pin-one and polarity drawings, and any instructions for through-hole connectors. Request a quote for the assembled driver PCB; list external LED heads and heatsinks separately.
- **Verification scope:** the first order would be prototype hardware for current-limited bring-up. Confirm separately whether the assembler can provide inspection or a specified electrical test. Functional UV operation requires the measured startup, protection and thermal checks already tracked above.


### Fully routed Rev B and quote package

The [Rev B PCB](../uv_driver/UV_DRIVER.kicad_pcb) now has all schematic nets connected. The remaining connections were drafted with a local router with existing power and Kelvin routes locked and In1.Cu reserved, then checked and corrected in KiCad. A top ground fill and through-vias connect the controller returns. The quote draft assumes a 0.15 mm minimum track width. Confirm it with the selected manufacturer and review the power and gate loops, copper loss, switching margins and thermal path before approving production.

KiCad 10.0.3 verified zero design-rule violations, zero unrouted connections, zero schematic parity issues, and zero ERC errors or warnings. The [quote-only archive](../results/UV_DRIVER_RevB_QUOTE_ONLY.zip) was checked for a closed 110 × 76 mm outline, four copper layers, metric drill files, 70 board BOM entries, and 64 top-side SMT placement records. The [quote brief](UV_PROTOTYPE_QUOTE.md) identifies the six through-hole parts and the remaining release checks. Hardware startup, PWM peaks and eFuse behavior remain pending measured bring-up.
