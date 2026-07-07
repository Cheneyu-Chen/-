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

    def wave_speed(self) -> float:
        return 2.0 * self.length * self.base_frequency

    def estimate_plot_range(
        self,
        x: np.ndarray,
        drive_frequency: float,
        mode: int,
        damping: float,
        amplitude: float,
        excitation_position: float,
        boundary: str = "fixed-fixed",
    ) -> tuple[float, float]:
        mode = max(1, int(mode))
        natural_frequency = self.natural_frequency(mode, boundary)
        horizon = max(2.0, 2.5 / max(drive_frequency, 1e-6), 2.5 / max(natural_frequency, 1e-6))
        sample_times = np.linspace(0.0, horizon, 24)
        peak = 0.0

        for sample_time in sample_times:
            y, _, _ = self.simulate(
                x,
                float(sample_time),
                drive_frequency,
                mode,
                damping,
                amplitude,
                excitation_position,
                boundary,
            )
            peak = max(peak, float(np.max(np.abs(y))))

        limit = max(0.12, peak * 1.35)
        step = max(0.05, round(limit / 4.0 / 0.05) * 0.05)
        return limit, step

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

        natural_frequency = self.natural_frequency(mode, boundary)
        coupling = abs(eigen_func(excitation_position))
        gain = self.amplitude_gain(drive_frequency, mode, damping, boundary)
        effective_amplitude = amplitude * np.clip(coupling, 0.08, 1.0) * gain / 3.0

        angular_frequency = 2 * np.pi * drive_frequency
        wave_speed = self.wave_speed()
        travel_distance = wave_speed * time_value
        wavelength = wave_speed / max(drive_frequency, 1e-6)
        wavenumber = 2 * np.pi / max(wavelength, 1e-6)
        distance_from_source = np.abs(x - excitation_position)
        local_spread = np.clip(0.04 * self.length + 0.12 * travel_distance, 0.04 * self.length, 0.35 * self.length)
        local_packet = np.exp(-((distance_from_source - travel_distance) ** 2) / (2 * local_spread**2))
        local_wave = local_packet * np.cos(angular_frequency * time_value - wavenumber * distance_from_source)
        local_decay = np.exp(-time_value / max(0.7, 1.2 / max(drive_frequency, 1e-6)))
        local_component = amplitude * np.clip(coupling, 0.08, 1.0) * local_wave * local_decay / 2.5

        spatial = eigen_func(x)
        temporal = np.cos(2 * np.pi * drive_frequency * time_value)
        damping_factor = np.exp(-0.1 * damping * time_value)
        build_up = 1.0 - np.exp(-time_value / max(0.9, 1.6 / max(natural_frequency, 1e-6)))
        standing_component = effective_amplitude * spatial * temporal * damping_factor * build_up
        y = local_component + standing_component
        envelope = np.abs(local_component) + np.abs(standing_component)
        
        info = {
            "natural_frequency": natural_frequency,
            "gain": gain,
            "coupling": coupling,
            "effective_amplitude": effective_amplitude,
            "node_positions": node_positions,
            "build_up": build_up,
            "travel_distance": travel_distance,
        }
        return y, envelope, info
