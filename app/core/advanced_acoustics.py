from __future__ import annotations

import numpy as np


def interference_field(
    frequency: float,
    source_spacing: float,
    phase_difference: float,
    sound_speed: float = 343.0,
    resolution: int = 220,
):
    x = np.linspace(-2.0, 2.0, resolution)
    y = np.linspace(-2.0, 2.0, resolution)
    xx, yy = np.meshgrid(x, y)
    k = 2 * np.pi * frequency / sound_speed
    sources = [(-source_spacing / 2, 0.0, 0.0), (source_spacing / 2, 0.0, phase_difference)]
    pressure = np.zeros_like(xx, dtype=np.complex128)
    for sx, sy, phase in sources:
        rr = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
        rr = np.maximum(rr, 0.04)
        pressure += np.exp(1j * (k * rr + phase)) / np.sqrt(rr)
    intensity = np.abs(pressure) ** 2
    intensity /= max(float(np.max(intensity)), 1e-9)
    return xx, yy, intensity


def diffraction_field(
    frequency: float,
    slit_width: float,
    screen_distance: float,
    sound_speed: float = 343.0,
    resolution: int = 260,
):
    x = np.linspace(-2.5, 2.5, resolution)
    wavelength = sound_speed / frequency
    beta = np.pi * slit_width * x / (wavelength * screen_distance)
    envelope = np.ones_like(beta)
    mask = np.abs(beta) > 1e-9
    envelope[mask] = (np.sin(beta[mask]) / beta[mask]) ** 2
    envelope /= max(float(np.max(envelope)), 1e-9)
    return x, envelope, wavelength


def phononic_chain_dispersion(
    mass_ratio: float,
    stiffness_ratio: float,
    cells: int = 240,
):
    q = np.linspace(0, np.pi, cells)
    m1 = 1.0
    m2 = max(mass_ratio, 0.05)
    k1 = 1.0
    k2 = max(stiffness_ratio, 0.05)
    term = (k1 + k2) * (1 / m1 + 1 / m2)
    coupling = 4 * k1 * k2 * np.sin(q / 2) ** 2 / (m1 * m2)
    root = np.sqrt(np.maximum(term**2 - 4 * coupling, 0.0))
    acoustic = np.sqrt(np.maximum((term - root) / 2, 0.0))
    optical = np.sqrt(np.maximum((term + root) / 2, 0.0))
    gap = max(float(np.min(optical) - np.max(acoustic)), 0.0)
    return q / np.pi, acoustic, optical, gap


def helmholtz_absorber_response(
    resonant_frequency: float,
    damping: float,
    f_min: float = 50.0,
    f_max: float = 1000.0,
    points: int = 400,
):
    freqs = np.linspace(f_min, f_max, points)
    ratio = freqs / max(resonant_frequency, 1e-6)
    damping = max(damping, 1e-4)
    absorption = (2 * damping * ratio) ** 2 / ((1 - ratio**2) ** 2 + (2 * damping * ratio) ** 2)
    absorption = np.clip(absorption, 0.0, 1.0)
    half_power = freqs[absorption >= 0.5]
    bandwidth = float(half_power[-1] - half_power[0]) if len(half_power) > 1 else 0.0
    return freqs, absorption, bandwidth
