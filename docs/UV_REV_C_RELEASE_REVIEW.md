# Rev C fabrication release review

**Status: quote and DFM review only.** The archive contains matching Rev C fabrication and assembly data. Wait for supplier DFM approval and the electrical decisions below before ordering. No supplier has been selected or contacted.

## Fabrication and assembly screen

JLCPCB is a reference process for this review. Use a standard four-layer 1.6 mm FR-4 stackup with 1 oz outer and 0.5 oz inner copper as the starting quote configuration. Confirm actual copper thickness, stackup, finish, stencil and inspection with the manufacturer. ENIG is a reasonable quote option for the exposed pads and fine-pitch assembly. [JLCPCB published stackups](https://jlcpcb.com/help/article/multi-layer-pcb-standard-laminated-structures), [JLCPCB PCB capabilities](https://jlcpcb.com/capabilities/Capabilities).

| Check | Rev C result and disposition |
| --- | --- |
| Outline and layers | 110 × 76 mm closed rectangular centerline from Edge.Cuts. F.Cu, In1.Cu, In2.Cu and B.Cu. In1.Cu is the principal ground plane. Confirm the physical fixture, connector wire clearance and retention. The current board has zero mounting holes. |
| Track and spacing | 0.150 mm minimum outer-layer trace, 0.200 mm nominal track-to-track clearance. The published multilayer 1 oz width and spacing is 0.09/0.09 mm for the standard service. Compare the actual plated-hole-to-copper and mask geometry in supplier CAM. |
| Drills and annulus | 67 via drills at 0.300 mm, with 0.550–0.650 mm via lands and 0.125 mm minimum radial via ring. Smallest component-hole radial ring is 0.35 mm. Drill report totals 80 plated hits and zero NPTH hits. Check the drill and plating tolerances with the selected process. |
| Component placement | 73 sites total, 65 populated SMT positions on the top, six populated through-hole parts, two DNP. JLCPCB publishes support for the board size, four-layer top-side assembly, 0.5 mm lead pitch and mixed assembly. Confirm sourcing, lead compatibility and whether panel fiducials or edge rails are needed for the assembly option. |
| Paste and exposed pads | U1 and U2 have two 0.99 × 1.86 mm paste apertures over a 2.46 × 2.31 mm mask opening, about 65% nominal coverage. U3 has four 1.09 mm square apertures over its 2.7 mm square exposed pad, also about 65%. Inspect the stencil, pad wetting, via treatment, and voiding plan with the assembler. These geometry ratios are not solder-joint measurements. |
| DNP handling | Leave C110 and C210 unpopulated. The supplied front paste layer and SMT placement file omit both sites. Other copper and mask layers retain their tuning pads. |

The six through-hole parts are C102, C202, J1, J2, J101 and J201. For Diodes Inc. B5100C, confirm the ordering suffix and polarity. Check the 63 V hybrid capacitors, power connectors, winding orientation, DPAK drain tabs and IC pin 1 on the assembly drawing before approving a placement preview. [JLCPCB assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities).

## Electrical release decisions

| Review | Result and remaining decision |
| --- | --- |
| LED current and temperature | With a 2.5 V reference at ±0.5%, 1% dividers and shunts, and a ±6.7 mV current-sense-offset sensitivity, the 365 nm setpoint screens at about 607–693 mA and the 405 nm setpoint at 556–641 mA. This is a paper screen at the datasheet offset extremes used for sensitivity, with ripple, temperature drift and PWM peaks outside the calculation. Broadcom rates the 365 nm emitter at 700 mA maximum with thermal derating. The 405 nm module's allowable pulse current and cooling remain unconfirmed. Use dummy loads first. Starting divider options of R110 = 8.06 kΩ and R210 = 12.4 kΩ would give about 579 mA and 501 mA nominal. These are reduced-current tuning options and are outside the exported population. |
| 405 nm restart and output energy | The datasheet-sequenced behavioral model reached 0.669 A at restart and 0.752 A in the largest cold-start case. Its longer soft-start trials reduced startup peaks but left restart as a separate issue. A 75.2 µF bulk bank stores about 75 mJ at 40 V. This energy can discharge locally into a fault independently of eFuse turn-off. Confirm precharge, PWM, OVP/restart waveforms and discharge on a current-limited dummy load. |
| Switch stress and shunt | The room-temperature saturation screen for the 365 nm coupled inductor gave about 4.76 A including an assumed turn-off delay versus a 5.4 A typical 10%-inductance-drop point. Hot data and measured switch turn-off are pending. Both 0.120 Ω shunts need pulse and hot-derating review. Capture switch voltage and gate ringing before accepting the 100 V MOSFET and diode margins. |
| Input protection and thermal | The 405 nm eFuse sits ahead of the boost converter. Its 6.04 kΩ ILIM resistor sets approximately 2.98 A typical versus roughly 2.22 A estimated full-load input. At 31 mΩ typical it dissipates about 0.15 W at that input current, before hot-resistance increase. Current limit, short behavior, latch-off, startup with PWM asserted and thermal transients still need verification. The boost inductor alone screened near 0.59 W 25 °C winding loss. Check rectifiers, shunts, the DPAK switches and both converter packages at sustained load. |
| COMP and sourcing | The CSV includes candidate part numbers and requirements where generic values are appropriate. Verify the COMP capacitors' effective capacitance with applied bias, tolerance, temperature and aging. Approve exact sourcing and substitutions before releasing an order. |

Sources for electrical limits and component behavior. [TPS92691 datasheet](https://www.ti.com/lit/ds/symlink/tps92691.pdf), [TPS26630 datasheet](https://www.ti.com/lit/ds/symlink/tps2663.pdf), [Broadcom 365 nm LED datasheet](https://docs.broadcom.com/doc/AUV3-Sxx2-0xx0K-3W-3535-SMT-UV-LED-DS), [Coilcraft coupled inductor datasheet](https://www.coilcraft.com/getmedia/8d898720-dd5a-438f-9500-665db0e36d7c/msd1583t.pdf).

## Archive contents and use

- `gerbers/` contains four copper files, two solder masks, top silk, top paste, Edge.Cuts, the Gerber job file and metric plated and nonplated Excellon files. The NPTH file has no drill hits. The paste for this build was plotted from a temporary board copy with only the DNP paste apertures suppressed.
- `assembly/` contains the engineering BOM, top SMT placement CSV in millimeters, and an SVG assembly drawing.
- `review/` contains the matching schematic PDF. `verification/` contains the netlist, ERC, DRC, drill report and source hashes.
- Board files cover the driver only. Emitter heads, heatsinks, external controller, wiring, motor and power supply are outside the assembly scope.

A KiCad design-rule pass verifies the geometry and connectivity against the project rules. Supplier CAM, final component approval and measured bring-up remain release gates.
