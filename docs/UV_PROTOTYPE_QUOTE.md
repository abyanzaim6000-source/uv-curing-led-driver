# UV driver prototype quote brief

**Rev B, quote and design-for-manufacture review only.** Confirm approved manufacturing files and a final BOM before ordering. Rev B has no enclosure mounting holes. Confirm mounting and connector access before releasing the outline.

The archive contains nine Gerber layers, the Gerber job file, metric plated/nonplated drill files, a 70-line BOM, a 64-position top-side SMT placement file, an assembly drawing, and ERC/DRC evidence. The six through-hole parts absent from the SMT placement file are C102, C202, J1, J2, J101 and J201. The NPTH file is empty because Rev B has no nonplated drill hits.

## Board and assembly

- 12 V UV curing driver evaluation PCB, nominal outline 110 × 76 mm, four copper layers, 1.6 mm nominal thickness. Quote the supplier’s standard four-layer stackup and identify copper weights and required process changes. Rev B uses 0.15 mm minimum trace width, nominal 0.20 mm netclass clearance and 0.30 mm minimum programmed drill diameter. Confirm actual process and plating assumptions.
- Quote a small prototype lot with assembly as a separate line item. All populated components are on the top side. Quote the SMT pass and through-hole fitting for the radial input capacitors and the power, LED and PWM connectors.
- For the exposed-pad TPS92691 and TPS26630 packages, review solder coverage, stencil strategy and thermal-via treatment. Flag any proposed process or library-footprint changes for approval.
- Main power components use named parts. Passives with generic values or provisional compensation/protection values must be resolved to an approved BOM before ordering. Quote any substitutions separately and identify the footprint or electrical impact.
- Scope is the driver board. External 365 nm and 405 nm LED heads, heatsinks, power supply, motor, controller and wiring are outside the assembly price. Ask for separately priced inspection or testing if available.
- Assembly inspection and continuity checks are useful. Functional acceptance for this project also requires current-limited bring-up and dummy-load startup, DIM and protection checks. Actual emitter tests follow in a shielded fixture.

## Files and release checks

Before an order, confirm a single matching revision of the schematic, routed board, layer plots, drill files, BOM and placement data. Review the outline, layer order, pin-one marks, diode and capacitor polarity, exposed pads and connector access. Save the clean KiCad DRC and schematic-parity evidence. Label prototypes as awaiting electrical bring-up until measured results are available.
