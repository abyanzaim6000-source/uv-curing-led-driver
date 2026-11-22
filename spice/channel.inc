* Behavioral LED buck channel. Vprobe measures LED current in both switch states.
.subckt LED_BUCK vin dim sw gnd params: extra_vf=0 rsense=83.333333m inductance=68u
Rsense vin csn {rsense}
Dled csn led_drop LED_APPROX
Vextra led_drop led_return {extra_vf}
Lout led_return inductor_end {inductance}
Vprobe inductor_end sw 0
Dfree sw vin FREEWHEEL_APPROX
* Approximate switch-node capacitance regularizes rapid commutation.
Csw sw gnd 100p

* Positive control closes the low-side switch. The switch opens at 115 mV
* sense drop and closes at 85 mV. DIM below 0.3 V forces the switch open.
Bcontrol control gnd V=V(dim,gnd)<0.3 ? -1 : 0.1-V(vin,csn)
Spower sw gnd control gnd POWER_SWITCH

.model LED_APPROX D(Is=1e-24 N=2 Rs=0.12)
.model FREEWHEEL_APPROX D(Is=1u N=1.1 Rs=0.07)
.model POWER_SWITCH SW(Ron=0.4 Roff=100Meg Vt=0 Vh=15m)
.ends LED_BUCK
