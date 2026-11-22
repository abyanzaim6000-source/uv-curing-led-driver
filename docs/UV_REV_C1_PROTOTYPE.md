# Rev C1 first-prototype population

**Status: quote and review only.** Rev C1 specifies the reduced-current starting population for a current-limited dummy-load prototype. The previous Rev C quote remains a record of the higher target-current design. Supplier DFM, component sourcing and hardware verification are still open.

## Fit list and current assumptions

| Ref | Fit on Rev C1 | Purpose |
| --- | --- | --- |
| R110 | 8.06 kΩ, ±1%, 0603. Candidate Yageo RC0603FR-078K06L. | 365 nm nominal **579 mA**. |
| R210 | 12.4 kΩ, ±1%, 0603. Candidate Yageo RC0603FR-0712K4L. | 405 nm nominal **501 mA**. |
| C207 | 220 nF, ±10%, 50 V X7R, 0603. Candidate TDK C1608X7R1H224K080AE. | Slower initial soft start on 405 nm. |
| C110, C210 | Do not fit. | Reserved COMP tuning positions. |

Populate the other schematic positions as listed in the C1 review BOM. R111 and R211 remain 20.0 kΩ, both LED shunts remain 0.22 Ω, and both switch shunts remain 0.120 Ω. The schematic, PCB and assembly exports carry the C1 population. No trace or footprint changes were needed.

The nominal current uses `I = [2.5 V × 20 kΩ / (Rtop + 20 kΩ)] / (14 × 0.22 Ω)`. With the same sensitivity assumptions as the Rev C release review, the steady-current bands are approximately **537–621 mA** and **460–543 mA**. These are paper screening bands before ripple and transient peaks. Keep the original 4.99 kΩ and 7.15 kΩ resistors as later tuning options only after the emitters' current and temperature limits are established. [TI TPS92691 datasheet](https://www.ti.com/lit/ds/symlink/tps92691.pdf), [TDK capacitor catalog](https://product.tdk.com/system/files/dam/technicalsupport/tdk_meister/tdk_meister_partslist_en.pdf).

## Verification before emitter use

- **365 nm:** The switched CCM screen found zero growing modes across 128 cases at the new current with the selected coupled inductor. The highest modeled switch peak was 2.028 A. Run `python3 scripts/check_uv_sepic_switching.py`.
- **405 nm:** At nominal 501 mA, the modeled 100 nF configuration still reached 0.715 A during cold start in the high-line/high-capacitance case. With 220 nF, the maximum across the five screened combinations was 0.524 A at startup and 0.547 A at restart. A 543 mA target sensitivity gave 0.555 A startup and 0.598 A restart maxima. Run `python3 scripts/check_uv_405_restart.py --prototype`. The model omits the actual eFuse and controller internals. The longer soft-start setting still needs measured timing, input-current, and fault-recovery checks.
- Start with the optical emitters disconnected. Enable one channel at a time into a suitably rated dummy load using a current-limited bench supply. Record steady current, output voltage, ripple, cold startup and PWM restart at nominal input first. Capture the first switching cycle and later response. Use the 33 V nominal CV load for the 405 nm comparison and an appropriate CV load for the 365 nm string. Then check the intended voltage endpoints, eFuse behavior and combined operation. Investigate any peak above the provisional 0.65 A 405 nm review level before advancing. This is a test threshold and the actual module's current limit still needs confirmation.
- Before exposing an emitter to these settings, close the emitter's thermal and peak-current limits, verify the heat sink and shielding, and confirm the waveforms measured on the prototype. The manufacturing and fault review items in the Rev C release review still apply.

## Quote package

The archive includes matching C1 Gerbers, drill files, BOM, top-side placement data, assembly drawing, schematic and verification reports. C110/C210 are omitted in both the placement file and paste plot. Use the BOM's candidate part numbers for sourcing review and confirm availability with the assembler. The archive is for quote and CAM review.
