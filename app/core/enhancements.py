from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from matplotlib.path import Path as MplPath
from scipy import sparse
from scipy.ndimage import (
    binary_closing,
    binary_fill_holes,
    distance_transform_edt,
    gaussian_filter,
    gaussian_filter1d,
    label as nd_label,
    sobel,
    zoom,
)
from scipy.sparse.linalg import eigsh

from app.core.modes import circular_mode, rectangular_mode, triangular_mode


@dataclass
class SimilarityResult:
    score: float
    correlation: float
    structure_overlap: float
    reference: np.ndarray
    simulation: np.ndarray


@dataclass(frozen=True)
class RoiCandidate:
    image: np.ndarray
    mask: np.ndarray
    confidence: float
    center_x: float = 0.5
    center_y: float = 0.5
    radius: float = 0.5


@dataclass(frozen=True)
class NormalizedView:
    image: np.ndarray
    mask: np.ndarray


@dataclass(frozen=True)
class FeatureBundle:
    values: np.ndarray
    mask: np.ndarray
    kind: str = "map"


@dataclass(frozen=True)
class MatchMetrics:
    score: float
    correlation: float
    structure_overlap: float


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


def _photo_grayscale(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image, dtype=float)
    if arr.ndim == 3:
        arr = arr[..., :3]
        arr = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
    arr = np.nan_to_num(arr)
    if arr.max() > 1.5:
        arr = arr / 255.0
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


def _normalize_feature(arr: np.ndarray) -> np.ndarray:
    values = np.asarray(arr, dtype=float)
    low, high = np.percentile(values, [1.0, 99.0])
    values = np.clip(values, low, high)
    values -= low
    values /= max(float(high - low), 1e-9)
    return values


def _structural_feature(image: np.ndarray) -> np.ndarray:
    gray = gaussian_filter(np.asarray(image, dtype=float), sigma=0.8)
    background = gaussian_filter(gray, sigma=10.0)
    local_contrast = np.abs(gray - background)
    gradient_x = sobel(gray, axis=1, mode="reflect")
    gradient_y = sobel(gray, axis=0, mode="reflect")
    edge_strength = np.hypot(gradient_x, gradient_y)
    feature = 0.65 * _normalize_feature(local_contrast) + 0.35 * _normalize_feature(edge_strength)
    return gaussian_filter(_normalize_feature(feature), sigma=0.8)


def _center_square_crop(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    if height == width:
        return image
    if width > height:
        start = (width - height) // 2
        return image[:, start : start + height]
    start = (height - width) // 2
    return image[start : start + width, :]


def _pad_to_square(image: np.ndarray, fill_value: float | None = None) -> np.ndarray:
    height, width = image.shape[:2]
    if height == width:
        return image
    size = max(height, width)
    if fill_value is None:
        fill_value = float(np.median(image))
    result = np.full((size, size), fill_value, dtype=float)
    offset_y = (size - height) // 2
    offset_x = (size - width) // 2
    result[offset_y : offset_y + height, offset_x : offset_x + width] = image
    return result


def _content_square_crop(image: np.ndarray) -> np.ndarray:
    gray = np.asarray(image, dtype=float)
    if gray.ndim != 2:
        gray = grayscale_image(gray)
    gray = np.nan_to_num(gray)
    if min(gray.shape[:2]) < 12:
        return _center_square_crop(gray)

    smooth = gaussian_filter(gray, sigma=0.9)
    background = gaussian_filter(smooth, sigma=max(6.0, min(gray.shape) / 7.0))
    local_contrast = np.abs(smooth - background)
    gradient_x = sobel(smooth, axis=1, mode="reflect")
    gradient_y = sobel(smooth, axis=0, mode="reflect")
    edge_strength = np.hypot(gradient_x, gradient_y)
    activity = _normalize_feature(0.72 * local_contrast + 0.28 * edge_strength)
    activity = gaussian_filter(activity, sigma=1.25)

    threshold = max(float(np.quantile(activity, 0.80)), 0.18)
    mask = activity >= threshold
    if mask.sum() < max(24, int(activity.size * 0.05)):
        threshold = max(float(np.quantile(activity, 0.68)), 0.12)
        mask = activity >= threshold
    mask = binary_closing(mask, iterations=2)
    mask = binary_fill_holes(mask)

    labels, count = nd_label(mask)

    if count == 0:
        return _center_square_crop(gray)

    center = np.array([(gray.shape[0] - 1) / 2.0, (gray.shape[1] - 1) / 2.0])
    best_index: int | None = None
    best_score: float | None = None
    for label_index in range(1, count + 1):
        region = labels == label_index
        area = int(region.sum())
        if area < max(24, int(gray.size * 0.02)):
            continue
        rows, cols = np.where(region)
        if rows.size == 0:
            continue
        centroid = np.array([float(rows.mean()), float(cols.mean())])
        distance = float(np.linalg.norm(centroid - center))
        span_y = float(rows.max() - rows.min() + 1)
        span_x = float(cols.max() - cols.min() + 1)
        span = float(np.hypot(span_y, span_x))
        score = area / (1.0 + 0.25 * distance) + 0.15 * span
        if best_score is None or score > best_score:
            best_score = score
            best_index = label_index

    if best_index is None:
        return _center_square_crop(gray)

    region = labels == best_index
    rows, cols = np.where(region)
    if rows.size == 0:
        return _center_square_crop(gray)

    centroid_y = float(rows.mean())
    centroid_x = float(cols.mean())
    span_y = float(rows.max() - rows.min() + 1)
    span_x = float(cols.max() - cols.min() + 1)
    side = int(round(max(span_y, span_x) * 1.8))
    side = max(side, int(round(min(gray.shape) * 0.62)))
    side = min(side, max(gray.shape))

    center_y = int(round(centroid_y))
    center_x = int(round(centroid_x))
    top = max(0, min(center_y - side // 2, gray.shape[0] - side))
    left = max(0, min(center_x - side // 2, gray.shape[1] - side))
    bottom = top + side
    right = left + side
    crop = gray[top:bottom, left:right]
    if crop.size == 0:
        return _center_square_crop(gray)
    return _pad_to_square(crop, fill_value=float(np.median(gray)))


def _center_scale(image: np.ndarray, scale: float) -> np.ndarray:
    if abs(scale - 1.0) < 1e-9:
        return image
    scaled = zoom(image, (scale, scale), order=1)
    size_y, size_x = image.shape
    if scaled.shape[0] >= size_y and scaled.shape[1] >= size_x:
        start_y = (scaled.shape[0] - size_y) // 2
        start_x = (scaled.shape[1] - size_x) // 2
        return scaled[start_y : start_y + size_y, start_x : start_x + size_x]
    result = np.full_like(image, float(np.median(image)))
    offset_y = (size_y - scaled.shape[0]) // 2
    offset_x = (size_x - scaled.shape[1]) // 2
    result[offset_y : offset_y + scaled.shape[0], offset_x : offset_x + scaled.shape[1]] = scaled
    return result


def _template_valid_mask(template: str, resolution: int) -> np.ndarray:
    axis = np.linspace(0.0, 1.0, resolution)
    xx, yy = np.meshgrid(axis, axis)
    if template == "圆形克拉尼图形":
        return (xx - 0.5) ** 2 + (yy - 0.5) ** 2 <= 0.92**2
    if template == "三角形薄板模态":
        return (yy <= 1.0 - xx) & (xx >= 0.04) & (yy >= 0.04)
    return (xx >= 0.04) & (xx <= 0.96) & (yy >= 0.04) & (yy <= 0.96)


def _masked_correlation(first: np.ndarray, second: np.ndarray, mask: np.ndarray) -> float:
    first_values = np.asarray(first[mask], dtype=float)
    second_values = np.asarray(second[mask], dtype=float)
    if first_values.size < 16:
        return 0.0
    first_values -= first_values.mean()
    second_values -= second_values.mean()
    denominator = np.linalg.norm(first_values) * np.linalg.norm(second_values)
    if denominator < 1e-9:
        return 0.0
    return float(np.dot(first_values, second_values) / denominator)


def _structure_overlap(first: np.ndarray, second: np.ndarray, mask: np.ndarray) -> float:
    first_values = first[mask]
    second_values = second[mask]
    if first_values.size < 16 or second_values.size < 16:
        return 0.0
    first_binary = first >= np.quantile(first_values, 0.74)
    second_binary = second >= np.quantile(second_values, 0.74)
    first_binary &= mask
    second_binary &= mask

    intersection = np.logical_and(first_binary, second_binary).sum()
    union = np.logical_or(first_binary, second_binary).sum()
    iou = float(intersection / max(union, 1))
    if not first_binary.any() or not second_binary.any():
        return iou

    first_distance = distance_transform_edt(~first_binary)
    second_distance = distance_transform_edt(~second_binary)
    first_to_second = float(second_distance[first_binary].mean())
    second_to_first = float(first_distance[second_binary].mean())
    tolerance = max(first.shape) * 0.08
    distance_score = float(np.exp(-0.5 * (first_to_second + second_to_first) / max(tolerance, 1e-9)))
    return float(np.clip(0.55 * iou + 0.45 * distance_score, 0.0, 1.0))


def _offsets(radius: int, step: int) -> list[int]:
    values = list(range(-radius, radius + 1, step))
    if radius not in values:
        values.append(radius)
    if -radius not in values:
        values.insert(0, -radius)
    return values


def _aligned_views(
    reference: np.ndarray,
    simulation: np.ndarray,
    valid_mask: np.ndarray,
    dy: int,
    dx: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    size_y, size_x = reference.shape
    ref_y_start, ref_y_end = max(dy, 0), min(size_y, size_y + dy)
    sim_y_start, sim_y_end = max(-dy, 0), min(size_y, size_y - dy)
    ref_x_start, ref_x_end = max(dx, 0), min(size_x, size_x + dx)
    sim_x_start, sim_x_end = max(-dx, 0), min(size_x, size_x - dx)
    return (
        reference[ref_y_start:ref_y_end, ref_x_start:ref_x_end],
        simulation[sim_y_start:sim_y_end, sim_x_start:sim_x_end],
        valid_mask[sim_y_start:sim_y_end, sim_x_start:sim_x_end],
    )


def _full_frame_candidate(photo: np.ndarray, confidence: float = 1.0) -> RoiCandidate:
    gray = _photo_grayscale(photo)
    return RoiCandidate(
        image=gray,
        mask=np.ones(gray.shape, dtype=bool),
        confidence=confidence,
        center_x=0.5,
        center_y=0.5,
        radius=0.5,
    )


def _resize_mask(mask: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    if mask.shape == shape:
        return np.asarray(mask, dtype=bool)
    scale_y = shape[0] / mask.shape[0]
    scale_x = shape[1] / mask.shape[1]
    resized = zoom(np.asarray(mask, dtype=float), (scale_y, scale_x), order=0)
    return resized[: shape[0], : shape[1]] >= 0.5


def _normalize_candidate(candidate: RoiCandidate, resolution: int) -> NormalizedView:
    image = np.asarray(candidate.image, dtype=float)
    mask = np.asarray(candidate.mask, dtype=bool)
    image = _center_square_crop(image)
    mask = _center_square_crop(mask)
    normalized = resize_to(image, (resolution, resolution))
    normalized_mask = _resize_mask(mask, (resolution, resolution))
    return NormalizedView(normalized, normalized_mask)


class _SimilarityAdapter:
    def detect_roi(self, photo: np.ndarray) -> list[RoiCandidate]:
        return [_full_frame_candidate(photo)]

    def normalize(self, candidate: RoiCandidate, resolution: int) -> NormalizedView:
        return _normalize_candidate(candidate, resolution)

    def simulation_view(
        self,
        template: str,
        primary: int,
        secondary: int,
        resolution: int,
    ) -> NormalizedView:
        simulation = simulation_template(template, primary, secondary, resolution)
        mask = _template_valid_mask(template, resolution)
        return NormalizedView(simulation, mask)

    def extract_features(self, view: NormalizedView) -> FeatureBundle:
        return FeatureBundle(view.image, view.mask, "map")

    def compare(self, reference: FeatureBundle, simulation: FeatureBundle) -> MatchMetrics:
        return _compare_feature_bundles(reference, simulation)


class _StandingWaveAdapter(_SimilarityAdapter):
    def simulation_view(
        self,
        template: str,
        primary: int,
        secondary: int,
        resolution: int,
    ) -> NormalizedView:
        simulation = simulation_template(template, primary, secondary, resolution)
        return NormalizedView(simulation, np.ones(simulation.shape, dtype=bool))

    def normalize(self, candidate: RoiCandidate, resolution: int) -> NormalizedView:
        image = resize_to(np.asarray(candidate.image, dtype=float), (resolution, resolution))
        mask = _resize_mask(candidate.mask, (resolution, resolution))
        return NormalizedView(image, mask)

    def extract_features(self, view: NormalizedView) -> FeatureBundle:
        image = gaussian_filter(view.image, sigma=1.0)
        image -= image.min()
        image /= max(float(image.max()), 1e-9)
        return FeatureBundle(image, view.mask, "standing")

    def compare(self, reference: FeatureBundle, simulation: FeatureBundle) -> MatchMetrics:
        return _compare_standing_bundles(reference, simulation)


class _CurvePhotoAdapter(_SimilarityAdapter):
    def normalize(self, candidate: RoiCandidate, resolution: int) -> NormalizedView:
        image = resize_to(np.asarray(candidate.image, dtype=float), (resolution, resolution))
        mask = _resize_mask(candidate.mask, (resolution, resolution))
        return NormalizedView(image, mask)

    def extract_features(self, view: NormalizedView) -> FeatureBundle:
        return FeatureBundle(_curve_profile(view.image, view.image.shape[0]), view.mask.any(axis=0), "profile")

    def compare(self, reference: FeatureBundle, simulation: FeatureBundle) -> MatchMetrics:
        return _compare_profile_bundles(reference, simulation)


class _PlanarPhotoAdapter(_SimilarityAdapter):
    pass


class _GenericPhotoAdapter(_PlanarPhotoAdapter):
    pass


class _CircularPhotoAdapter(_PlanarPhotoAdapter):
    @staticmethod
    def _sample(image: np.ndarray, rows: np.ndarray, cols: np.ndarray) -> np.ndarray:
        row_index = np.clip(np.rint(rows).astype(int), 0, image.shape[0] - 1)
        col_index = np.clip(np.rint(cols).astype(int), 0, image.shape[1] - 1)
        return image[row_index, col_index]

    @classmethod
    def _proposal_score(
        cls,
        gray: np.ndarray,
        edge: np.ndarray,
        center_y: float,
        center_x: float,
        radius: float,
    ) -> float:
        angles = np.linspace(0.0, 2.0 * np.pi, 192, endpoint=False)
        sin_angles = np.sin(angles)
        cos_angles = np.cos(angles)
        edge_ring = cls._sample(
            edge,
            center_y + radius * sin_angles,
            center_x + radius * cos_angles,
        )
        inner_ring = cls._sample(
            gray,
            center_y + radius * 0.78 * sin_angles,
            center_x + radius * 0.78 * cos_angles,
        )
        outer_ring = cls._sample(
            gray,
            center_y + radius * 1.10 * sin_angles,
            center_x + radius * 1.10 * cos_angles,
        )
        edge_baseline = float(np.median(edge))
        contrast = float(np.median(np.abs(inner_ring - outer_ring)))
        edge_consistency = float(np.quantile(edge_ring, 0.55))
        return edge_consistency / max(edge_baseline, 1e-6) + 0.75 * contrast

    @staticmethod
    def _square_crop(
        gray: np.ndarray,
        center_y: float,
        center_x: float,
        side: int,
    ) -> np.ndarray:
        fill = float(np.median(gray))
        result = np.full((side, side), fill, dtype=float)
        top = int(round(center_y - side / 2.0))
        left = int(round(center_x - side / 2.0))
        source_top = max(top, 0)
        source_left = max(left, 0)
        source_bottom = min(top + side, gray.shape[0])
        source_right = min(left + side, gray.shape[1])
        if source_top >= source_bottom or source_left >= source_right:
            return result
        target_top = source_top - top
        target_left = source_left - left
        result[
            target_top : target_top + source_bottom - source_top,
            target_left : target_left + source_right - source_left,
        ] = gray[source_top:source_bottom, source_left:source_right]
        return result

    def detect_roi(self, photo: np.ndarray) -> list[RoiCandidate]:
        gray = _photo_grayscale(photo)
        if gray.ndim != 2 or min(gray.shape) < 24:
            return [_full_frame_candidate(gray)]

        smooth = gaussian_filter(gray, sigma=1.0)
        gradient_x = sobel(smooth, axis=1, mode="reflect")
        gradient_y = sobel(smooth, axis=0, mode="reflect")
        edge = np.hypot(gradient_x, gradient_y)
        height, width = gray.shape
        minimum = float(min(height, width))
        center_rows = np.linspace(0.40 * (height - 1), 0.60 * (height - 1), 7)
        center_cols = np.linspace(0.40 * (width - 1), 0.60 * (width - 1), 7)
        radii = np.linspace(0.26 * minimum, 0.50 * minimum, 10)

        best: tuple[float, float, float, float] | None = None
        for center_y in center_rows:
            for center_x in center_cols:
                for radius in radii:
                    score = self._proposal_score(gray, edge, center_y, center_x, radius)
                    if best is None or score > best[0]:
                        best = (score, center_y, center_x, radius)

        if best is None:
            return [_full_frame_candidate(gray)]

        score, center_y, center_x, radius = best
        if score < 0.50:
            return [_full_frame_candidate(gray, confidence=0.60)]

        side = max(24, int(round(2.0 * radius * 1.12)))
        crop = self._square_crop(gray, center_y, center_x, side)
        crop_center = (side - 1) / 2.0
        crop_radius = radius * 0.98
        crop_axis = np.arange(side, dtype=float)
        crop_xx, crop_yy = np.meshgrid(crop_axis, crop_axis)
        crop_mask = (crop_xx - crop_center) ** 2 + (crop_yy - crop_center) ** 2 <= crop_radius**2
        quality = float(np.clip((score - 0.50) / 4.0, 0.0, 1.0))
        confidence = float(0.60 + 0.35 * quality)
        circle_candidate = RoiCandidate(
            image=crop,
            mask=crop_mask,
            confidence=confidence,
            center_x=center_x / max(width - 1, 1),
            center_y=center_y / max(height - 1, 1),
            radius=2.0 * radius / minimum,
        )
        content = _content_square_crop(gray)
        content_candidate = RoiCandidate(
            image=content,
            mask=np.ones(content.shape, dtype=bool),
            confidence=0.70,
            center_x=0.5,
            center_y=0.5,
            radius=0.5,
        )
        return [circle_candidate, content_candidate, _full_frame_candidate(gray, confidence=0.45)]


def _adapter_for_template(template: str) -> _SimilarityAdapter:
    if template == "一维驻波":
        return _StandingWaveAdapter()
    if template == "共振曲线":
        return _CurvePhotoAdapter()
    if template == "圆形克拉尼图形":
        return _CircularPhotoAdapter()
    if template in {"二维驻波", "三角形薄板模态", "矩形克拉尼图形"}:
        return _PlanarPhotoAdapter()
    return _GenericPhotoAdapter()


def _compare_feature_bundles(reference: FeatureBundle, simulation: FeatureBundle) -> MatchMetrics:
    reference_values = np.asarray(reference.values, dtype=float)
    simulation_values = np.asarray(simulation.values, dtype=float)
    simulation_feature = _structural_feature(simulation_values)
    valid_mask = np.logical_and(reference.mask, simulation.mask)
    radius = max(3, reference_values.shape[0] // 16)
    best: tuple[float, float, float] | None = None
    for scale in (0.85, 1.0, 1.15, 1.30):
        reference_feature = _structural_feature(_center_scale(reference_values, scale))
        for dy in _offsets(radius, 3):
            for dx in _offsets(radius, 3):
                ref_view, sim_view, mask_view = _aligned_views(
                    reference_feature,
                    simulation_feature,
                    valid_mask,
                    dy,
                    dx,
                )
                correlation = _masked_correlation(ref_view, sim_view, mask_view)
                overlap = _structure_overlap(ref_view, sim_view, mask_view)
                score = float(np.clip(0.62 * ((correlation + 1.0) / 2.0) + 0.38 * overlap, 0.0, 1.0))
                if best is None or score > best[0]:
                    best = (score, correlation, overlap)
    if best is None:
        return MatchMetrics(0.0, 0.0, 0.0)
    return MatchMetrics(*best)


def _compare_standing_bundles(reference: FeatureBundle, simulation: FeatureBundle) -> MatchMetrics:
    reference_values = np.asarray(reference.values, dtype=float)
    simulation_values = np.asarray(simulation.values, dtype=float)
    mask = np.logical_and(reference.mask, simulation.mask)
    ref_values = reference_values[mask]
    sim_values = simulation_values[mask]
    ref_centered = ref_values - ref_values.mean()
    sim_centered = sim_values - sim_values.mean()
    denominator = np.linalg.norm(ref_centered) * np.linalg.norm(sim_centered)
    correlation = float(np.dot(ref_centered, sim_centered) / max(float(denominator), 1e-9))
    ref_binary = reference_values > np.quantile(ref_values, 0.70)
    sim_binary = simulation_values > np.quantile(sim_values, 0.70)
    intersection = np.logical_and(np.logical_and(ref_binary, sim_binary), mask).sum()
    union = np.logical_and(np.logical_or(ref_binary, sim_binary), mask).sum()
    overlap = float(intersection / max(union, 1))
    score = float(np.clip(0.68 * ((correlation + 1.0) / 2.0) + 0.32 * overlap, 0.0, 1.0))
    return MatchMetrics(score, correlation, overlap)


def _compare_profile_bundles(reference: FeatureBundle, simulation: FeatureBundle) -> MatchMetrics:
    reference_profile = np.asarray(reference.values, dtype=float)
    simulation_profile = np.asarray(simulation.values, dtype=float)
    reference_centered = reference_profile - reference_profile.mean()
    simulation_centered = simulation_profile - simulation_profile.mean()
    denominator = np.linalg.norm(reference_centered) * np.linalg.norm(simulation_centered)
    correlation = float(np.dot(reference_centered, simulation_centered) / max(float(denominator), 1e-9))
    shape_score = float(
        np.clip(1.0 - np.sqrt(np.mean((reference_profile - simulation_profile) ** 2)), 0.0, 1.0)
    )
    peak_distance = abs(int(np.argmax(reference_profile)) - int(np.argmax(simulation_profile))) / max(
        len(reference_profile) - 1, 1
    )
    peak_score = float(np.exp(-8.0 * peak_distance))
    width_score = float(np.exp(-6.0 * abs(_curve_width(reference_profile) - _curve_width(simulation_profile))))
    overlap = float(np.clip(0.55 * shape_score + 0.25 * peak_score + 0.20 * width_score, 0.0, 1.0))
    score = float(np.clip(0.55 * ((correlation + 1.0) / 2.0) + 0.45 * overlap, 0.0, 1.0))
    return MatchMetrics(score, correlation, overlap)


def _compare_with_pipeline(
    photo: np.ndarray,
    template: str,
    primary: int,
    secondary: int,
    resolution: int,
) -> SimilarityResult:
    adapter = _adapter_for_template(template)
    simulation_view = adapter.simulation_view(template, primary, secondary, resolution)
    simulation_features = adapter.extract_features(simulation_view)
    candidates = adapter.detect_roi(photo)
    best: tuple[float, MatchMetrics, NormalizedView] | None = None

    for candidate in candidates:
        reference_view = adapter.normalize(candidate, resolution)
        reference_features = adapter.extract_features(reference_view)
        metrics = adapter.compare(reference_features, simulation_features)
        confidence = float(np.clip(candidate.confidence, 0.0, 1.0))
        adjusted_score = float(metrics.score * (0.98 + 0.02 * confidence))
        if best is None or adjusted_score > best[0]:
            best = (adjusted_score, metrics, reference_view)

    if best is None:
        empty = np.zeros((resolution, resolution), dtype=float)
        return SimilarityResult(0.0, 0.0, 0.0, empty, simulation_view.image)

    score, metrics, reference_view = best
    return SimilarityResult(
        score,
        metrics.correlation,
        metrics.structure_overlap,
        reference_view.image,
        simulation_view.image,
    )


def _curve_profile(image: np.ndarray, resolution: int) -> np.ndarray:
    gray = resize_to(grayscale_image(image), (resolution, resolution))
    margin = max(3, int(round(resolution * 0.08)))
    inner = gray[margin:-margin, margin:-margin]
    candidates: list[tuple[float, np.ndarray]] = []
    for polarity in (inner, 1.0 - inner):
        strength = gaussian_filter(polarity, sigma=(1.2, 1.2))
        row_profile = np.argmax(strength, axis=0).astype(float)
        peak_strength = np.max(strength, axis=0)
        background_strength = np.median(strength, axis=0)
        quality = float(np.median(peak_strength - background_strength))
        candidates.append((quality, row_profile))

    _, profile = max(candidates, key=lambda item: item[0])
    profile = gaussian_filter1d(profile, sigma=2.0)
    response = 1.0 - profile / max(float(inner.shape[0] - 1), 1.0)
    response -= response.min()
    response /= max(float(response.max()), 1e-9)
    return response


def _curve_width(profile: np.ndarray) -> float:
    baseline = float(np.quantile(profile, 0.20))
    threshold = baseline + 0.5 * (float(profile.max()) - baseline)
    above = np.flatnonzero(profile >= threshold)
    if above.size < 2:
        return 0.0
    return float((above[-1] - above[0]) / max(len(profile) - 1, 1))


def compare_experiment_photo(
    photo: np.ndarray,
    template: str,
    primary: int = 3,
    secondary: int = 2,
    resolution: int = 220,
) -> SimilarityResult:
    return _compare_with_pipeline(photo, template, primary, secondary, resolution)


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
