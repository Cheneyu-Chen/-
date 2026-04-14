from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks


def scan_resonance(start_freq: float, end_freq: float, points: int, natural_frequency: float, damping: float):
    frequencies = np.linspace(start_freq, end_freq, points)
    damping = max(damping, 1e-4)
    ratio = frequencies / max(natural_frequency, 1e-6)
    response = 1.0 / np.sqrt((1 - ratio**2) ** 2 + (2 * damping * ratio) ** 2)
    peaks, _ = find_peaks(response, prominence=max(response) * 0.1)
    return frequencies, response, peaks
