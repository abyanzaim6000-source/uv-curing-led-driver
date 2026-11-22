# UV driver Rev B engineering review

**Fabrication status: hold.** Rev B passed fresh KiCad ERC and strict PCB DRC with schematic parity. The power-stage review found issues to address before releasing the first prototype. All numerical results below are design screens. Bench bring-up is pending.

## 405 nm boost loop

Run `python3 scripts/check_uv_boost_loop.py` from the project root. The script evaluates the TPS92691 averaged boost modulator and the COMP impedance from datasheet §8.1.9. It uses 10.8–13.2 V input, 32–34 V output, 600 mA, 80–120 µH, and nominal controller gain. The sweep uses 2, 4.7 and 9.4 µF **effective** output capacitance and 2, 4, 8 and 12 Ω LED incremental resistance. The capacitance and resistance values are sensitivity assumptions pending manufacturer curves or measurement. The screen requires a single unity-gain crossing below one-fifth of the modeled right-half-plane zero and at least 45° phase margin. It only searches up to 16.5 kHz, one-tenth of the minimum switching frequency.

| Population | Corners meeting screen | Estimated crossover and phase margin |
| --- | ---: | --- |
| Rev B nominal, 10 kΩ / 2.2 nF / 100 pF | 0/96 | No crossover in the range where the screen applies. |
| Integral candidate, R206 = 0 Ω, C209 = 220 nF effective, C210 unpopulated | 96/96 | 456–716 Hz, 69–87° |

The modeled boost right-half-plane zero ranges from 7.6 to 18.1 kHz. The integral candidate gives a starting point for the next design revision. Re-run the screen after choosing the actual capacitors, LED range and switch shunt. Include component tolerance, controller sampling and PWM turn-on transients before freezing the population. Validate the response at 100% PWM with a small line step and check current settling under PWM and load changes. [TI TPS92691 datasheet](https://www.ti.com/lit/ds/symlink/tps92691.pdf).

## 365 nm SEPIC loop and output capacitors

TI’s SEPIC right-half-plane zero estimate gives about 18 kHz as a conservative screening floor using 13.6 V, 650 mA, duty up to 0.60 and 81.6 µH. The coupling-capacitor resonance estimate `1/(2π√(L₂ × C101_eff))` gives about 8.1–15.3 kHz for 54.4–81.6 µH and a sensitivity range of 2–4.7 µF. Use a provisional crossover target at or below roughly 1.3 kHz, one-sixth of the lowest resonance estimate. Rev B’s COMP zero is about 7.2 kHz. It cannot be assumed to provide useful phase boost below that target. Use a SEPIC-specific plant model including both inductors and C101 to select a starting population. Crossover and phase margin remain open for this channel. [TI SEPIC design brief](https://www.ti.com/lit/ab/slvafj6/slvafj6.pdf), [TI AN-1484](https://www.ti.com/lit/an/snva168e/snva168e.pdf).

The two output capacitors on each channel total 9.4 µF nominal. With a provisional 5% peak-to-peak LED current ripple target and 165 kHz switching, the capacitor charge balance approximation gives `Ceff ≥ D/(0.05 × fsw × rd)` before ESR and layout parasitics. This assumes CCM and neglects the reduction in LED current during the MOSFET on interval.

| Assumed LED dynamic resistance | 365 nm at duty 0.60 | 405 nm at duty 0.683 |
| ---: | ---: | ---: |
| 2 Ω | 36.4 µF | 41.4 µF |
| 4 Ω | 18.2 µF | 20.7 µF |
| 8 Ω | 9.1 µF | 10.3 µF |
| 12 Ω | 6.1 µF | 6.9 µF |

Confirm the voltage-dependent capacitance for each exact Murata part at output bias and temperature, including tolerance and aging. Confirm the LED slopes around rated current and check the allowable peak current at temperature. Size the output capacitor banks with that evidence, and retain space for additional capacitance if the lower-resistance cases are credible. Changing capacitance also changes PWM behavior and loop gain. [Murata SimSurfing](https://ds.murata.com/simsurfing/mlcc.html), [TI TPS92691 datasheet, §8.1.3](https://www.ti.com/lit/ds/symlink/tps92691.pdf).

## Switch-current headroom and thermal screening

The earlier 3.28–3.70 A estimate is a static comparator calculation. The TPS92691 duty-adjusted equation uses `Ipk = (VIS(LIMIT) − VSL × D) / RIS`. At the low comparator threshold of 497 mV, typical 200 mV ramp and +1% shunt tolerance, the usable limit is about **2.49 A for SEPIC** at duty 0.60 and **2.38 A for boost** at duty 0.683. Prior loss-inclusive peak estimates reach about 2.5 A on both channels. The ramp is a typical value, so these are margin checks and do not certify a worst-case threshold. The boost slope bound from the TI quick design equation is about 0.155 Ω at 34 V, 80 µH and 165 kHz, leaving little headroom for the 0.15 Ω part. For SEPIC, both inductor currents contribute to the switch current. Their summed down-slope requires a separate inner-loop check. Re-size the shunts and slope compensation together, then recheck the maximum fault current, eFuse interaction, pulse energy and component stress before changing the BOM. [TI TPS92691 datasheet, §8.1.8](https://www.ti.com/lit/ds/symlink/tps92691.pdf).

At 2.22 A average and roughly 0.61 A peak-to-peak ripple, the 405 nm inductor dissipates about 0.59 W winding loss using Bourns' 118 mΩ maximum 25 °C DCR. Allow for hot copper and core loss. The same screening pass puts the 405 nm switch shunt near 0.51 W under normal conditions. The rectifier, MOSFET, inductor and shunt should all be measured at sustained maximum load and checked again after the fault limits are finalized. TI recommends separate attention to the switching-node copper, low-impedance returns and exposed-pad thermal paths. [Bourns SRP1770TA datasheet](https://www.bourns.com/docs/product-datasheets/SRP1770TA.pdf), [TI TPS92691 datasheet, §10](https://www.ti.com/lit/ds/symlink/tps92691.pdf).

## Routed board review

Lengths below are sums of routed segments from the Rev B KiCad board. Switch-node totals include the inductor branch. They serve as geometry evidence, with loop inductance and temperature still requiring validation.

| Review area | Rev B observation | Action for next revision |
| --- | --- | --- |
| Switching loops | SEPIC switch and coupling nodes have 31.6 mm and 30.8 mm of top-layer routing. The SEPIC output-cap ground vias are about 38–43 mm from the switching shunt ground via. Boost has 24.7 mm of top switch-node routing, and the nearest output-cap ground via is about 23 mm from its shunt ground via. | Cluster the switches, rectifiers, shunts and output ceramic capacitors. Include C101 in the SEPIC cluster. Shorten the entire pulsed-current return path as well as the high-dv/dt node. Keep In1.Cu as a continuous ground reference. |
| Gates and sense | U1/U2 main gate routes are 29.2/22.2 mm with two vias each. IS sense branches have about 25/20 mm on In2.Cu alone. U2’s VCC route uses three vias. Each LED shunt has two bottom-layer Kelvin branches, spanning about 35–38 mm for SEPIC and 21–22 mm for boost. | Move the controllers and their VCC bypass capacitors closer to the switches and shunts. Preserve the dedicated Kelvin takeoffs and route the paired traces together, away from switch nodes. Reserve tuning pads for IS/LED sense filtering if the compact routing needs it. |
| eFuse and boost feed | C303 is 100 nF near U3. The main protected feed transitions from a 0.85 mm top track to a 1.1 mm track into L201. The SMC clamp D301 reaches that feed through about 12 mm of 0.20 mm trace including its branch across the top layer. | Put the clamp next to the protected output and its ground return with a short, wide path. Place a local ceramic bypass at the boost input. Verify power neck-downs at U3, the startup limit with C202, and the heating using the proposed fabrication stackup. |
| Exposed pads and copper | F.Cu and In1.Cu have ground fills. U1, U2 and U3 have split paste apertures and adjacent ground stitching. No stitching via is inside their exposed-pad copper. | Review short pad-to-plane thermal connections with the assembler. Confirm paste apertures, via treatment and fab copper weights. Keep additional heat-spreading copper on quiet nodes where practical. |
| Probe access and mechanics | J1 provides raw input and ground, J2 provides both PWM signals and ground, and J101/J201 provide LED terminals. Temporary clip or solder access exists at C202 for the protected rail, C103/C203 for converter output and C108/C208 for IMON. LED negative pins are switched returns. The board has no dedicated probe pads or mounting holes. | Add accessible pads with nearby ground references for both IMONs, outputs and protected input. Provide compact gate/IS/switch-node probe access where it will preserve the layout. Set mounting and wire clearances before exporting. Use a circuit-ground reference and an appropriately rated differential probe for floating measurements. |

## Verification and release sequence

- Fresh KiCad CLI checks returned zero ERC violations, zero DRC violations, zero unconnected items and zero schematic-parity issues.
- The new boost screen ran successfully with standard Python. Existing switched ngspice regressions were not rerun because ngspice was unavailable on PATH and in the checked Homebrew locations. This pass changed documentation and added the screening script.
- Before release, close current limit and slope compensation, choose effective output capacitance and the initial COMP population for each channel, and reroute the power loops and probe access. Recheck the PCB and make a matched fabrication export. Bench work starts on current-limited dummy loads before any emitter test.
