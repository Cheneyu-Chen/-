from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from matplotlib.path import Path as MplPath
from scipy import sparse
from scipy.ndimage import gaussian_filter, zoom
from scipy.sparse.linalg import eigsh

from app.core.modes import circular_mode, rectangular_mode, triangular_mode


@dataclass
class SimilarityResult:
    score: float
    correlation: float
    structure_overlap: float
    reference: np.ndarray
    simulation: np.ndarray


@dataclass
class PolygonModeResult:
    x: np.ndarray
    y: np.ndarray
    mode: np.ma.MaskedArray
    mask: np.ndarray
    relative_frequency: float
    active_points: int


@dataclass
class MetamaterialResult:
    frequencies: np.ndarray
    transmission_db: np.ndarray
    field: np.ndarray
    bandgap_start: float
    bandgap_end: float
    min_transmission: float


def grayscale_image(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image, dtype=float)
    if arr.ndim == 3:
        arr = arr[..., :3]
        arr = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
    arr = np.nan_to_num(arr)
    if arr.max() > 1.5:
        arr = arr / 255.0
    arr -= arr.min()
    arr /= max(float(arr.max()), 1e-9)
    return arr


def resize_to(image: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    scale_y = shape[0] / image.shape[0]
    scale_x = shape[1] / image.shape[1]
    resized = zoom(image, (scale_y, scale_x), order=1)
    return resized[: shape[0], : shape[1]]


def simulation_template(template: str, primary: int = 3, secondary: int = 2, resolution: int = 220) -> np.ndarray:
    if template == "一维驻波":
        x = np.linspace(0, 1, resolution)
        y = np.linspace(-1, 1, resolution)
        xx, yy = np.meshgrid(x, y)
        mode = max(primary, 1)
        curve = 0.62 * np.sin(mode * np.pi * xx)
        line = np.exp(-((yy - curve) ** 2) / 0.010)
        envelope = 0.24 * np.exp(-((yy - 0.62 * np.abs(np.sin(mode * np.pi * xx))) ** 2) / 0.022)
        arr = np.maximum(line, envelope)
    elif template == "二维驻波":
        x = np.linspace(0, 1, resolution)
        y = np.linspace(0, 1, resolution)
        xx, yy = np.meshgrid(x, y)
        arr = np.abs(np.sin(max(primary, 1) * np.pi * xx) * np.sin(max(secondary, 1) * np.pi * yy))
    elif template == "共振曲线":
        x = np.linspace(0.35, 2.4, resolution)
        y = np.linspace(0, 1, resolution)
        xx, yy = np.meshgrid(x, y)
        damping = max(0.035 * max(secondary, 1), 0.035)
        response = 1.0 / np.sqrt((1 - xx**2) ** 2 + (2 * damping * xx) ** 2)
        response = response / max(float(response.max()), 1e-9)
        curve = 0.08 + 0.82 * response
        arr = np.exp(-((yy - curve) ** 2) / 0.004)
        arr += 0.32 * np.exp(-((yy - 0.08) ** 2) / 0.002)
    elif template == "圆形克拉尼图形":
        _, _, mode, _ = circular_mode(max(primary - 1, 0), max(secondary, 1), resolution=resolution)
        arr = np.abs(np.ma.filled(mode, 0.0))
    elif template == "三角形薄板模态":
        _, _, mode, _ = triangular_mode(max(primary, 1), max(secondary, 1), resolution=resolution)
        arr = np.abs(np.ma.filled(mode, 0.0))
    else:
        _, _, mode, _ = rectangular_mode(max(primary, 1), max(secondary, 1), resolution=resolution)
        arr = np.abs(np.ma.filled(mode, 0.0))
    arr -= arr.min()
    arr /= max(float(arr.max()), 1e-9)
    return arr


def compare_experiment_photo(
    photo: np.ndarray,
    template: str,
    primary: int = 3,
    secondary: int = 2,
    resolution: int = 220,
) -> SimilarityResult:
    reference = grayscale_image(photo)
    reference = resize_to(reference, (resolution, resolution))
    reference = gaussian_filter(reference, sigma=1.0)
    reference -= reference.min()
    reference /= max(float(reference.max()), 1e-9)

    simulation = simulation_template(template, primary, secondary, resolution)
    simulation = gaussian_filter(simulation, sigma=1.0)

    ref_centered = reference - reference.mean()
    sim_centered = simulation - simulation.mean()
    correlation = float(
        np.sum(ref_centered * sim_centered)
        / max(np.linalg.norm(ref_centered) * np.linalg.norm(sim_centered), 1e-9)
    )
    correlation_score = (correlation + 1.0) / 2.0

    ref_binary = reference > np.quantile(reference, 0.70)
    sim_binary = simulation > np.quantile(simulation, 0.70)
    intersection = np.logical_and(ref_binary, sim_binary).sum()
    union = np.logical_or(ref_binary, sim_binary).sum()
    overlap = float(intersection / max(union, 1))

    score = float(np.clip(0.68 * correlation_score + 0.32 * overlap, 0.0, 1.0))
    return SimilarityResult(score, correlation, overlap, reference, simulation)


def parse_polygon_vertices(text: str) -> np.ndarray:
    vertices: list[tuple[float, float]] = []
    cleaned = text.replace("\n", ";")
    for item in cleaned.split(";"):
        item = item.strip()
        if not item:
            continue
        parts = [part.strip() for part in item.split(",")]
        if len(parts) != 2:
            raise ValueError("顶点格式应为 x,y；多个顶点用分号或换行分隔。")
        x, y = float(parts[0]), float(parts[1])
        vertices.append((x, y))
    if len(vertices) < 3:
        raise ValueError("多边形至少需要 3 个顶点。")
    return np.asarray(vertices, dtype=float)


def regular_polygon_vertices(sides: int = 6, radius: float = 0.42, center: tuple[float, float] = (0.5, 0.5)) -> np.ndarray:
    angles = np.linspace(0, 2 * np.pi, sides, endpoint=False) + np.pi / 2
    cx, cy = center
    return np.column_stack([cx + radius * np.cos(angles), cy + radius * np.sin(angles)])


def polygon_to_text(vertices: np.ndarray) -> str:
    return ";\n".join(f"{x:.3f},{y:.3f}" for x, y in vertices)


def finite_difference_plate_mode(
    vertices: np.ndarray,
    mode_index: int = 1,
    resolution: int = 38,
) -> PolygonModeResult:
    axis = np.linspace(0, 1, resolution)
    xx, yy = np.meshgrid(axis, axis)
    points = np.column_stack([xx.ravel(), yy.ravel()])
    mask = MplPath(vertices).contains_points(points).reshape(resolution, resolution)

    index_map = -np.ones_like(mask, dtype=int)
    active = np.argwhere(mask)
    if len(active) < 12:
        raise ValueError("多边形内部网格点太少，请增大面积或提高分辨率。")
    for idx, (row, col) in enumerate(active):
        index_map[row, col] = idx

    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    for idx, (row, col) in enumerate(active):
        rows.append(idx)
        cols.append(idx)
        data.append(4.0)
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            n_row, n_col = row + d_row, col + d_col
            if 0 <= n_row < resolution and 0 <= n_col < resolution and mask[n_row, n_col]:
                rows.append(idx)
                cols.append(index_map[n_row, n_col])
                data.append(-1.0)

    laplacian = sparse.csr_matrix((data, (rows, cols)), shape=(len(active), len(active)))
    plate_operator = laplacian @ laplacian
    requested = max(1, min(mode_index, min(8, len(active) - 2)))
    eigen_count = min(max(requested + 2, 4), len(active) - 1)
    values, vectors = eigsh(plate_operator, k=eigen_count, which="SM")
    order = np.argsort(values)
    vector = vectors[:, order[requested - 1]]

    field = np.full(mask.shape, np.nan, dtype=float)
    field[mask] = vector
    field /= max(float(np.nanmax(np.abs(field))), 1e-9)
    mode = np.ma.array(field, mask=~mask)
    relative_frequency = float(np.sqrt(max(values[order[requested - 1]], 0.0)))
    return PolygonModeResult(xx, yy, mode, mask, relative_frequency, len(active))


def metamaterial_array_response(
    rows: int = 8,
    cols: int = 8,
    resonant_frequency: float = 520.0,
    coupling: float = 0.36,
    damping: float = 0.08,
    observe_frequency: float = 520.0,
    points: int = 360,
) -> MetamaterialResult:
    frequencies = np.linspace(80.0, 1200.0, points)
    omega = frequencies / max(resonant_frequency, 1e-9)
    gamma = max(damping, 0.01)
    local_response = 1.0 / np.sqrt((1.0 - omega**2) ** 2 + (2.0 * gamma * omega) ** 2)
    stop_strength = np.exp(-((frequencies - resonant_frequency) / max(70.0 + 220.0 * coupling, 1.0)) ** 2)
    bragg = 0.18 * np.exp(-((frequencies - resonant_frequency * (1.0 + coupling)) / 130.0) ** 2)
    transmission = np.exp(-(0.28 + 2.15 * coupling) * stop_strength * local_response / max(local_response.max(), 1e-9) - bragg)
    transmission_db = 20.0 * np.log10(np.maximum(transmission, 1e-5))

    low_threshold = -6.0
    low = np.where(transmission_db < low_threshold)[0]
    if len(low):
        bandgap_start = float(frequencies[low[0]])
        bandgap_end = float(frequencies[low[-1]])
    else:
        bandgap_start = float(resonant_frequency)
        bandgap_end = float(resonant_frequency)

    x = np.arange(cols)
    y = np.arange(rows)
    xx, yy = np.meshgrid(x, y)
    phase = 2 * np.pi * observe_frequency / max(resonant_frequency, 1e-9)
    envelope = np.exp(-0.09 * xx * (1.0 + coupling * stop_strength[np.argmin(np.abs(frequencies - observe_frequency))]))
    lattice_wave = np.cos(phase * xx + 0.55 * np.sin(yy))
    resonator = 1.0 / np.sqrt((1.0 - (observe_frequency / resonant_frequency) ** 2) ** 2 + (2 * gamma * observe_frequency / resonant_frequency) ** 2)
    field = envelope * lattice_wave / max(resonator, 1.0)
    field /= max(float(np.max(np.abs(field))), 1e-9)

    return MetamaterialResult(
        frequencies=frequencies,
        transmission_db=transmission_db,
        field=field,
        bandgap_start=bandgap_start,
        bandgap_end=bandgap_end,
        min_transmission=float(transmission_db.min()),
    )
