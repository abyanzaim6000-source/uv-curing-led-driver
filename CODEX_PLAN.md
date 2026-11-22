# UV curing LED driver PCB development plan

## Portfolio closeout

**Completed at the design and simulation stage.** The final milestone includes the routed Rev C1 PCB, reproducible simulations, and the verified quote package. Fabrication, measured bring-up and curing validation remain possible follow-up work.

See the [portfolio README](README.md) and [interview walkthrough](DEMO.md). Root-level legacy CAD, blank sheets, editor history and unused outputs were moved into the ignored local archive for recovery.


The owner supplied the UV curing device brief after the initial audit. This section is the active product plan. The earlier behavioral simulation records remain below for traceability.

## Product objective and completion criteria

Build, fabricate, assemble and verify a KiCad PCB for a 12 V DC UV curing device with four 365 nm emitters and one 405 nm emitter. Regulate LED current for the chosen wiring and verify idle, startup, shutdown, load changes and relevant faults. Provide a defined controller interface and a safe default-off state. Confirm whether the ESP32 and motor stage live on this PCB or connect externally. Validate temperature and input loading at the intended curing duty cycle using a shielded fixture.

Release hardware when the approved schematic passes ERC, the routed board passes DRC and schematic parity, and all relevant exceptions are documented. Check the actual fabrication and assembly package, including Gerbers, drill files, fabrication notes and BOM. Complete current-limited bring-up, dummy-load testing and supervised UV testing with measured results before calling the board functional.

## Current hardware baseline

The first [UV driver schematic](uv_driver/UV_DRIVER.kicad_sch) is in a separate KiCad project under `uv_driver/`. It draws both TPS92691 stages and has passed ERC and exported-net checks. Component ratings, compensation and fault behavior are pending. The original baseline below describes the top-level PT4115 project.

- The KiCad root schematic contains two PT4115 buck examples and a separate 12 V motor/MOSFET fragment. No LM3478 boost converter or ESP32 control circuit was found in this project. Three channel sheets are empty.
- Prior baseline ERC found seven errors and two warnings, including unconnected DIM pins, a floating motor MOSFET gate and missing PT4115 footprint configuration. Nothing has been changed in the schematic since those checks.
- The KiCad board is empty. No routed board, fabrication export, or hardware test evidence was found here.
- The prior regression validates a generic single-LED behavioral buck model at approximately 1.2 A. It offers reusable test and plotting infrastructure. It does not validate conversion from 12 V to the UV module voltages, current sharing between 365 nm modules, boost behavior, or this PCB.

## Selected emitter baseline for preliminary design

The internship brief leaves part selection to the designer. Use the following named products for schematic trade studies. The prior 30–34 V per 365 nm module estimate is superseded for this baseline.

| Channel | Candidate | Electrical inputs |
| --- | --- | --- |
| 365 nm | 4 × Broadcom AUV3-SQ62-0RT0K in series, 3535 surface mount, 60° typical viewing angle. | Datasheet at 700 mA and 25 °C junction: 3.4–4.0 V per emitter, 3.7 V typical, with stated ±0.1 V voltage tolerance. Four in series give 13.6–16.0 V at that reference point before tolerance, cold shift and wiring loss. Start driver sizing at 650 mA nominal. Keep current within the manufacturer's 700 mA DC ceiling and thermal derating limits. |
| 405 nm | 1 × TaoYuan TY-405nm20W, supplier catalog model TY-405nm-20W. | Supplier lists a 405–410 nm wavelength bin, 32–34 V forward drop and 600 mA operating current. Electrical input is 19.2–20.4 W at 600 mA. Use a 600 mA design point and a lower current for initial bench checks. Obtain the exact drawing, confirmed bin, temperature-dependent voltage, and thermal/power derating data before board release. |

Sources: [Broadcom datasheet](https://docs.broadcom.com/doc/AUV3-Sxx2-0xx0K-3W-3535-SMT-UV-LED-DS), [DigiKey India listing](https://www.digikey.in/en/products/detail/broadcom-limited/AUV3-SQ62-0RT0K/13693502), [TaoYuan product sheet](https://www.ledwv.com/uv/uv-leds-c-19/uv-led-405nm-20w-p-638.html).

For preliminary budgeting only, using the 365 nm 700 mA voltage table as a proxy at the lower 650 mA setpoint gives about 28–31 W of total LED electrical power and 2.6–3.0 A from a nominal 12 V supply at assumed 85–90% efficiency. This excludes the motor, controller and startup allowance. The voltage figures are starting analysis points. Actual driver compliance limits require hot/cold and tolerance checks.

The first schematic design uses **two independently enabled TPS92691 channels**. Use SEPIC at 365 nm and boost at 405 nm. See the [first power-stage design pass](docs/UV_POWER_STAGE.md) for the current calculations, assumptions and remaining schematic checks. The 365 nm string and 405 nm module have different voltage needs. Compare that approach with the provisional shared 38 V rail and compatible buck current stages. Check whether the hot 365 nm string voltage can approach or drop below maximum input voltage. If it can, a boost-only channel cannot regulate throughout the required range and a buck-boost or suitable shared-bus stage is needed. Keep the 405 nm supplier bin and thermal characterization as explicit gates before fabrication.

## Electrical decisions before schematic freeze

| Decision | Why it gates the design |
| --- | --- |
| Identify the 365 nm and 405 nm emitters | Collect exact part numbers or supplier documentation and verify voltage at operating current, temperature limits and rated current. Part numbers and rated voltage/current remain provisional. If documentation is unavailable, plan controlled characterization with an appropriate heatsink, current limit and shielded fixture. |
| Select 365 nm wiring and regulation | Four genuine 30–34 V modules in series would need 120–136 V before regulation headroom, so a 38 V rail cannot drive that string. If the modules are individually 30–34 V and use a shared rail, evaluate one regulated branch per module or a validated current-balancing scheme. A single shared current setting will not guarantee safe current in each parallel module. |
| Choose the voltage architecture | A 38 V shared bus plus compatible constant-current stages is one candidate. Direct constant-current step-up stages are another. Estimate cold LED forward voltage, required headroom, peak switch voltages and fault behavior before picking a bus. The PT4115 datasheet specifies a 6–30 V operating input, ruling it out for direct use on a 38 V bus. The LM3478 is a candidate boost controller and requires an external switching power stage. The attached brief does not establish its operating values or stabilization network. |
| Size the 12 V source and confirm controller scope | At provisional 30–34 V, four 100 mA modules plus one 600 mA module total 30–34 W. At the nominal 32 W and assumed 85–90% end-to-end efficiency, LEDs alone would draw about 3.0–3.1 A from 12 V. Measure motor running and starting/stall current if it shares the source. Specify controller pins, fault behavior, and whether motor and ESP32 are on-board or external. |

Source for the PT4115 operating range: the locally available UMW PT4115 datasheet. Boost-controller reference: [Texas Instruments LM3478 datasheet](https://www.ti.com/lit/ds/symlink/lm3478.pdf).

## Critical path and remaining work

| Gate | Deliverable and verification |
| --- | --- |
| 1. Requirements and topology | Confirm emitters, wiring, desired cure duty cycle, current targets, source and board interfaces. Compare viable supply/current-regulation options and freeze one architecture. |
| 2. Schematic and validation | Design input and boost or direct step-up stages, current regulation for every branch, enable/PWM interface, default-off behavior, overcurrent and thermal handling. Select actual orderable parts, confirm ratings and footprints, and validate nominal/startup/open-load behavior and simultaneous operation with the chosen power design. |
| 3. PCB and release | Route power and sense paths intentionally, account for heat, add connectors and bring-up test points, review clearances and manufacturer rules, run ERC/DRC, and inspect Gerber and drill outputs. Generate BOM and assembly files if required. |
| 4. Fabricate, assemble and bring up | Order after design review. Bring up the supply and current loops on dummy loads first, then verify the UV channels in a shielded setup. Measure voltage, current, ripple, efficiency and temperatures, including operation with the motor if applicable. Record fixes for the next revision if needed. |

## Delivery path without lab access

The owner worked remotely during the internship and has no bench access now. The deliverable is a PCB built around two commercial TPS92691 controller ICs. Custom silicon fabrication is outside the project scope.

1. **Design for review.** Complete and verify the routed KiCad board, design calculations, documented simulations, and a short presentation. This is a shareable engineering deliverable before ordering anything. Identify simulated and unverified behavior in the presentation.
2. **Assembled prototype for demonstration.** After a prototype design review, corroborate part ratings and ordering choices and generate Gerbers, drill files, BOM, placement files and assembly notes. Consider board fabrication plus assembly together because the controller and eFuse use exposed-pad packages. Quote the driver board and any manually fitted parts separately. LED heads and heatsinks are separate from board assembly. Publish prototype files only after approval and mark the hardware as awaiting bring-up.
3. **Functional proof as a separate milestone.** Arrange one-off access to a lab or electronics technician for current-limited dummy-load bring-up and captures. An assembly order alone does not establish functional testing. If access cannot be arranged, present the assembled prototype and simulation evidence with measured operation left open. Demonstrate UV curing only after the electrical, thermal and shielding checks.

Proceed with routing under the documented provisional assumptions. Keep deliberate rework access around COMP, current programming, PWM and input protection. Include probe points for input, protected rail, both outputs, PWM and current monitoring where feasible. Check current paths, capacitor DC-bias derating, component stress and cooling, startup precautions and all manufacturability checks before signing off a first prototype order. Treat measured startup, PWM peaks and short-circuit response as bring-up gates for claiming functional hardware.

## Work to finish while purchasing is deferred

The quote-only Rev B archive rechecks cleanly and can support a budget estimate. The owner is deferring purchases, so use this time to prepare a single reviewed prototype revision and matching order files. No procurement is needed for the design work below.

| Priority | Task | Done when |
| --- | --- | --- |
| 1 | Close the schematic and BOM review | Assign orderable parts or approved generic specifications to every line. Check voltage, tolerance, power, temperature ratings, footprints and substitutions. Resolve the 12 explicitly provisional placements in the quote BOM, including both channels’ soft-start, COMP, OVP filter and switch-sense parts. Use effective output capacitance and the best available LED dynamic-resistance data for compensation. Record any bounded assumptions that need first-article tuning. |
| 2 | Review the PCB as a switching power board | Inspect switching and gate loops, Kelvin sense routing, ground return, eFuse feed and copper heating. Review exposed-pad thermal paths and assembly process. Add or designate accessible probe points for input, protected rail, both outputs, PWM and current monitor. Resolve connector wire access and mounting. The current board has no enclosure mounting holes and no dedicated test-point footprints. |
| 3 | Prepare the first prototype order package | Confirm fabrication and assembly constraints, especially the four-layer stackup, 0.15 mm minimum trace, drill/annular rules and exposed-pad stencil. Re-export a matching schematic/PCB, Gerbers, drill files, BOM and placements after changes. Re-run strict ERC, DRC and schematic parity and inspect the layers and assembly data. Prepare a prototype order checklist with quantities, approved substitutions and the six through-hole parts. |
| 4 | Prepare bring-up and presentation evidence | Keep the dummy-load test worksheet and simulated results ready. Prepare a short explanation of what the PCB does, what was simulated and which measurements remain open. |

**BOM review in progress.** The [Rev B sourcing review](docs/UV_REV_B_BOM.md) covers all 70 placements and records first-article decisions for the 12 provisional positions. Remaining before release are the compensation and component margin calculations, the switching-layout review, and a matched fabrication export. Procurement and bench validation remain pending.

**Engineering review complete, corrections pending.** The [Rev B engineering review](docs/UV_REV_B_ENGINEERING_REVIEW.md) documents boost loop screening, provisional SEPIC bounds, reduced switch-current margin and measured routing geometry. Close the electrical values and shorten the power loops before the first prototype export.

Once those reviews are complete, the user can approve a small fabrication-and-assembly order when budget permits. Procurement and measured bring-up are separate milestones. On arrival, start with dummy loads and a current-limited source. Measured operation and the UV emitter thermal and shielding checks are required for a functional claim, even when the order itself was ready earlier.

**Rev C sizing drafted.** The [Rev C sizing note](docs/UV_REV_C_SIZING.md) records the candidate shunts, larger output banks and a revised boost COMP starting value. The switched SEPIC model reproduces the growing mode with separate inductors. Both catalog-based coupled candidates cleared the modeled sweep. Carry forward the 47 µH Coilcraft MSD1583T-473MED and 0.120 Ω SEPIC shunt into a Rev C draft. The pin map is verified. Hot saturation and fault turn-off remain validation gates. The 405 nm transient and both channels’ ripple and fault margins remain open before schematic and layout signoff.

**Rev C KiCad draft started.** Open [the draft project](uv_driver/rev_c/UV_DRIVER.kicad_pro). The 365 nm schematic replaces L101/L102 with the coupled MSD1583T-473MED. Both switch shunts are 0.120 Ω. The draft adds four 47 µF hybrid capacitors and the initial integral COMP population. KiCad reported zero ERC errors and warnings. A Rev B/Rev C netlist comparison verified the four winding nets and preserved the other connections. The new local footprint exported successfully and its pad numbering and dimensions were checked against Coilcraft’s drawing. The routed Rev B project is the layout reference. The Rev C boost power-component screen lowered the low-line restart peak from 1.64 A to 1.03 A, with 1.18 A at high line. The follow-up datasheet-sequenced screen found up to 0.669 A restart current and identified longer soft start as a cold-start tuning option. Hardware transient and effective COMP capacitance validation remain open. The [Rev C PCB](uv_driver/rev_c/UV_DRIVER.kicad_pcb) has 73 footprints and is fully routed. The [routing check](results/uv-driver-rev-c-routing-drc.json) reports zero rule violations, unconnected items and schematic parity issues. The [engineering notes](docs/UV_REV_C_SIZING.md) record the probe map using existing pads, ground vias and outstanding gate, thermal and mechanical checks. Review fabrication constraints and electrical margins before creating the Rev C order package.

**Rev C quote package verified.** The [Rev C release review](docs/UV_REV_C_RELEASE_REVIEW.md) checks a published 1 oz outer, four-layer reference process and records the remaining supplier, thermal, source and current-margin decisions. The [Rev C quote-only archive](results/UV_DRIVER_RevC_QUOTE_ONLY.zip) includes nine Gerbers, separate drill files, 65 SMT placements, a BOM covering 73 sites and fresh clean ERC/DRC evidence. C110/C210 are excluded from both placement and stencil. Confirm the operating-current population and supplier DFM before issuing the order package.

**Rev C1 first-prototype population drafted and verified.** Fit R110 = 8.06 kΩ for 579 mA nominal, R210 = 12.4 kΩ for 501 mA nominal and C207 = 220 nF for slower 405 nm cold start. The [C1 prototype note](docs/UV_REV_C1_PROTOTYPE.md) records the selected population, simulation results and bench limits. The [C1 quote package](results/UV_DRIVER_RevC1_QUOTE_ONLY.zip) matches the active KiCad files and supersedes Rev C for first-prototype quoting. Supplier DFM, sourcing and hardware checks are open.

### Final workspace cleanup

- Preserve the Rev C draft under `uv_driver/rev_c/`, its project libraries, the routed Rev B baseline while Rev C is in development, and the release BOM, Gerbers, drills and verification reports that match the approved board.
- Candidates for removal are the root-level empty board `LED_DRIVER.kicad_pcb`, the three root-level `channel*.kicad_sch` files with empty symbol tables and no circuit, root and active KiCad `.kicad_prl` local settings, `.DS_Store` and `scripts/__pycache__/`. No zero-byte regular files were found in the workspace inventory to depth three.
- The root `LED_DRIVER.kicad_sch` contains real legacy design data. Archive it with its project settings and any dependent files if it is out of portfolio scope. The old simulation decks, exported traces and figures still support `README.md`, `DEMO.md` or recorded checks. Update those references before removing or moving them.
- Review intermediate renderings and reports only after the new package exists. Preserve the old quote ZIP and KiCad's `.history/` until there is a verified backup or explicit approval to remove them. Present the exact deletion list at final cleanup before deleting anything.

## Remaining-access schedule

- **First remaining week:** Identify parts and freeze topology. Start the fabricable schematic as soon as the load and supply are confirmed.
- **Second remaining week:** Finish schematic, component selection and power-stage validation. Begin layout once the review passes.
- **Third remaining week:** Route, verify and export the fabrication package if design gates are met. Fabrication, shipping, assembly and bench bring-up are external milestones and may extend beyond Codex access.

## Active progress

- [x] Read the actual UV curing project brief and checked it against the current KiCad source.
- [x] Identify the PT4115/38 V mismatch and the 365 nm series-string conflict.
- [x] Select catalog emitter candidates and define preliminary electrical loads.
- [ ] Confirm 405 nm sample bin, thermal data and mechanical drawing, and obtain the actual 12 V supply rating and tolerance.
- [ ] Confirm control and motor boundaries and intended board fabrication method.
- [x] Select first-pass power topology and size LED sense and magnetics candidates.
- [ ] Verify first-pass assumptions and freeze the schematic design after component and protection review.
- [x] Draw Rev A SEPIC and boost stages, with independent PWM inputs, LED return disconnects, switch shunts and OVP networks. Verify ERC and exported connectivity.
- [x] Calculate static switch-current and overvoltage trip ranges for the proposed Rev A values.
- [x] Assign principal power-component candidates and footprints, add the 405 nm latch-off input eFuse in Rev B, and verify ERC, netlist and simplified fault path.
- [x] Create preliminary four-layer placement for 70 footprints. Placement DRC found zero physical violations and zero schematic mismatches, with 148 unrouted connections.
- [x] Route initial power and Kelvin-sense paths and fill an inner ground plane. Current DRC has zero physical violations and schematic mismatches, with 97 unrouted connections. Record [quote inputs](docs/UV_POWER_STAGE.md#prototype-fabrication-and-assembly-quote-inputs).
- [x] Complete Rev B routing. Final KiCad DRC has zero violations, unconnected items and parity mismatches. Export [the quote-only ZIP](results/UV_DRIVER_RevB_QUOTE_ONLY.zip) and record verification in the design notes.
- [x] Audit the quote archive. Confirm 70 BOM entries, 12 explicitly provisional placements, and clean saved DRC and parity. Record the pre-order work sequence.
- [ ] Complete the manufacturer DFM review, resolve the order BOM, confirm mechanics and review switching-loop/thermal design before approving prototype fabrication.
- [x] Simulate passive boost precharge with PWM disabled and record placement and electrical release gates.
- [x] Run the switched 405 nm dummy-load simulation at three modeled operating points and record open-load and feed-through results. The behavioral model flags startup and PWM restart peaks for bench review.
- [x] Prepare the [405 nm bench worksheet](docs/UV_405_BENCH.md), including a lower-current EVM baseline and the first two scope captures.
- [ ] Obtain an assembled reference or prototype and instruments. Validate actual TPS92691 startup/PWM peaks and compensation, review bias/thermal limits and test the physical eFuse path before functional hardware signoff. Prototype routing and release preparation can proceed with these tests tracked.
- [ ] Fabricate, assemble and bench validate.

---

# Prior behavioral demonstration record

The following material describes the earlier generic buck study and its historical roadmap. The active fabrication work follows the UV PCB plan above.

## Intended design

A dual-channel hysteretic buck LED driver IC. Each channel senses the voltage from VIN to CSN across its external sense resistor, turns the power switch off at the upper trip point and on at the lower trip point, and allows DIM to override switching. Each channel has an external inductor, catch diode and LED load. The handover calls for a high-side sense amplifier, hysteretic comparator, DIM logic, level shifter and tapered gate driver, and LDMOS switch. A shared 1.25 V reference feeds the threshold generation. A ground-referenced switch and independent DIM inputs are proposed for the model and need a pin and topology review.

Handover targets are 6–30 V input, 1.2 A nominal average current (working interpretation), 85/115 mV trip points, DIM below 0.3 V forcing the switch off, gate edges under 20 ns with the intended load, and switch on-resistance at most 0.4 Ω. At 1.2 A the ideal sense resistor is about 83.3 mΩ, giving nominal 1.02–1.38 A current thresholds. Propagation delay and parasitics can move the actual extrema. The standalone design procedure was unavailable for independent confirmation, so these targets are traced to the handover transcription.

## Current baseline

| Area | Verified finding |
| --- | --- |
| Workspace | No top-level Git repository. KiCad’s nested `.history/.git` contains automatic snapshots. The project settings parse as JSON. There is no README, checked-in test suite, SPICE source, dependency manifest, or project-local PDK setup. |
| Schematic | The root contains two commercial PT4115 circuits and a separate 12 V motor/MOSFET fragment. Each PT4115 branch wires VIN → 0.13 Ω shunt → LED → 68 µH inductor → SW, with a Schottky return from SW to VIN. Both use a shared net named `6-30V`, two bridge-like source sections with 1 V sine sources and distinct return nets, and open DIM pins. The second source wiring warrants review if this prototype is reused. Three named channel sheets are empty. The shunt value differs from the IC target and the sources do not exercise its input range. |
| IC implementation | No custom sense amplifier, comparator, DIM logic, gate driver, power switch model, reference, closed-loop testbench, or PVT results found. The KiCad circuit is useful as a topology reference and needs its own validation if developed further. |
| ERC | KiCad 10.0.3, exit 5. Seven errors and two warnings. Q1 gate and both DIM pins are open, three power-input nets have no recognized driver, and both ICs lack a configured PT4115 footprint library. The Q1 gate produces two errors. Simulation-model ERC is disabled in the project. |
| Exports | XML connectivity export succeeded with an annotation warning. Source and SPICE export confirm duplicate `Rs`, `L` and `Cin` designators. SPICE export initially failed on cache access. With cache access it exited zero and produced a deck with incomplete PT4115 and other device lines, repeated element names, and no analysis command. It cannot serve as the baseline simulation. |
| PCB | The board is an empty KiCad stub. DRC on the temporary copy exited 134 without a report. Board validation remains unavailable. |
| Tests and environment | No project tests to execute and no successful circuit simulation. macOS arm64, Python 3.11.8, NumPy 2.4.6 and KiCad 10.0.3 available. KiCad bundles an ngspice shared library. Standalone ngspice, pytest and matplotlib were unavailable in the checked local environment. Virtuoso/Spectre and an appropriate HV PDK were not confirmed. |

## Completion criteria for the portfolio release

- A clean checkout can regenerate simulations, automated pass/fail results and the main plots using documented tool versions and one command.
- A nominal single channel and then two channels regulate within agreed thresholds and current tolerances at 6, 12, 24 and 30 V with a declared LED load and inductor. Report conditions where LED headroom prevents regulation.
- Each channel starts, turns its switch off under DIM override, and resumes predictably. PWM dimming and simultaneous or independent operation are demonstrated. Analog dimming needs a defined transfer function before validation.
- Measured results include steady-state average and extrema of LED current, sense thresholds, and switching frequency. The results state which blocks are behavioral and which use characterized transistor models.
- A public-ready README and demo show the circuit, setup, test commands, waveforms, results and limitations. If included, IC-level claims about 20 ns edges, 0.4 Ω, PVT or layout each have corresponding evidence.

## Original Week 1 milestone status

The implementation milestone from the audit is complete. The single-channel behavioral loop runs in batch, with nominal waveforms and passing current-regulation checks at all four input voltages. The dual-channel, dimming and headroom regressions are also in place.

The original scope decisions remain open. The model assumes a ground-referenced switch, a nominal single LED, independent DIM inputs and 1.2 A per channel. The final pinout and real load and supply requirements still need confirmation. No suitable HV PDK is confirmed, so the reproducible demo uses the behavioral scope while those decisions remain open.

## Open decisions

| Decision | Working choice for the portfolio demo | What would close it |
| --- | --- | --- |
| Deliverable | Demonstrate the reproducible behavioral driver. Use the existing PT4115 sheet as a topology reference. | Owner confirms whether a PT4115 PCB or custom transistor-level block is also a deliverable. |
| Real load and source | Use the simplified single LED and documented source and decoupling assumptions. Treat 1.2 A as the nominal average target per channel. | Select an LED or string and obtain forward voltage versus current and temperature. Define minimum voltage at the driver pins, source droop, and allowable current error. Re-run the 6 V headroom cases with those values. |
| Pins and dimming | Logical interface uses shared VIN and GND, with separate CSN, SW and DIM for A and B. DIM below 0.3 V disables switching. The demonstrated dimming mode is PWM. | Confirm the interface, supply domains, and whether analog dimming is required. If required, define its input-to-current transfer and acceptance limits before implementing it. |
| Process and transistor scope | Use behavioral sensing, switching and thresholds for the release. | Confirm a locally accessible simulator and PDK with suitably rated HV devices, usable models, and permission to share public results. Then choose one block to characterize first and lock the reference and gate-drive requirements. |

The demo can be finished under the working choices. The most useful owner inputs are the intended LED or string and any PDK or Virtuoso access already available. The source design procedure can settle pinout and DIM questions if it specifies them.

## Priorities and remaining three weeks

| Week of access | Priority and work | Exit evidence |
| --- | --- | --- |
| 2 | **P0** Confirm the pinout, LED headroom and DIM contract. Establish a portable batch run and keep automated assertions for the single channel. **P1** Add the second channel and independent DIM tests. Time-box the HV PDK decision within this week. | Repeatable run for both channels at 6, 12, 24 and 30 V, with DIM override and recovery. |
| 3 | **P1** Run load and passive tolerance sweeps, verify PWM behavior and shared-supply interaction, and generate plots. Spend time on a transistor-level block only if suitable models are already available and core tests are stable. | Measured results and reproducible sweep report. |
| 4 | **P1** Fix regressions, reproduce results from a clean workspace, and finish README, architecture drawing, demo and measured resume bullets. Review Git contents when the owner is ready. | Reproducible demonstration and documented scope. |

## Initial single-channel results

`spice/single_channel.cir` implements high-side sensing, a hysteretic ground-referenced switch, and a DIM override. The starting assumptions are an 83.33 mΩ shunt, 68 µH inductor, 0.4 Ω on-state switch resistance, ideal DC supply and an approximate single LED. The switch model has ideal threshold behavior. At 27 °C, under the assumed load, a 1 ms transient gave these steady-state readings.

| VIN | Average LED current | Current valley–peak | Switching frequency |
| --- | --- | --- | --- |
| 6 V | 1.1999 A | 1.020–1.380 A | 58.8 kHz |
| 12 V | 1.1991 A | 1.021–1.380 A | 102.7 kHz |
| 24 V | 1.1987 A | 1.021–1.380 A | 124.6 kHz |
| 30 V | 1.1993 A | 1.020–1.380 A | 129.0 kHz |

All four runs reached 1.02 A within 25 µs from zero initial inductor current. Halving the maximum timestep at 12 V shifted average current by about 0.32 mA. A separate 12 V run drove DIM to 0.2 V, verified switch-off control throughout the off interval, checked that the current decayed below 10 µA, and measured 1.1985 A after recovery.

These initial measurements used KiCad’s bundled ngspice 44.2 and a temporary Python harness. The revised shared model adds an assumed 100 pF switch-node capacitance to resolve convergence during dual-channel switching.

## Current regression

Run `python3 scripts/check_sim.py` from the project root with Python 3.9 or newer. The script uses standalone `ngspice` on PATH if present or the standard KiCad macOS installation’s bundled library. Use `--library PATH` to select an alternate shared library. Verified with the bundled ngspice 44.2 backend. The standalone backend remains unverified locally.

- At 6, 12, 24 and 30 V, both channels passed the average-current checks when enabled together. Turning either channel off held its current below 10 µA RMS after decay, and the other averaged between 1.1987 A and 1.2040 A. Both recovered after DIM was released.
- At 12 V and 1 kHz PWM, 10%, 50% and 90% duty produced 0.1310 A, 0.6089 A and 1.0869 A average LED current.
- At 6 V with the approximate LED model, an added 2.0 V of forward drop yielded 1.2214 A and exceeded the provisional 1.18–1.22 A regression band. An added 2.5 V reduced current to 1.0564 A. This is a headroom sensitivity sweep relative to the model’s base LED drop. This sweep uses an ideal source. A separate shared-supply regression models the feed and input decoupling.
- The nominal checks also cover startup and a 12 V timestep comparison. The channel and deck files can be explored directly with `ngspice -b dual_channel.cir` or `ngspice -b single_channel.cir` from the `spice` directory.

## Shared-supply and passive tolerance results

The dual-channel regression adds an assumed 100 mΩ feed resistance, 200 nH feed inductance, and 100 µF input capacitor with 50 mΩ series resistance. The capacitor starts charged so this test measures switching and DIM interactions during operation.

| Source | Local input range | Largest change in the other channel’s average current when one channel turned off |
| --- | --- | --- |
| 6 V | 5.777–5.967 V | 6.0 mA |
| 12 V | 11.829–11.995 V | 3.9 mA |
| 24 V | 23.851–24.032 V | 1.8 mA |
| 30 V | 29.854–30.058 V | 1.3 mA |

At 6 V and 30 V, eight combinations of inductor ±20% and shunt ±1% produced 1.1880–1.2125 A average current and 48.5–162.5 kHz switching frequency. These are separate passive and shared-supply sweeps with the approximate single LED. At 30 V with 54.4 µH and the +1% shunt, a 50 ns timestep ceiling materially changed the simulated average current. The new sweeps use a 10 ns ceiling and the regression checks that tightening this corner to 5 ns changes the mean by less than 5 mA.

## Combined low-input results and waveform exports

At a 6 V source, 12 cases combine the assumed shared feed and decoupling with ±20% inductor and ±1% shunt endpoints on both channels. Channel B uses the nominal LED model. Channel A uses the same model plus a 0, 2.0 or 2.5 V series drop. The table reports average current during 90–190 µs with both channels enabled.

| Extra LED drop on A | Channel A average | Channel B average |
| --- | --- | --- |
| 0 V | 1.1855–1.2140 A | 1.1855–1.2140 A |
| 2.0 V | 1.0778–1.2660 A | 1.1869–1.2141 A |
| 2.5 V | 0.6116–0.7114 A | 1.1880–1.2144 A |

All 12 cases passed the DIM isolation and nominal-channel checks. At +2.5 V, A remains current-limited by headroom under the modeled conditions while B continues switching. The +2 V results show strong sensitivity to the load and passive assumptions over the sampled interval. These results do not establish a universal LED forward-voltage limit.

Run `python3 scripts/check_sim.py --export-dir results` with Pillow 10.1 or later to regenerate both 100 ns-spaced waveform CSVs, the 12-case summary and the PNG figure. The waveform files include local input voltage, both DIM voltages and both LED currents. `results/6v-waveforms.png` is the presentation figure derived from the two waveform CSVs. Its nominal traces initially overlap because the two modeled channels start together with identical parameters.

## Testing strategy

1. Run a simulator smoke test, then a nominal transient in batch mode. Fail the regression for simulator errors, missing or nonfinite measurements and missing switching cycles, even if the process exits zero.
2. Ramp the sensed voltage through both thresholds and measure trip points and delay. Run 1 ms as an initial system test where sufficient, measure after startup across several complete cycles and tighten the timestep to check numerical sensitivity. Compare average, valley and peak current against agreed limits.
3. At 6, 12, 24 and 30 V test startup, steady-state operation and DIM override/recovery. Test representative PWM duty cycles, including short pulses relative to startup time. Check immediate switch disable and eventual LED-current decay through the freewheel path. Verify the other channel remains in regulation when DIM changes.
4. Sweep declared LED forward voltage, inductor and shunt tolerances. With characterized models, add -40/27/125 °C and applicable TT/FF/SS corners, common-mode gain/offset, switch stress and on-resistance, and 10–90%/90–10% driver transitions into the verified gate load. Label behavioral parameter sweeps as sensitivity studies.
5. Run targeted checks after each meaningful edit and the full regression before the demo. If the KiCad prototype is included, give it unique designators and portable libraries, review power and DIM wiring, rerun ERC, and validate its exported models. Board DRC applies once a board exists.

## Risks and scope cuts

- **Critical path:** freeze topology and load assumptions → establish batch simulation → prove one closed-loop channel → verify dual-channel DIM and operating range → package reproducible results.
- **HV models and access:** a model must support actual device stress, including SW rising above VIN during freewheel. The current release target is the behavioral demo. Revisit transistor-level scope if supported models and access are confirmed.
- **Operating range:** a load that needs too much forward voltage can lose regulation at 6 V. Switch and series losses further reduce available headroom. At high VIN, propagation delay can push peak current above its intended threshold. Verify both ends early.
- **Time cuts, in order:** IC layout/DRC/LVS/PEX, transistor-level bandgap, full transistor-level integration and full process-corner coverage, KiCad PCB work, analog dimming, and elaborate video or visuals. Keep dual-channel regulation, PWM/override, measured results and reproducibility as release priorities.

## Progress tracker

- [x] Read handover, inventory workspace, inspect project settings and exported connectivity.
- [x] Run KiCad ERC and netlist exports on scratch copies, attempt DRC, and check local tools.
- [x] Record baseline, discrepancies and proposed roadmap.
- [ ] Review prototype role, original procedure if available, and acceptance limits with owner.
- [ ] Verify repeatable ngspice setup and close the PDK decision.
- [x] Verify nominal single-channel regulation at four supply points, ideal startup, DIM override/recovery, and a timestep comparison.
- [x] Persist the supply and DIM regression and verify it with bundled ngspice.
- [ ] Verify the standalone ngspice backend in a clean environment.
- [x] Pass nominal dual-channel and independent DIM checks at all four supply points.
- [x] Run a first PWM and low-VIN LED drop sweep.
- [x] Verify modeled common supply impedance and decoupling at four input voltages, and sweep inductor and shunt tolerances at 6 V and 30 V.
- [x] Run combined 6 V headroom, source impedance and passive cases, and export waveforms and the summary.
- [ ] Confirm real LED and source assumptions before using simulated headroom as an operating limit.
- [x] Generate first sweep outputs and waveform figure.
- [x] Add a project README with setup, model scope, waveforms and measured results.
- [x] Verify the regression and all three CSV exports from a fresh temporary directory using Python 3.11.8 and bundled ngspice 44.2. The regenerated CSVs matched byte for byte.
- [x] Write the three-minute demo walkthrough and regenerate the presentation figure in the export command. A fresh-directory run using Pillow 12.3.0 and bundled ngspice reproduced all four outputs byte for byte.
- [ ] Review Git contents and publication with owner.

Record evidence, blockers and the next action here after each milestone. The reusable regression passes via the bundled simulator. A clean standalone verification run is pending. Full transistor-level verification depends on suitable HV models and access.
