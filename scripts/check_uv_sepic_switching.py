#!/usr/bin/env python3
"""Cycle-by-cycle CCM SEPIC stability screen. Requires NumPy."""
from itertools import product
from math import ceil, log, log2, pi, sqrt

import numpy as np

from check_uv_rev_c import SENSE_GAIN, SEED_COMP, sepic_closed_poles

SHUNT = 0.10
RAMP = 0.20
LED_CURRENT = 0.65
BLANKING_TIME = 188e-9  # Leading-edge blanking in seconds.
MAX_DUTY = 0.904
PERTURBATION = 1e-5


def interval_matrix(vin, vout, l1, l2, coupling_cap, output_cap, load_r,
                    fsw, *, switch_on, coupling=0.0, damping=0.0, winding_dcr=0.068, shunt=SHUNT,
                    led_current=LED_CURRENT):
    """Return affine state dynamics normalized to one clock period.

    The state is iL1, iL2 (positive upwards), Vc - Vin, Vo - Vtarget,
    and comparator command voltage. The sixth coordinate is constant.
    """
    mutual = coupling * sqrt(l1 * l2)
    inductance = np.array([[l1, mutual], [mutual, l2]])
    matrix = np.zeros((6, 6))
    # Fixed-drop Schottky, specified winding DCR, 50 mΩ MOSFET on-resistance.
    dcr, diode_drop, on_resistance = winding_dcr, 0.60, 0.05 + shunt
    if switch_on:
        voltage = [
            [-dcr-on_resistance, -on_resistance, 0, 0, 0, vin],
            [-on_resistance, -dcr-on_resistance-damping, 1, 0, 0, vin],
        ]
        matrix[2, 1] = -1 / coupling_cap
    else:
        voltage = [
            [-dcr-damping, 0, -1, -1, 0, -vout-diode_drop],
            [0, -dcr, 0, -1, 0, -vout-diode_drop],
        ]
        matrix[2, 0] = 1 / coupling_cap
        matrix[3, :2] = 1 / output_cap
    matrix[:2] = np.linalg.solve(inductance, voltage)
    matrix[3, 3] = -1 / (load_r * output_cap)
    matrix[3, 5] = -led_current / output_cap
    matrix[4, 3] = -SENSE_GAIN / (load_r * SEED_COMP)
    return matrix / fsw


def propagator(matrix):
    # Scale the matrix so the Taylor expansion stays accurate even at
    # high coupling, where the leakage-mode dynamics are fast.
    squarings = max(0, ceil(log2(max(1, np.linalg.norm(matrix, np.inf)))))
    scaled = matrix / 2**squarings
    terms = [np.eye(len(matrix))]
    for degree in range(1, 17):
        terms.append(terms[-1] @ scaled / degree)
    coefficients = np.array(terms)

    def propagate(fraction, state):
        transition = np.polynomial.polynomial.polyval(fraction, coefficients)
        for _ in range(squarings):
            transition = transition @ transition
        return transition @ state

    return propagate


def cycle_map(corner, coupling, damping, winding_dcr, shunt, led_current):
    on = propagator(interval_matrix(*corner, switch_on=True,
                                   coupling=coupling, damping=damping,
                                   winding_dcr=winding_dcr, shunt=shunt, led_current=led_current))
    off = propagator(interval_matrix(*corner, switch_on=False,
                                    coupling=coupling, damping=damping,
                                   winding_dcr=winding_dcr, shunt=shunt, led_current=led_current))
    blanking_fraction = BLANKING_TIME * corner[-1]

    def step(state):
        augmented = np.append(state, 1)
        lower, upper = blanking_fraction, MAX_DUTY
        for _ in range(33):
            duty = (lower + upper) / 2
            switch_state = on(duty, augmented)
            comparator = shunt * sum(switch_state[:2]) + RAMP*duty - switch_state[4]
            if comparator < 0:
                lower = duty
            else:
                upper = duty
        duty = (lower + upper) / 2
        switch_state = on(duty, augmented)
        return off(1-duty, switch_state)[:5], duty, switch_state

    return step


def jacobian(step, state):
    return np.column_stack([
        (step(state + delta)[0] - step(state - delta)[0]) / (2*PERTURBATION)
        for delta in np.eye(len(state)) * PERTURBATION
    ])


def solve_corner(corner, *, coupling=0.0, damping=0.0, winding_dcr=0.068, shunt=SHUNT,
                    led_current=LED_CURRENT):
    vin, vout = corner[:2]
    duty = vout/(vin+vout)
    state = np.array([led_current*duty/(1-duty), led_current, 0, 0,
                      shunt*led_current/(1-duty)+RAMP*duty])
    step = cycle_map(corner, coupling, damping, winding_dcr, shunt, led_current)
    for _ in range(12):
        next_state, duty, switch_state = step(state)
        residual = next_state - state
        if np.linalg.norm(residual, np.inf) < 1e-8:
            blanking_fraction = BLANKING_TIME * corner[-1]
            if min(sum(state[:2]), sum(switch_state[:2])) <= 0:
                raise ValueError("Diode current reaches zero. CCM map is inapplicable.")
            if duty <= blanking_fraction + 1e-6 or duty >= MAX_DUTY - 1e-6:
                raise ValueError("Periodic orbit hits a PWM duty limit.")
            multipliers = np.linalg.eigvals(jacobian(step, state))
            dominant = max(multipliers, key=abs)
            return abs(dominant), abs(np.angle(dominant))*corner[-1]/(2*pi), duty, sum(switch_state[:2])
        state -= np.linalg.solve(jacobian(step, state)-np.eye(5), residual)
    raise ValueError("Periodic orbit did not converge.")


def main():
    # Use symmetric winding corners for a clean comparison of coupled
    # and uncoupled circuits. Mixed-inductance cases remain to be checked.
    corners = [
        (vin, vout, inductance, inductance, cap, out, load, frequency)
        for vin, vout, inductance, cap, out, load, frequency in product(
            (10.8, 13.2), (13.6, 16), (54.4e-6, 81.6e-6),
            (2e-6, 4.7e-6), (56e-6, 110e-6), (2, 12), (165e3, 230e3),
        )
    ]
    averaged = [max(sepic_closed_poles(*corner).real) > 0 for corner in corners]
    failures = 0
    for label, options, inductance_range in (
        ("Separate inductors", {}, None),
        ("Separate, 0.47 Ω coupling-cap series resistance", {"damping": 0.47}, None),
        ("Coupled, k = 0.90", {"coupling": 0.90}, None),
        ("MSD1583T-473MED candidate", {"coupling": 0.99, "winding_dcr": 0.12},
         (37.6e-6, 56.4e-6)),
        ("47 µH Rev C, 0.12 Ω shunt and 125 °C winding DCR",
         {"coupling": 0.98, "winding_dcr": 0.160, "shunt": 0.12}, (37.6e-6, 56.4e-6)),
        ("MSD1583T-333MED candidate", {"coupling": 0.99, "winding_dcr": 0.095},
         (26.4e-6, 39.6e-6)),
        ("47 µH Rev C1, reduced-current population",
         {"coupling": 0.98, "winding_dcr": 0.160, "shunt": 0.12,
          "led_current": 2.5 * 20_000 / (20_000 + 8_060) / (14 * 0.22)},
         (37.6e-6, 56.4e-6)),
    ):
        sweep = corners
        if inductance_range:
            replacement = dict(zip((54.4e-6, 81.6e-6), inductance_range))
            sweep = [
                (v_in, v_out, replacement[l1], replacement[l2], *remaining)
                for v_in, v_out, l1, l2, *remaining in corners
            ]
        try:
            results = [solve_corner(corner, **options) for corner in sweep]
        except (ValueError, np.linalg.LinAlgError) as error:
            print(f"{label}: incomplete model sweep: {error}")
            failures += 1
            continue
        unstable = sum(radius > 1 for radius, _, _, _ in results)
        radius, frequency, duty, _ = max(results)
        print(f"{label}: {unstable}/{len(results)} growing; worst multiplier {radius:.5f}, "
              f"mode {frequency:.0f} Hz, duty {duty:.3f}")
        print(f"  Maximum on-time end current {max(result[3] for result in results):.3f} A")
        if not options:
            print(f"  Averaged model flagged {sum(averaged)}/{len(corners)}; "
                  f"agreement in {sum(a == (r[0] > 1) for a, r in zip(averaged, results))} cases")
            print(f"  Worst switched growth rate {log(radius)*corners[results.index(max(results))][-1]:.0f} /s")

    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
