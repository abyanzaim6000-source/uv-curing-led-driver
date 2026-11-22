#!/usr/bin/env python3
"""Compare candidate UV driver values. The SEPIC sweep requires NumPy."""
from itertools import product
from math import pi

import numpy as np

from check_uv_boost_loop import boost_model, unity_crossings

SENSE_GAIN = 14 * 121e-6 * 0.22
SEED_COMP = 1e-6  # Effective COMP capacitance in both sweeps.


def boost_corners():
    corners = product(
        (10.8, 13.2), (32, 34), (80e-6, 120e-6),
        (2, 4, 8, 12), (56e-6, 75e-6, 110e-6),
    )
    results = []
    for corner in corners:
        gain, pole, rhp_zero = boost_model(*corner)
        candidate_model = (gain * 0.15 / 0.12, pole, rhp_zero)
        (frequency, margin), = unity_crossings(candidate_model, 0, SEED_COMP, 0)
        passed = margin >= 45 and frequency <= rhp_zero / (10 * pi)
        results.append((frequency, margin, passed))
    return results


def sepic_closed_poles(vin, vout, l1, l2, coupling_cap, output_cap, load_r, fsw):
    """Linearized averaged CCM circuit with a summed-current comparator."""
    duty = vout / (vin + vout)
    off = 1 - duty
    total_current = 0.65 / off
    dcr = 0.068
    shunt = 0.10
    ramp = 0.20

    # States: input inductor current, second inductor current, coupling
    # capacitor voltage, and output capacitor voltage. DC uses ideal duty.
    fixed_duty = np.array([
        [-dcr/l1, 0, -off/l1, -off/l1],
        [0, -dcr/l2, duty/l2, -off/l2],
        [off/coupling_cap, -duty/coupling_cap, 0, 0],
        [off/output_cap, off/output_cap, 0, -1/(load_r*output_cap)],
    ])
    duty_input = np.array([
        (vin+vout)/l1, (vin+vout)/l2,
        -total_current/coupling_cap, -total_current/output_cap,
    ])

    # Peak = average summed current + half of its on-time ripple.
    duty_per_volt = 1 / (ramp + shunt*vin*(1/l1+1/l2)/(2*fsw))
    duty_per_state = -duty_per_volt * shunt * np.array([
        1, 1, duty/(2*fsw*l2), 0,
    ])

    # The fifth state is COMP voltage with integral current feedback.
    closed_loop = np.zeros((5, 5))
    closed_loop[:4, :4] = fixed_duty + np.outer(duty_input, duty_per_state)
    closed_loop[:4, 4] = duty_input * duty_per_volt
    closed_loop[4, 3] = -SENSE_GAIN / (load_r * SEED_COMP)
    return np.linalg.eigvals(closed_loop)


def main():
    boost = boost_corners()
    print(f"405 nm boost: {sum(row[2] for row in boost)}/{len(boost)} corners meet the screen")
    print(f"  Crossover {min(row[0] for row in boost):.0f}–{max(row[0] for row in boost):.0f} Hz")
    print(f"  Phase margin {min(row[1] for row in boost):.1f}–{max(row[1] for row in boost):.1f}°")

    sepic = [
        max(sepic_closed_poles(*corner).real)
        for corner in product(
            (10.8, 13.2), (13.6, 16), (54.4e-6, 81.6e-6), (54.4e-6, 81.6e-6),
            (2e-6, 4.7e-6), (56e-6, 110e-6), (2, 12), (165e3, 230e3),
        )
    ]
    print(f"365 nm SEPIC: {sum(pole < 0 for pole in sepic)}/{len(sepic)} corners "
          "have all averaged closed-loop poles in the left half-plane")
    print("These are sensitivity results, with hardware and switching-model validation pending.")


if __name__ == "__main__":
    main()
