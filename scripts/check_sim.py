"""Run the behavioral LED-driver regression with standalone or bundled ngspice."""
import argparse
import ctypes
import csv
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

SPICE = Path(__file__).resolve().parents[1] / "spice"
KICAD_NGSPICE = Path(
    "/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib"
)
MEASUREMENT = re.compile(
    r"^(\w+)\s*=\s*([-+\d.eE]+)(?:\s|$)", re.MULTILINE
)


def run_shared(library_path, deck_path):
    """Run one shared-library simulation in an isolated worker process."""
    library = ctypes.CDLL(library_path)
    callback_type = ctypes.CFUNCTYPE(
        ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p
    )

    @callback_type
    def message(data, _identifier, _user_data):
        print(data.decode(errors="replace").removeprefix("stdout ").removeprefix("stderr "))
        return 0

    library.ngSpice_Init.argtypes = [callback_type, callback_type] + [ctypes.c_void_p] * 5
    library.ngSpice_Circ.argtypes = [ctypes.POINTER(ctypes.c_char_p)]
    library.ngSpice_Command.argtypes = [ctypes.c_char_p]
    if library.ngSpice_Init(message, message, None, None, None, None, None):
        return 1
    lines = Path(deck_path).read_bytes().splitlines()
    circuit = (ctypes.c_char_p * (len(lines) + 1))(*lines, None)
    return library.ngSpice_Circ(circuit) or library.ngSpice_Command(b"run")


def simulate(command, directory, name, source, *, timeout=30):
    deck = directory / "case.cir"
    deck.write_text(source, encoding="utf-8")
    result = subprocess.run(
        [*command, str(deck)], cwd=directory, capture_output=True, text=True, timeout=timeout
    )
    output = result.stdout + "\n" + result.stderr
    if result.returncode or re.search(
        r"timestep too small|simulation\(s\) aborted|^\s*error[: ]", output,
        re.IGNORECASE | re.MULTILINE,
    ):
        raise ValueError(f"{name}: simulation failed\n{output}")
    return {key: float(value) for key, value in MEASUREMENT.findall(output)}


def check(metrics, name, low, high):
    value = metrics.get(name, math.nan)
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{name}: expected {low:g} to {high:g}, got {value:g}")
    return value


def with_supply(source, voltage):
    return source.replace("Vin vin 0 12", f"Vin vin 0 {voltage}")


def shared_supply(source, voltage):
    feed = (
        f"Vin source 0 {voltage}\n"
        "Rfeed source feed 100m\n"
        "Lfeed feed vin 200n\n"
        "Resr vin bulk 50m\n"
        f"Cbulk bulk 0 100u IC={voltage}"
    )
    return source.replace("Vin vin 0 12", feed).replace("0 50n uic", "0 10n uic")


def export_waveform(directory, destination):
    source = directory / "waveform.dat"
    with source.open() as data, destination.open("w", newline="") as output:
        header = next(data).split()
        if len(header) != 6:
            raise ValueError(f"Unexpected waveform columns: {header}")
        writer = csv.writer(output)
        writer.writerow(("time_s", "local_vin_v", "dim_a_v", "dim_b_v", "led_a_a", "led_b_a"))
        for line in data:
            writer.writerow(line.split())
    source.unlink()


def combined_cases(command, directory, dual, export_dir):
    print("Combined 6 V supply, LED headroom and passive tolerances", flush=True)
    rows = []
    for extra in (0, 2, 2.5):
        for inductance in (54.4, 81.6):
            for shunt in (82.5, 84.166666):
                source = shared_supply(dual, 6).replace(
                    "LED_BUCK", f"LED_BUCK inductance={inductance}u rsense={shunt}m"
                ).replace(
                    "Xa vin dima swa 0 LED_BUCK", f"Xa vin dima swa 0 LED_BUCK extra_vf={extra}"
                )
                capture = export_dir and inductance == 54.4 and shunt == 84.166666 and extra in (0, 2.5)
                if capture:
                    source = source.replace(
                        ".end\n",
                        ".control\nrun\nlinearize v(vin) v(dima) v(dimb) i(v.xa.vprobe) i(v.xb.vprobe)\n"
                        "set wr_singlescale\nset wr_vecnames\n"
                        "wrdata waveform.dat v(vin) v(dima) v(dimb) i(v.xa.vprobe) i(v.xb.vprobe)\n"
                        ".endc\n.end\n",
                    )
                name = f"6 V +{extra:g} V LED drop, {inductance:g} uH, {shunt:.2f} mΩ"
                metrics = simulate(command, directory, name, source)
                for channel in ("a", "b"):
                    check(metrics, f"{channel}_off", 0, 1e-5)
                    check(metrics, f"{channel}_control_off", -1.01, -0.99)
                b = check(metrics, "b_both_on", 1.17, 1.23)
                b_alone = check(metrics, "b_while_a_off", 1.17, 1.23)
                check(metrics, "b_recovered", 1.17, 1.23)
                a = check(metrics, "a_both_on", 0, 1.28)
                a_alone = check(metrics, "a_while_b_off", 0, 1.28)
                check(metrics, "a_recovered", 0, 1.28)
                if extra == 0:
                    for metric in ("a_both_on", "a_while_b_off", "a_recovered"):
                        check(metrics, metric, 1.17, 1.23)
                if extra == 2.5:
                    check(metrics, "a_both_on", 0, 1.17)
                rows.append((extra, inductance, shunt, a, b, a_alone, b_alone))
                print(f"  {name}: both on A {a:.4f} A, B {b:.4f} A")
                if capture:
                    filename = "6v-regulation.csv" if extra == 0 else "6v-dropout.csv"
                    export_waveform(directory, export_dir / filename)
    if export_dir:
        with (export_dir / "combined-6v-summary.csv").open("w", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(("extra_a_led_drop_v", "inductance_uh", "shunt_mohm",
                             "a_both_on_a", "b_both_on_a", "a_alone_a", "b_alone_a"))
            writer.writerows(rows)


def regression(command, directory, export_dir):
    single = (SPICE / "single_channel.cir").read_text()
    dual = (SPICE / "dual_channel.cir").read_text()
    shutil.copyfile(SPICE / "channel.inc", directory / "channel.inc")

    print("Supply and independent DIM checks", flush=True)
    for voltage in (6, 12, 24, 30):
        metrics = simulate(command, directory, f"single {voltage} V", with_supply(single, voltage))
        average = check(metrics, "led_avg", 1.18, 1.22)
        check(metrics, "startup", 1e-9, 100e-6)
        check(metrics, "led_min", 1.01, 1.03)
        check(metrics, "led_max", 1.37, 1.39)
        period = check(metrics, "switching_period", 1e-6, 50e-6)
        if voltage == 12:
            refined = single.replace("0 50n uic", "0 25n uic")
            fine = simulate(command, directory, "12 V refined timestep", refined)
            check(fine, "led_avg", average - 0.005, average + 0.005)
        metrics = simulate(command, directory, f"dual {voltage} V", with_supply(dual, voltage))
        for channel in ("a", "b"):
            check(metrics, f"{channel}_off", 0, 1e-5)
            check(metrics, f"{channel}_control_off", -1.01, -0.99)
            check(metrics, f"{channel}_both_on", 1.18, 1.22)
            check(metrics, f"{channel}_recovered", 1.18, 1.22)
        a_on = check(metrics, "a_while_b_off", 1.18, 1.22)
        b_on = check(metrics, "b_while_a_off", 1.18, 1.22)
        print(f"  {voltage:2} V: single {average:.4f} A at {1e-3 / period:.1f} kHz, "
              f"A alone {a_on:.4f} A, B alone {b_on:.4f} A")

    print("Shared supply with feed impedance and input decoupling", flush=True)
    for voltage in (6, 12, 24, 30):
        source = shared_supply(dual, voltage).replace(
            ".end\n",
            ".meas tran rail_min MIN v(vin) FROM=90u TO=1m\n"
            ".meas tran rail_max MAX v(vin) FROM=90u TO=1m\n.end\n",
        )
        metrics = simulate(command, directory, f"shared supply {voltage} V", source)
        shifts = []
        for channel, other in (("a", "b"), ("b", "a")):
            both = check(metrics, f"{channel}_both_on", 1.18, 1.22)
            alone = check(metrics, f"{channel}_while_{other}_off", 1.18, 1.22)
            check(metrics, f"{channel}_recovered", 1.18, 1.22)
            check(metrics, f"{channel}_off", 0, 1e-5)
            check(metrics, f"{channel}_control_off", -1.01, -0.99)
            shifts.append(abs(alone - both))
        worst_shift = max(shifts)
        if worst_shift > 0.02:
            raise ValueError(f"{voltage} V: channel current changed by {worst_shift:.4f} A")
        rail_min = check(metrics, "rail_min", voltage - 0.5, voltage + 0.5)
        rail_max = check(metrics, "rail_max", rail_min, voltage + 0.5)
        print(f"  {voltage:2} V: rail {rail_min:.3f}–{rail_max:.3f} V, "
              f"largest mean current shift {worst_shift * 1000:.1f} mA")

    print("Inductor and shunt tolerance endpoints", flush=True)
    for voltage in (6, 30):
        for inductance in (54.4, 81.6):
            for shunt_scale in (0.99, 1.01):
                shunt = 83.333333 * shunt_scale
                source = with_supply(single, voltage).replace(
                    "sw 0 LED_BUCK", f"sw 0 LED_BUCK inductance={inductance}u rsense={shunt:.6f}m"
                ).replace("0 50n uic", "0 10n uic")
                metrics = simulate(command, directory, f"passives {voltage} V", source)
                average = check(metrics, "led_avg", 1.17, 1.23)
                if (voltage, inductance, shunt_scale) == (30, 54.4, 1.01):
                    refined = source.replace("0 10n uic", "0 5n uic")
                    fine = simulate(command, directory, "refined 30 V passive corner", refined)
                    check(fine, "led_avg", average - 0.005, average + 0.005)
                check(metrics, "led_min", 1.00, 1.04)
                check(metrics, "led_max", 1.35, 1.41)
                period = check(metrics, "switching_period", 1e-6, 50e-6)
                print(f"  {voltage:2} V, {inductance:.1f} uH, {shunt:.2f} mΩ: "
                      f"{average:.4f} A at {1e-3 / period:.1f} kHz")

    combined_cases(command, directory, dual, export_dir)

    print("PWM at 12 V and 1 kHz", flush=True)
    for duty in (0.1, 0.5, 0.9):
        source = single.split(".tran", 1)[0].replace(
            "Vdim dim 0 1", f"Vdim dim 0 PULSE(0.2 1 0 100n 100n {duty}m 1m)"
        )
        source += (".tran 100n 5m 0 50n uic\n"
                   ".meas tran pwm_avg AVG i(v.xled.vprobe) FROM=2m TO=5m\n.end\n")
        metrics = simulate(command, directory, f"PWM {duty:.0%}", source)
        average = check(metrics, "pwm_avg", 1.2 * duty - 0.04, 1.2 * duty + 0.04)
        print(f"  {duty:.0%}: {average:.4f} A average")

    print("LED forward-voltage headroom at 6 V", flush=True)
    for extra in (0, 1, 2, 2.25, 2.5, 2.75, 3):
        source = with_supply(single, 6).replace("sw 0 LED_BUCK", f"sw 0 LED_BUCK extra_vf={extra}")
        # Switching can stop in dropout, so measure current without requiring a period.
        source = "\n".join(line for line in source.splitlines()
                           if not line.startswith(".meas tran switching_period")) + "\n"
        metrics = simulate(command, directory, f"headroom +{extra} V", source)
        average = check(metrics, "led_avg", 0, 1.25)
        if extra == 0:
            check(metrics, "led_avg", 1.18, 1.22)
        if extra == 3:
            check(metrics, "led_avg", 0, 1.17)
        print(f"  +{extra:g} V LED drop: {average:.4f} A average")


def boost_diagnostics(command, directory):
    source = (SPICE / "uv_405_dummy_load.cir").read_text()
    cases = (
        ("Nominal", 12, 33, 6.8),
        ("Low input / high LED drop", 10.8, 34, 4.7),
        ("High input / low LED drop", 13.2, 32, 9.4),
    )
    print("405 nm behavioral boost with switched power stage", flush=True)
    for name, voltage, dummy, cap in cases:
        deck = source.replace(
            ".param input_v=12 dummy_v=33 cap_out=6.8u",
            f".param input_v={voltage} dummy_v={dummy} cap_out={cap}u",
        )
        metrics = simulate(command, directory, name, deck, timeout=90)
        steady = check(metrics, "led_steady", 0.57, 0.63)
        check(metrics, "led_off", 0, 1e-5)
        recovered = check(metrics, "led_restarted", 0.57, 0.63)
        startup_peak = check(metrics, "startup_peak", steady, 5)
        restart_peak = check(metrics, "pwm_restart_peak", recovered, 5)
        print(f"  {name}: steady {steady:.3f} A, recovered {recovered:.3f} A, "
              f"startup / PWM restart peaks {startup_peak:.3f} / {restart_peak:.3f} A", flush=True)
        if max(startup_peak, restart_peak) > 0.65:
            print("    Review: transient peak exceeds the 0.65 A screening level.", flush=True)

    print("405 nm behavioral open-load cutoff", flush=True)
    deck = source.split(".tran", 1)[0].replace(
        "Vopen open_fault 0 0", "Vopen open_fault 0 PWL(0 0 4.999m 0 5m 1)"
    )
    deck += (".tran 50n 8m 0 50n\n"
             ".meas tran open_peak MAX v(out) FROM=5m TO=8m\n"
             ".meas tran open_gate AVG v(gate) FROM=6m TO=6.9m\n"
             ".meas tran open_current RMS i(Vprobe) FROM=6m TO=6.9m\n.end\n")
    metrics = simulate(command, directory, "open load", deck, timeout=90)
    peak = check(metrics, "open_peak", 39.5, 45)
    check(metrics, "open_gate", 0, 1e-3)
    check(metrics, "open_current", 0, 1e-5)
    print(f"  Peak output {peak:.2f} V; switching disabled after simulated OVP.")

    source = (SPICE / "uv_boost_feedthrough.cir").read_text()
    metrics = simulate(command, directory, "fault feed-through", source)
    raw = check(metrics, "unprotected_fault_avg", 3, 6)
    check(metrics, "protected_before_open", 3, 6)
    after = check(metrics, "protected_after_open", 0, 1e-5)
    print(f"405 nm feed-through: {raw:.2f} A without interruption, {after * 1e6:.2f} µA after forced disconnect.")
    print("Behavioral diagnostic checks complete. Controller and eFuse hardware signoff remain open.")



def boost_rev_c_diagnostics(command, directory):
    """Screen the new power components using the existing behavioral control."""
    source = (SPICE / "uv_405_dummy_load.cir").read_text()
    cases = (
        ("Rev B reference", 10.8, 34, 4.7, False),
        ("Rev C nominal", 12, 33, 75.2, True),
        ("Rev C low line", 10.8, 34, 75.2, True),
        ("Rev C high line", 13.2, 32, 75.2, True),
        ("Rev C low line, low capacitance", 10.8, 34, 56, True),
        ("Rev C low line, high capacitance", 10.8, 34, 110, True),
    )
    print("405 nm power-component sensitivity with behavioral control", flush=True)
    for name, voltage, dummy, cap, rev_c in cases:
        deck = source.replace(
            ".param input_v=12 dummy_v=33 cap_out=6.8u",
            f".param input_v={voltage} dummy_v={dummy} cap_out={cap}u",
        )
        if rev_c:
            deck = deck.replace("Ris sense 0 0.15", "Ris sense 0 0.12")
            deck = deck.replace(
                "Cout out 0 {cap_out}",
                "Cceramic out 0 4.7u\nRbulk out cb 11m\nCout cb 0 {cap_out}",
            )
        deck = deck.replace(
            ".end\n",
            ".meas tran pre_restart FIND v(out) AT=7.998m\n"
            ".meas tran first_cycle_peak MAX i(Vprobe) FROM=8m TO=8.005m\n.end\n",
        )
        metrics = simulate(command, directory, name, deck, timeout=90)
        steady = check(metrics, "led_steady", 0.55, 0.65)
        recovered = check(metrics, "led_restarted", 0.55, 0.65)
        startup = check(metrics, "startup_peak", steady, 5)
        restart = check(metrics, "pwm_restart_peak", recovered, 5)
        first_cycle = check(metrics, "first_cycle_peak", 0, 5)
        pre_restart = check(metrics, "pre_restart", 0, 45)
        print(f"  {name}: steady/recovered {steady:.3f}/{recovered:.3f} A, "
              f"startup/restart {startup:.3f}/{restart:.3f} A, "
              f"first cycle {first_cycle:.3f} A at {pre_restart:.2f} V before restart", flush=True)
        if max(startup, restart) > 0.65:
            print("    Review: transient peak exceeds the 0.65 A screening level.", flush=True)
    print("Rev C uses the existing behavioral control law. Hardware transients remain open.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, help="path to an ngspice shared library")
    parser.add_argument("--export-dir", type=Path, help="write waveform CSVs, result summary, and comparison figure (requires Pillow 10.1+)")
    diagnostics = parser.add_mutually_exclusive_group()
    diagnostics.add_argument("--uv-405", action="store_true", help="run the 405 nm switched-boost diagnostics")
    diagnostics.add_argument("--uv-405-rev-c", action="store_true",
                             help="screen the Rev C boost power components")
    args = parser.parse_args()
    if (args.uv_405 or args.uv_405_rev_c) and args.export_dir:
        parser.error("UV diagnostics and --export-dir run different suites")
    if args.export_dir:
        try:
            from plot_waveforms import plot_waveforms
        except ImportError:
            parser.error("figure export requires Pillow 10.1+ (python3 -m pip install 'Pillow>=10.1')")
    executable = shutil.which("ngspice")
    if executable and args.library is None:
        command = [executable, "-b"]
    else:
        library = (args.library or KICAD_NGSPICE).resolve()
        if not library.is_file():
            parser.error("install ngspice or supply its shared library with --library")
        command = [sys.executable, str(Path(__file__).resolve()), "--shared-worker", str(library)]

    try:
        with tempfile.TemporaryDirectory(prefix="led-driver-") as scratch:
            if args.export_dir:
                args.export_dir.mkdir(parents=True, exist_ok=True)
            if args.uv_405:
                boost_diagnostics(command, Path(scratch))
            elif args.uv_405_rev_c:
                boost_rev_c_diagnostics(command, Path(scratch))
            else:
                regression(command, Path(scratch), args.export_dir)
            if args.export_dir:
                plot_waveforms(args.export_dir)
    except (ValueError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"FAIL: {error}\n")
    if not args.uv_405:
        print("PASS: behavioral LED-driver regression")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--shared-worker"]:
        sys.exit(run_shared(*sys.argv[2:]))
    main()
