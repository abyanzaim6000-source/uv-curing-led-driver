"""Render the regulation and dropout comparison from exported waveform CSVs."""
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def plot_waveforms(results):
    fonts = Path("/System/Library/Fonts/Supplemental")
    image = Image.new('RGB', (1320, 910), 'white')
    draw = ImageDraw.Draw(image)

    def label(x, y, message, size=18, color='#24364a', bold=False, anchor='la'):
        filename = "Arial Bold.ttf" if bold else "Arial.ttf"
        try:
            font = ImageFont.truetype(str(fonts / filename), size)
        except OSError:
            font = ImageFont.load_default(size=size)
        draw.text((x, y), message, font=font, fill=color, anchor=anchor)

    label(65, 30, 'Dual-channel LED current at a 6 V source', 38, bold=True)
    label(66, 81, '54.4 µH inductors · 84.17 mΩ shunts · shared feed and 100 µF input capacitor', 21)
    draw.line((70, 135, 109, 135), fill='#006f9e', width=4)
    label(120, 135, 'Channel A', anchor='lm')
    draw.line((255, 135, 294, 135), fill='#ab4d17', width=4)
    label(305, 135, 'Channel B', anchor='lm')
    label(1270, 135, 'Shaded bands mark DIM-off intervals', anchor='rm')

    left, right = 132, 1250
    width = right - left
    for filename, title, top in [
        ('6v-regulation.csv', 'Nominal LED drop on both channels', 190),
        ('6v-dropout.csv', 'Channel A with 2.5 V additional LED drop', 535),
    ]:
        with (results / filename).open() as stream:
            reader = csv.reader(stream)
            next(reader)
            samples = [tuple(map(float, row)) for row in reader]
        if len(samples) < 2 or abs(samples[-1][0] - 0.001) > 1e-8:
            raise ValueError(f"{filename} does not cover the 1 ms demo interval")
        bottom = top + 236
        label(left, top - 29, title, 22, bold=True)
        for lo, hi in ((0.2, 0.4), (0.6, 0.8)):
            draw.rectangle((left + lo * width, top, left + hi * width, bottom), fill='#edf1f6')
        for amps in (0, 0.4, 0.8, 1.2, 1.6):
            y = bottom - amps / 1.6 * (bottom - top)
            draw.line((left, y, right, y), fill='#d8dfe7')
            label(left - 14, y, f'{amps:.1f}', anchor='rm')
        for ms in (0, 0.2, 0.4, 0.6, 0.8, 1):
            x = left + ms * width
            draw.line((x, bottom, x, bottom + 6), fill='#718096')
            label(x, bottom + 12, f'{ms:.1f}', anchor='ma')
        for channel, color in ((5, '#ab4d17'), (4, '#006f9e')):
            points = [
                (left + row[0] * 1000 * width, bottom - row[channel] / 1.6 * (bottom - top))
                for row in samples
            ]
            draw.line(points, fill=color, width=2)
        label(45, top + 115, 'A', bold=True)
        label((left + right) // 2, bottom + 40, 'Time (ms)', anchor='ma')

    label(66, 856, 'Behavioral ngspice simulation · DIM-off: channel A 0.20–0.40 ms, channel B 0.60–0.80 ms', 17)
    image.save(results / '6v-waveforms.png')
