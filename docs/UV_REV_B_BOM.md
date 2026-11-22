# Rev B prototype sourcing review

Use this list to prepare a cart and review substitutions. Quantities are per board and exclude spares. The existing [quote archive](../results/UV_DRIVER_RevB_QUOTE_ONLY.zip) remains the reference for placement and footprint data. Release of the prototype order requires the checks below. Stock, pricing and assembler-approved substitutes are pending.

**Follow-up review:** The [engineering review](UV_REV_B_ENGINEERING_REVIEW.md) supersedes the initial switch-shunt and compensation carry-forward decisions. Keep those parts and the output-capacitor banks on hold for the next design revision.

## Board BOM

Generic resistors are 0603, 1%, ≥0.1 W at rated conditions, ≤100 ppm/°C and ≥50 V working voltage unless specified otherwise. Generic capacitors are 0603 and ±10% unless specified. Verify the chosen manufacturer's land pattern, derating and availability before locking the cart.

| References | Qty | Candidate or minimum specification | Review |
| --- | ---: | --- | --- |
| C101, C103, C104 | 3 | Murata GRM32ER71H475KA88L, 4.7 µF, 50 V X7R, 1210 | Check coupling-capacitor RMS current and effective capacitance under bias. |
| C102, C202 | 2 | Panasonic EEU-FR1V101, 100 µF, 35 V, radial Ø8 mm, 3.5 mm pitch | Check input ripple and polarity. Through-hole. |
| C105, C205, C302, C303 | 4 | 100 nF, 50 V X7R | Generic. |
| C106, C206 | 2 | 2.2 µF, ≥16 V X7R | VCC bypass. Check effective capacitance near 7.5 V and consider a 4.7 µF candidate in the same footprint if needed. |
| C107, C207 | 2 | 100 nF, 50 V X7R | Provisional soft-start population. |
| C108, C208 | 2 | 1 nF, 50 V C0G | Generic. |
| C109, C209 | 2 | 2.2 nF, 50 V C0G | COMP tuning. |
| C110, C210 | 2 | 100 pF, 50 V C0G | COMP tuning. |
| C111, C211 | 2 | 100 pF, 50 V C0G | Provisional OVP filter population. |
| C203, C204 | 2 | Murata GRM31CC72A475ME11L, 4.7 µF, 100 V X7S, 1206 | Check effective capacitance across normal load and OVP voltages. |
| C301 | 1 | 47 nF, 50 V X7R | Verify eFuse startup with the boost input bulk capacitor. |
| D101, D201, D301 | 3 | Diodes Inc. B5100C family, 100 V, 5 A Schottky, SMC | Confirm exact packaging suffix. Review rectifier heat and eFuse clamp pulse. |
| D102, D202 | 2 | Texas Instruments LM4040B25IDBZR, 2.5 V, SOT-23 | DBZ pin 1 cathode, pin 2 anode, pin 3 floating or tied to anode per TI. Rev B leaves pin 3 floating. |
| J1, J101, J201 | 3 | Phoenix Contact 1715721, 2 positions, 5.08 mm pitch, horizontal wire entry | Through-hole. Check wire access in the enclosure. |
| J2 | 1 | Samtec TSW-103-07-G-S, 1×3 straight 2.54 mm header | Through-hole. Include mating cable in the bench kit. |
| L101, L102 | 2 | Bourns SRP1770TA-680M, 68 µH | Check hot saturation headroom and copper loss. |
| L201 | 1 | Bourns SRP1770TA-101M, 100 µH | Check saturation and heating at the high trip corner. |
| Q101, Q102, Q201, Q202 | 4 | Infineon IRLR3410TRPBF, 100 V, DPAK | Check switching loss, heat and overshoot margin. |
| R101, R201 | 2 | 0.22 Ω, 1%, 1210, ≥0.5 W. Candidate Vishay RCWE1210R220FKEA | LED current sensing. Review TCR and pad layout. |
| R102, R202 | 2 | 0.15 Ω, 1%, 2512, 1 W. Candidate Vishay WSL2512R1500FEA | Provisional switch shunt. Check pulse load and copper temperature. |
| R103, R107, R203, R207, R304 | 5 | 100 kΩ | Generic. |
| R104, R204 | 2 | 40.2 kΩ | Generic. |
| R105, R205, R303 | 3 | 10 kΩ | Generic. |
| R106, R206 | 2 | 10 kΩ | COMP tuning. |
| R108, R301 | 2 | 6.04 kΩ | Generic. |
| R109, R209 | 2 | 6.8 kΩ | Generic. |
| R110 | 1 | 4.99 kΩ | Generic. |
| R111, R211 | 2 | 20.0 kΩ | Generic. |
| R208 | 1 | 3.24 kΩ | Generic. |
| R210 | 1 | 7.15 kΩ | Generic. |
| R302 | 1 | 33 kΩ | Generic. |
| R305 | 1 | 15 kΩ | Generic. |
| U1, U2 | 2 | Texas Instruments TPS92691PWP, HTSSOP-16 exposed pad | Review stencil and thermal-pad assembly. |
| U3 | 1 | Texas Instruments TPS26630RGER, VQFN-24 exposed pad | Review stencil and thermal-pad assembly. |

70 placements total, including 64 SMT and six through-hole. See the [power-stage notes](UV_POWER_STAGE.md) for the principal power-component datasheets. [TI LM4040 datasheet](https://www.ti.com/lit/ds/symlink/lm4040.pdf), [Samtec header](https://www.samtec.com/products/tsw-103-07-g-s), [Phoenix terminal block](https://www.phoenixcontact.com/gb/products/1715721), [Vishay RCWE](https://www.vishay.com/docs/20019/rcwe.pdf), [Vishay WSL](https://www.vishay.com/docs/30100/wsl.pdf).

## Review of the 12 starred placements

| References | First-article decision | Release or test condition |
| --- | --- | --- |
| C107, C207 | Retain 100 nF as the starting soft-start value. TI uses 100 nF in a reference design with an approximately 8 ms target. | Check startup current and overshoot with PWM high and low. Rev B's total ramp depends on the converters, load and eFuse behavior. |
| C111, C211 | Retain 100 pF C0G as the starting OVP filter. Divider Thévenin resistance gives approximately 0.57 µs at 365 nm and 0.31 µs at 405 nm, ignoring parasitics. | Calculate transient headroom against OVP threshold spread and check trip, overshoot and restart with an open load. |
| R102, R202 | Retain 0.15 Ω, 1%, 1 W as the starting switch shunt. The comparator and resistor tolerances give a 3.28–3.70 A static trip range. | Screening gives approximately 0.29 W SEPIC and 0.51 W boost in normal steady operation using the estimated input currents, duty and inductor ripple. About 2 W can occur instantaneously at the upper trip. Review pulse curves, current-limit delay, hot derating and fault repetition. |
| R106, R206, C109, C209, C110, C210 | Keep 10 kΩ, 2.2 nF and 100 pF as tuning candidates for each channel. These values give a network zero near 7.2 kHz and a high-frequency pole near 166 kHz. | Estimate crossover and phase margin separately for SEPIC and boost. Use vendor capacitance under DC bias, measured or bounded LED incremental resistance and topology-specific right-half-plane zeros. Plan bench tuning and stock only the alternatives justified by the analysis. |

The nominal current settings from the IADJ dividers and 0.22 Ω shunts are approximately 650 mA and 598 mA. The steady shunt dissipation is approximately 93 mW and 79 mW. Emitters still need a current and thermal envelope that includes ripple, tolerance and hot operating conditions. The existing behavioral simulation can screen power-stage behavior and the test sequence. Loop stability with the actual controller and load remains open. [TI TPS92691 datasheet](https://www.ti.com/lit/ds/symlink/tps92691.pdf).

## Before ordering and after delivery

1. Before paying for fabrication, close the on-paper compensation, capacitor, electrical stress and PCB layout review. Check package dimensions, availability, and the manufacturer’s four-layer stackup, drills and exposed-pad assembly process. Freeze one revision and export matching fabrication and assembly files after the final KiCad checks.
2. Budget separately for the four Broadcom AUV3-SQ62-0RT0K emitters and a TaoYuan TY-405nm20W sample, heatsinking, wiring, plus access to a current-limited bench supply, dummy load and measurement tools. Close the module bin and temperature limits before using it at target current. See the [405 nm bench worksheet](UV_405_BENCH.md).
3. Buy components and submit a small prototype fabrication order when budget permits and the release checks pass. After assembly, verify startup, regulation, PWM, fault behavior and temperatures on dummy loads first. Use a shielded, appropriately cooled setup for UV emitter tests.
