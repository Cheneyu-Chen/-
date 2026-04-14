from __future__ import annotations

import numpy as np
from scipy.special import jn_zeros, jv


def rectangular_mode(m: int, n: int, resolution: int = 160):
    x = np.linspace(0, 1, resolution)
    y = np.linspace(0, 1, resolution)
    xx, yy = np.meshgrid(x, y)
    zz = np.sin(m * np.pi * xx) * np.sin(n * np.pi * yy)
    relative_frequency = np.sqrt(m**2 + n**2)
    return xx, yy, zz, relative_frequency


def circular_mode(order: int, radial_index: int, resolution: int = 220):
    axis = np.linspace(-1, 1, resolution)
    xx, yy = np.meshgrid(axis, axis)
    rr = np.sqrt(xx**2 + yy**2)
    theta = np.arctan2(yy, xx)
    zero = jn_zeros(order, radial_index)[radial_index - 1]
    zz = jv(order, zero * rr) * np.cos(order * theta)
    zz = np.ma.array(zz, mask=rr > 1.0)
    relative_frequency = float(zero)
    return xx, yy, zz, relative_frequency
