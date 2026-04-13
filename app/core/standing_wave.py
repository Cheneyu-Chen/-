from __future__ import annotations

import numpy as np


class StandingWaveModel:
    def __init__(self, length: float = 1.0, base_frequency: float = 1.0) -> None:
        self.length = length
        self.base_frequency = base_frequency

    def natural_frequency(self, mode: int, boundary: str = "fixed-fixed") -> float:
        mode = max(1, mode)
        if boundary == "fixed-fixed" or boundary == "free-free":
            return mode * self.base_frequency
        elif boundary == "fixed-free":
            return (mode - 0.5) * self.base_frequency
        return mode * self.base_frequency

    def amplitude_gain(self, drive_frequency: float, mode: int, damping: float, boundary: str = "fixed-fixed") -> float:
        f_n = self.natural_frequency(mode, boundary)
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
        boundary: str = "fixed-fixed",
    ) -> tuple[np.ndarray, np.ndarray, dict]:
        mode = max(1, int(mode))
        
        if boundary == "fixed-fixed":
            # x_n = L * n / m, n=0..m
            eigen_func = lambda pos: np.sin(mode * np.pi * pos / self.length)
            node_positions = [self.length * k / mode for k in range(mode + 1)]
        elif boundary == "free-free":
            # x_n = L * (n + 0.5) / m
            eigen_func = lambda pos: np.cos(mode * np.pi * pos / self.length)
            node_positions = [self.length * (k + 0.5) / mode for k in range(mode) if self.length * (k + 0.5) / mode <= self.length]
        else: # fixed-free
            # x_n = L * n / (m - 0.5)
            eigen_func = lambda pos: np.sin((mode - 0.5) * np.pi * pos / self.length)
            node_positions = [self.length * k / (mode - 0.5) for k in range(mode) if self.length * k / (mode - 0.5) <= self.length]

        coupling = abs(eigen_func(excitation_position))
        gain = self.amplitude_gain(drive_frequency, mode, damping, boundary)
        effective_amplitude = amplitude * np.clip(coupling, 0.08, 1.0) * gain / 3.0
        
        spatial = eigen_func(x)
        temporal = np.cos(2 * np.pi * drive_frequency * time_value)
        damping_factor = np.exp(-0.1 * damping * time_value)
        y = effective_amplitude * spatial * temporal * damping_factor
        envelope = np.abs(effective_amplitude * spatial)
        
        info = {
            "natural_frequency": self.natural_frequency(mode, boundary),
            "gain": gain,
            "coupling": coupling,
            "effective_amplitude": effective_amplitude,
            "node_positions": node_positions,
        }
        return y, envelope, info
