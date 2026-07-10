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
    intensity /= max(float(np.percentile(intensity, 98)), 1e-9)
    intensity = np.clip(intensity, 0, 1)
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


def diffraction_field_2d(
    frequency: float,
    slit_width: float,
    screen_distance: float,
    sound_speed: float = 343.0,
    x_resolution: int = 240,
    y_resolution: int = 160,
):
    x = np.linspace(-2.0, 2.0, x_resolution)
    y_max = max(screen_distance, 0.2)
    y = np.linspace(0.0, y_max, y_resolution)
    xx, yy = np.meshgrid(x, y)

    wavelength = sound_speed / max(frequency, 1e-6)
    sin_theta = xx / np.maximum(np.sqrt(xx**2 + yy**2), 1e-6)
    beta = np.pi * slit_width * sin_theta / max(wavelength, 1e-9)

    envelope = np.ones_like(beta)
    mask = np.abs(beta) > 1e-9
    envelope[mask] = (np.sin(beta[mask]) / beta[mask]) ** 2

    radius = np.sqrt(xx**2 + yy**2)
    attenuation = 1.0 / np.sqrt(np.maximum(radius, 0.25))
    intensity = envelope * attenuation
    intensity /= max(float(np.percentile(intensity, 98)), 1e-9)
    intensity = np.clip(intensity, 0.0, 1.0)
    return xx, yy, intensity, wavelength


def single_slit_diffraction_frame(
    frequency: float,
    slit_width: float,
    screen_distance: float,
    sound_speed: float,
    time_phase: float,
    resolution: int = 240,
):
    x = np.linspace(-2.5, 2.5, resolution)
    y = np.linspace(0.0, max(screen_distance, 0.2), resolution)
    xx, yy = np.meshgrid(x, y)

    wavelength = sound_speed / max(frequency, 1e-6)
    wave_number = 2.0 * np.pi / max(wavelength, 1e-9)
    omega = 2.0 * np.pi * time_phase

    obstacle_y = max(min(screen_distance * 0.28, screen_distance * 0.72), 0.18)
    slit_half = max(slit_width / 2.0, 0.02)
    aperture_count = max(21, int(np.ceil(48 * slit_width)))
    aperture_x = np.linspace(-slit_half, slit_half, aperture_count)
    aperture_y = np.full_like(aperture_x, obstacle_y)

    incident = np.cos(wave_number * yy - omega)
    transmitted = np.zeros_like(xx)
    for sx, sy in zip(aperture_x, aperture_y):
        rr = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
        rr = np.maximum(rr, 0.05)
        transmitted += np.cos(wave_number * rr - omega) / np.sqrt(rr)

    field = np.where(yy <= obstacle_y, incident, transmitted)
    field /= max(float(np.max(np.abs(field))), 1e-9)

    screen_x = np.linspace(-2.5, 2.5, resolution)
    screen_y = np.full_like(screen_x, screen_distance)
    screen_pressure = np.zeros_like(screen_x)
    for sx, sy in zip(aperture_x, aperture_y):
        rr = np.sqrt((screen_x - sx) ** 2 + (screen_y - sy) ** 2)
        rr = np.maximum(rr, 0.05)
        screen_pressure += np.cos(wave_number * rr - omega) / np.sqrt(rr)

    screen_intensity = screen_pressure**2
    screen_intensity /= max(float(np.max(screen_intensity)), 1e-9)

    return {
        "xx": xx,
        "yy": yy,
        "field": field,
        "screen_x": screen_x,
        "screen_intensity": screen_intensity,
        "wavefront_phase": float(time_phase % 1.0),
        "wavelength": wavelength,
        "obstacle_y": obstacle_y,
        "slit_half": slit_half,
    }


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
    f1 = float(half_power[0]) if len(half_power) > 0 else resonant_frequency
    f2 = float(half_power[-1]) if len(half_power) > 0 else resonant_frequency
    return freqs, absorption, bandwidth, f1, f2
