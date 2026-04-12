from __future__ import annotations

import numpy as np


class StandingWaveModel:
    def __init__(self, length: float = 1.0, base_frequency: float = 1.0) -> None:
        self.length = length
        self.base_frequency = base_frequency

    def natural_frequency(self, mode: int) -> float:
        return max(1, mode) * self.base_frequency

    def amplitude_gain(self, drive_frequency: float, mode: int, damping: float) -> float:
        f_n = self.natural_frequency(mode)
        ratio = drive_frequency / max(f_n, 1e-6)
        damping = max(damping, 1e-4)
        gain = 1.0 / np.sqrt((1 - ratio**2) ** 2 + (2 * damping * ratio) ** 2)
        return float(np.clip(gain, 0.05, 8.0))

    def simulate(
        self,
        x: np.ndarray,
        time_value: float,
        drive_frequency: float,
        mode: int,
        damping: float,
        amplitude: float,
        excitation_position: float,
    ) -> tuple[np.ndarray, np.ndarray, dict]:
        mode = max(1, int(mode))
        coupling = abs(np.sin(mode * np.pi * excitation_position / self.length))
        gain = self.amplitude_gain(drive_frequency, mode, damping)
        effective_amplitude = amplitude * np.clip(coupling, 0.08, 1.0) * gain / 3.0
        spatial = np.sin(mode * np.pi * x / self.length)
        temporal = np.cos(2 * np.pi * drive_frequency * time_value)
        damping_factor = np.exp(-0.1 * damping * time_value)
        y = effective_amplitude * spatial * temporal * damping_factor
        envelope = np.abs(effective_amplitude * spatial)
        node_positions = [self.length * k / mode for k in range(mode + 1)]
        info = {
            "natural_frequency": self.natural_frequency(mode),
            "gain": gain,
            "coupling": coupling,
            "effective_amplitude": effective_amplitude,
            "node_positions": node_positions,
        }
        return y, envelope, info
