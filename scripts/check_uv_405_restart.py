#!/usr/bin/env python3
"""Datasheet-sequenced boost restart sensitivity model, not a TI macro-model."""
import argparse
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Case:
    vin: float
    led_voltage: float
    capacitance: float
    led_slope: float = 1.5
    off_time: float = 1e-3
    soft_start_cap: float = 100e-9


def simulate(case, step=50e-9, *, target=0.6):
    # LED voltage is specified at 600 mA. Idealized DDRV connects a
    # piecewise-linear load instantly on each PWM rising edge.
    knee = case.led_voltage - 0.6 * case.led_slope
    period = 5e-6
    clocks = round(period / step)
    blank = round(150e-9 / step)
    disable = round(20e-3 / step)
    restart = disable + round(case.off_time / step)
    end = restart + round(8e-3 / step)

    current = command = soft_start = 0.0
    output = case.vin - 0.6
    running = gate = caught_up = overvoltage = False
    clock = 0
    cold_peak = first_cycle_peak = restart_peak = pre_restart = 0.0
    steady_sum = steady_count = 0

    for index in range(end):
        enabled = index < disable or index >= restart
        if overvoltage and output < 37.5:
            overvoltage = False
        elif output > 39.5:
            overvoltage = True
            command = soft_start = 0.0
        active = enabled and not overvoltage
        if active and not running:
            gate = True
            caught_up = False
            clock = 0
        elif not active:
            gate = False
        elif caught_up and clock == clocks:
            gate = True
            clock = 0
        running = active

        led = max(0.0, (output - knee) / case.led_slope) if active else 0.0
        if active:
            # COMP is expressed relative to the internal comparator
            # offset. Start the simplified SS ceiling at zero volts.
            soft_start += step * 10e-6 / case.soft_start_cap
            ramp = 0.20 * min(clock / clocks, 1.0) if caught_up else 0.0
            sensed = 0.12 * current + ramp
            if gate and clock >= blank and (sensed >= command or clock >= 0.93 * clocks):
                gate = False
                if not caught_up:
                    caught_up = True
                    clock = 0
            if caught_up:
                error_charge = 14 * 0.22 * 121e-6 * (target - led) * step
                command = max(0.0, min(soft_start, 0.525, command + error_charge / 1e-6))
            clock += 1

        if gate:
            current += step * (case.vin - (0.118 + 0.05 + 0.12) * current) / 100e-6
            diode_current = 0.0
        else:
            current = max(0.0, current + step * (
                case.vin - output - 0.6 - 0.118 * current
            ) / 100e-6)
            diode_current = current
        output += step * (diode_current - led - output / 100_000) / case.capacitance

        if index < disable:
            cold_peak = max(cold_peak, led)
        if disable - round(2e-3 / step) <= index < disable:
            steady_sum += led
            steady_count += 1
        if index == restart - 1:
            pre_restart = output
        if index >= restart:
            restart_peak = max(restart_peak, led)
            if index < restart + clocks:
                first_cycle_peak = max(first_cycle_peak, led)

    return cold_peak, steady_sum / steady_count, first_cycle_peak, restart_peak, pre_restart


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prototype", action="store_true", help="use the C1 R210 population")
    args = parser.parse_args()
    target = 2.5 * 20_000 / (20_000 + 12_400) / (14 * 0.22) if args.prototype else 0.6
    cases = (
        Case(12, 33, 75.2e-6),
        Case(10.8, 34, 75.2e-6),
        Case(13.2, 32, 75.2e-6),
        Case(10.8, 34, 56e-6, off_time=20e-3),
        Case(13.2, 32, 110e-6, led_slope=2.0, off_time=20e-3),
        Case(13.2, 32, 110e-6, led_slope=2.0, off_time=20e-3, soft_start_cap=150e-9),
        Case(13.2, 32, 110e-6, led_slope=2.0, off_time=20e-3, soft_start_cap=220e-9),
    )
    if args.prototype:
        cases = tuple(replace(case, soft_start_cap=220e-9) for case in cases[:5])
    targets = (target, 0.543) if args.prototype else (target,)
    for current_target in targets:
        print(f"Modeled current target: {current_target:.3f} A")
        print("Input  LED @ 0.6 A  Bulk µF  PWM off  SS nF  Startup  Steady  First 5 µs  Restart  Pre-restart V")
        for case in cases:
            result = simulate(case, target=current_target)
            finer = simulate(case, step=25e-9, target=current_target)
            print(f"{case.vin:5.1f}  {case.led_voltage:11.1f}  {case.capacitance*1e6:7.1f}  "
                  f"{case.off_time*1e3:6.0f} ms  {case.soft_start_cap*1e9:5.0f}  "
                  + "  ".join(f"{value:.3f}" for value in finer))
            peak_delta = max(abs(result[index] - finer[index]) for index in (0, 2, 3))
            if peak_delta > 0.03:
                print(f"  Peak timestep sensitivity: {peak_delta:.3f} A")



if __name__ == "__main__":
    main()
