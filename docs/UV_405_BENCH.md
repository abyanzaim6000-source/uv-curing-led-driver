# 405 nm boost bench worksheet

**Status: awaiting physical hardware.** Start an assembled Rev C1 board using the [first-prototype population and bench conditions](UV_REV_C1_PROTOTYPE.md), with the 405 nm channel set to about 501 mA nominal. A TPS92691EVM-752 or an equivalent reference board can establish a separate controller baseline. Record the specific board and settings for each capture. The 600 mA cases below are later engineering sweeps, and the eFuse tests require an assembled protected stage.


## Equipment and setup

- A current-limited bench supply at 12.0 V, a scope, and a DC electronic load in constant-voltage mode. For the 405 nm test the load must support 33 V and at least 600 mA simultaneously. Allow headroom above the steady operating point. Keep the optical emitter disconnected.
- Trigger on PWM and capture LED current with a current probe or differential voltage across a calibrated series shunt. Also record output voltage and, on the prototype, the eFuse output rail. Use a properly rated differential probe for any measurement across a floating or high-side shunt. An earth-referenced probe ground belongs at the circuit ground.
- On the TI EVM, use the boost output at J3. Leave the factory IADJ setting for the first nominal 350 mA run. Drive or hold TP8 low before power-up because the EVM normally pulls PWM up. Check jumper and connector markings against the user guide for the actual board revision. [TI EVM user guide, sections 3.1, 3.3 and 3.8](https://www.ti.com/lit/ug/slvuao7/slvuao7.pdf)

## First two captures

1. With the load in CV mode at 33 V and PWM held low, power up from a current-limited supply. Verify input voltage and record the initial output and current. Assert PWM and capture the first enable. Record peak current, settled current, output peak and approximate settling time. Start at the EVM's default 350 mA or another verified reduced current.
2. At the same load, capture a restart after a **1 ms PWM-off interval** so the timing can be compared with the switched model. Record the same measurements. Save the raw scope captures and note probe factors and current-sense conversion.
3. If the first two captures are acceptable for the test hardware, repeat at 600 mA. The EVM’s 0.16 Ω LED shunt implies nominal IADJ of 1.344 V for 600 mA. Follow its documented external-IADJ configuration and verify the actual current. The project board uses a different shunt and IADJ configuration. At 33 V × 600 mA, the load is about 19.8 W. Then repeat at the proposed 10.8 V and 13.2 V input endpoints. [TI EVM user guide, sections 4 and 6.4](https://www.ti.com/lit/ug/slvuao7/slvuao7.pdf)

| Board/revision | Input V | Load setting | Event | Peak A | Settled A | Output peak V | Settling time | Scope file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | 12.0 | 33 V CV / reduced current | First enable | | | | | |
| Pending | 12.0 | 33 V CV / reduced current | 1 ms off, then restart | | | | | |
| Pending | 12.0 | 33 V CV / 600 mA target | First enable | | | | | |
| Pending | 12.0 | 33 V CV / 600 mA target | 1 ms off, then restart | | | | | |

## Decision after the captures

At the 600 mA target, use 0.57–0.63 A as the provisional settled-current screening band. Flag any transient over 0.65 A for review. That value is a development screen and the module’s allowed pulse current still needs confirmation. If the waveform rings persistently, the supply current limit clips the run, or the peak exceeds the test hardware’s limits, stop the sweep and review the capture before increasing current or connecting the LED. Later, run open-load OVP and protected short-circuit tests as separate procedures on the assembled design.
