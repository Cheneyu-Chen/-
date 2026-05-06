from __future__ import annotations

import numpy as np


def spherical_wave_field(
    frequency: float,
    time_value: float,
    sound_speed: float = 343.0,
    extent: float = 2.0,
    resolution: int = 120,
):
    axis = np.linspace(-extent, extent, resolution)
    xx, yy = np.meshgrid(axis, axis)
    rr = np.sqrt(xx**2 + yy**2)
    wavelength = sound_speed / frequency
    k = 2 * np.pi / wavelength
    omega = 2 * np.pi * frequency
    pressure = np.cos(k * rr - omega * time_value) / np.sqrt(np.maximum(rr, 0.08))
    pressure /= max(float(np.max(np.abs(pressure))), 1e-9)
    return xx, yy, pressure, wavelength


def two_source_wave_field(
    frequency: float,
    spacing: float,
    phase_difference: float,
    time_value: float,
    sound_speed: float = 343.0,
    extent: float = 2.0,
    resolution: int = 120,
):
    axis = np.linspace(-extent, extent, resolution)
    xx, yy = np.meshgrid(axis, axis)
    wavelength = sound_speed / frequency
    k = 2 * np.pi / wavelength
    omega = 2 * np.pi * frequency
    pressure = np.zeros_like(xx)
    for sx, phase in [(-spacing / 2, 0.0), (spacing / 2, phase_difference)]:
        rr = np.sqrt((xx - sx) ** 2 + yy**2)
        pressure += np.cos(k * rr - omega * time_value + phase) / np.sqrt(np.maximum(rr, 0.08))
    pressure /= max(float(np.max(np.abs(pressure))), 1e-9)
    return xx, yy, pressure, wavelength


def room_mode_field(
    mode_x: int,
    mode_y: int,
    mode_z: int,
    time_value: float,
    frequency: float = 180.0,
    resolution: int = 70,
):
    x = np.linspace(0, 1, resolution)
    y = np.linspace(0, 1, resolution)
    xx, yy = np.meshgrid(x, y)
    z_slice = 0.5
    spatial = (
        np.cos(mode_x * np.pi * xx)
        * np.cos(mode_y * np.pi * yy)
        * np.cos(mode_z * np.pi * z_slice)
    )
    pressure = spatial * np.cos(2 * np.pi * frequency * time_value)
    pressure /= max(float(np.max(np.abs(pressure))), 1e-9)
    relative_frequency = np.sqrt(mode_x**2 + mode_y**2 + mode_z**2)
    return xx, yy, pressure, relative_frequency


def room_mode_slices(
    mode_x: int,
    mode_y: int,
    mode_z: int,
    time_value: float,
    frequency: float = 180.0,
    resolution: int = 55,
):
    axis = np.linspace(0, 1, resolution)
    xx, yy = np.meshgrid(axis, axis)
    temporal = np.cos(2 * np.pi * frequency * time_value)

    z_mid = 0.5
    xy_pressure = (
        np.cos(mode_x * np.pi * xx)
        * np.cos(mode_y * np.pi * yy)
        * np.cos(mode_z * np.pi * z_mid)
        * temporal
    )
    xy_x = xx
    xy_y = yy
    xy_z = np.full_like(xx, z_mid)

    yy2, zz2 = np.meshgrid(axis, axis)
    x_mid = 0.5
    yz_pressure = (
        np.cos(mode_x * np.pi * x_mid)
        * np.cos(mode_y * np.pi * yy2)
        * np.cos(mode_z * np.pi * zz2)
        * temporal
    )
    yz_x = np.full_like(yy2, x_mid)
    yz_y = yy2
    yz_z = zz2

    xx3, zz3 = np.meshgrid(axis, axis)
    y_mid = 0.5
    xz_pressure = (
        np.cos(mode_x * np.pi * xx3)
        * np.cos(mode_y * np.pi * y_mid)
        * np.cos(mode_z * np.pi * zz3)
        * temporal
    )
    xz_x = xx3
    xz_y = np.full_like(xx3, y_mid)
    xz_z = zz3

    max_abs = max(
        float(np.max(np.abs(xy_pressure))),
        float(np.max(np.abs(yz_pressure))),
        float(np.max(np.abs(xz_pressure))),
        1e-9,
    )
    xy_pressure /= max_abs
    yz_pressure /= max_abs
    xz_pressure /= max_abs

    relative_frequency = np.sqrt(mode_x**2 + mode_y**2 + mode_z**2)
    return {
        "xy": (xy_x, xy_y, xy_z, xy_pressure),
        "yz": (yz_x, yz_y, yz_z, yz_pressure),
        "xz": (xz_x, xz_y, xz_z, xz_pressure),
        "relative_frequency": relative_frequency,
    }
