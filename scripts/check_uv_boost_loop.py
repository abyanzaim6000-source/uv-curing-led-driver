#!/usr/bin/env python3
"""Screen Rev B boost compensation with TI TPS92691 equations 34 and 36."""
from cmath import phase
from itertools import product
from math import degrees, pi


def boost_model(vin, vout, inductance, led_resistance, output_capacitance):
    duty = 1 - vin / vout
    load_factor = 1 + led_resistance * 0.600 / vout
    dc_gain = (1 - duty) / (0.15 * load_factor)
    pole = load_factor / (led_resistance * output_capacitance)
    rhp_zero = vout * (1 - duty) ** 2 / (inductance * 0.600)
    return dc_gain, pole, rhp_zero


def unity_crossings(model, resistor, main_cap, hf_cap):
    dc_gain, pole, rhp_zero = model

    def loop(frequency):
        s = 2j * pi * frequency
        total_cap = main_cap + hf_cap
        compensation = (1 + s * resistor * main_cap) / (
            s * total_cap * (1 + s * resistor * main_cap * hf_cap / total_cap)
        )
        modulator = dc_gain * (1 - s / rhp_zero) / (1 + s / pole)
        return 14 * 121e-6 * 0.22 * compensation * modulator

    # Stop at one-tenth of minimum switching frequency. TI's averaged
    # model does not represent sampled switching behavior near the clock.
    previous_frequency = 10.0
    previous_gain = abs(loop(previous_frequency))
    crossings = []
    for step in range(1, 401):
        frequency = 10 * (16_500 / 10) ** (step / 400)
        gain = abs(loop(frequency))
        if (previous_gain >= 1) != (gain >= 1):
            lower, upper = previous_frequency, frequency
            for _ in range(30):
                midpoint = (lower + upper) / 2
                if (abs(loop(midpoint)) >= 1) == (previous_gain >= 1):
                    lower = midpoint
                else:
                    upper = midpoint
            crossing = (lower + upper) / 2
            angle = degrees(phase(loop(crossing)))
            margin = 180 + (angle if angle <= 0 else angle - 360)
            crossings.append((crossing, margin))
        previous_frequency, previous_gain = frequency, gain
    return crossings


def main():
    # Effective capacitance and LED incremental resistance are sensitivity
    # inputs. They are not measured component/load bounds.
    models = [
        boost_model(*corner)
        for corner in product(
            (10.8, 13.2), (32, 34), (80e-6, 120e-6),
            (2, 4, 8, 12), (2e-6, 4.7e-6, 9.4e-6),
        )
    ]
    print(f"Boost right-half-plane zero: {min(m[2] for m in models) / (2*pi):.0f}"
          f"–{max(m[2] for m in models) / (2*pi):.0f} Hz")
    for label, resistor, main_cap, hf_cap in (
        ("Rev B", 10_000, 2.2e-9, 100e-12),
        ("220 nF integral candidate", 0, 220e-9, 0),
    ):
        passes = []
        for model in models:
            crossings = unity_crossings(model, resistor, main_cap, hf_cap)
            if len(crossings) != 1:
                continue
            frequency, margin = crossings[0]
            if frequency <= model[2] / (2 * pi * 5) and margin >= 45:
                passes.append((frequency, margin))
        print(f"{label}: {len(passes)}/{len(models)} corners meet the screen")
        if passes:
            frequencies, margins = zip(*passes)
            print(f"  Crossover {min(frequencies):.0f}–{max(frequencies):.0f} Hz, "
                  f"phase margin {min(margins):.1f}–{max(margins):.1f}°")


if __name__ == "__main__":
    main()
