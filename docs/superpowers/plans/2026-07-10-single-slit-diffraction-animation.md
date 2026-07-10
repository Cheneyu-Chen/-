# 单缝声衍射动态图 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把进阶声学里的“单缝声衍射”改成可播放的动态图，直观展示声波穿过缝口并逐步形成衍射条纹的过程。

**Architecture:** 保留 `AdvancedAcousticsPage` 的参数面板和交互入口，只重做单缝模式的右侧绘图区域。把衍射过程的数学计算下沉到 `app/core/advanced_acoustics.py` 的纯函数里，页面层负责按时间帧组装上半区传播动画和下半区屏幕显影图，并继续复用现有的播放、暂停、重置、导出逻辑。

**Tech Stack:** Python, PySide6, NumPy, Matplotlib

---

### Task 1: Add a failing unit test for the single-slit frame data

**Files:**
- Create: `physics/tests/test_advanced_acoustics.py`
- Modify: `physics/app/core/advanced_acoustics.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from app.core.advanced_acoustics import single_slit_diffraction_frame


class SingleSlitDiffractionFrameTest(unittest.TestCase):
    def test_returns_geometry_and_field_data(self) -> None:
        frame = single_slit_diffraction_frame(
            frequency=800.0,
            slit_width=0.35,
            screen_distance=2.5,
            sound_speed=343.0,
            time_phase=0.25,
            resolution=120,
        )

        self.assertIn("xx", frame)
        self.assertIn("yy", frame)
        self.assertIn("field", frame)
        self.assertIn("screen_x", frame)
        self.assertIn("screen_intensity", frame)
        self.assertIn("wavefront_phase", frame)
        self.assertEqual(frame["field"].shape, frame["xx"].shape)
        self.assertEqual(frame["field"].shape, frame["yy"].shape)
        self.assertGreaterEqual(frame["screen_intensity"].min(), 0.0)
        self.assertLessEqual(frame["screen_intensity"].max(), 1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests -v`
Expected: `ImportError` or `AttributeError` because `single_slit_diffraction_frame` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
def single_slit_diffraction_frame(
    frequency: float,
    slit_width: float,
    screen_distance: float,
    sound_speed: float,
    time_phase: float,
    resolution: int = 240,
):
    import numpy as np

    x = np.linspace(-2.0, 2.0, resolution)
    y = np.linspace(0.0, max(screen_distance, 0.2), resolution)
    xx, yy = np.meshgrid(x, y)
    field = np.zeros_like(xx)
    screen_x = np.linspace(-2.0, 2.0, resolution)
    screen_intensity = np.zeros_like(screen_x)
    return {
        "xx": xx,
        "yy": yy,
        "field": field,
        "screen_x": screen_x,
        "screen_intensity": screen_intensity,
        "wavefront_phase": float(time_phase),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest physics.tests.test_advanced_acoustics.SingleSlitDiffractionFrameTest.test_returns_geometry_and_field_data -v`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git -C physics add app/core/advanced_acoustics.py tests/test_advanced_acoustics.py
git -C physics commit -m "test: add single-slit diffraction frame coverage"
```

### Task 2: Implement the real single-slit diffraction frame calculation

**Files:**
- Modify: `physics/app/core/advanced_acoustics.py`
- Modify: `physics/tests/test_advanced_acoustics.py`

- [ ] **Step 1: Extend the test with physics checks**

```python
def test_field_changes_with_time_phase(self) -> None:
    frame_a = single_slit_diffraction_frame(800.0, 0.35, 2.5, 343.0, 0.0, 120)
    frame_b = single_slit_diffraction_frame(800.0, 0.35, 2.5, 343.0, 0.5, 120)

    self.assertNotEqual(
        float(frame_a["field"][60, 80]),
        float(frame_b["field"][60, 80]),
    )
    self.assertGreater(frame_a["screen_intensity"].max(), 0.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests -v`
Expected: failure because the stub returns all zeros.

- [ ] **Step 3: Write the real implementation**

```python
def single_slit_diffraction_frame(
    frequency: float,
    slit_width: float,
    screen_distance: float,
    sound_speed: float,
    time_phase: float,
    resolution: int = 240,
):
    import numpy as np

    x = np.linspace(-2.5, 2.5, resolution)
    y = np.linspace(0.0, max(screen_distance, 0.2), resolution)
    xx, yy = np.meshgrid(x, y)

    wavelength = sound_speed / max(frequency, 1e-6)
    wave_number = 2.0 * np.pi / max(wavelength, 1e-9)
    obstacle_y = max(screen_distance * 0.22, 0.35)
    slit_half = max(slit_width / 2.0, 0.02)

    aperture_count = max(21, int(60 * slit_width))
    aperture_x = np.linspace(-slit_half, slit_half, aperture_count)
    aperture_y = np.full_like(aperture_x, obstacle_y)

    field = np.zeros_like(xx, dtype=np.complex128)
    for sx, sy in zip(aperture_x, aperture_y):
        rr = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
        rr = np.maximum(rr, 0.05)
        field += np.exp(1j * (wave_number * rr - 2.0 * np.pi * time_phase)) / np.sqrt(rr)

    field = np.real(field)
    field /= max(float(np.max(np.abs(field))), 1e-9)

    screen_x = np.linspace(-2.5, 2.5, resolution)
    screen_y = np.full_like(screen_x, screen_distance)
    screen_field = np.zeros_like(screen_x, dtype=np.complex128)
    for sx, sy in zip(aperture_x, aperture_y):
        rr = np.sqrt((screen_x - sx) ** 2 + (screen_y - sy) ** 2)
        rr = np.maximum(rr, 0.05)
        screen_field += np.exp(1j * (wave_number * rr - 2.0 * np.pi * time_phase)) / np.sqrt(rr)

    screen_intensity = np.abs(screen_field) ** 2
    screen_intensity /= max(float(np.max(screen_intensity)), 1e-9)

    wavefront_phase = float((time_phase % 1.0))
    return {
        "xx": xx,
        "yy": yy,
        "field": field,
        "screen_x": screen_x,
        "screen_intensity": screen_intensity,
        "wavefront_phase": wavefront_phase,
        "wavelength": wavelength,
        "obstacle_y": obstacle_y,
        "slit_half": slit_half,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m unittest physics.tests.test_advanced_acoustics -v`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git -C physics add app/core/advanced_acoustics.py tests/test_advanced_acoustics.py
git -C physics commit -m "feat: add single-slit diffraction frame model"
```

### Task 3: Replace the single-slit plot area with a two-panel animation

**Files:**
- Modify: `physics/app/pages/advanced_acoustics_page.py`

- [ ] **Step 1: Write the failing GUI-side smoke test**

```python
import unittest

from app.pages.advanced_acoustics_page import AdvancedAcousticsPage


class AdvancedAcousticsPageSmokeTest(unittest.TestCase):
    def test_single_slit_controls_still_exist(self) -> None:
        page = AdvancedAcousticsPage()
        self.assertTrue(hasattr(page, "experiment_box"))
        self.assertTrue(hasattr(page, "freq_spin"))
        self.assertTrue(hasattr(page, "param_a"))
        self.assertTrue(hasattr(page, "param_b"))
        self.assertTrue(hasattr(page, "canvas"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests -v`
Expected: may fail until the page still imports and constructs after the refactor.

- [ ] **Step 3: Rewrite the single-slit branch**

```python
if experiment == "单缝声衍射":
    self.label_a.setText("缝宽 a / m")
    self.label_b.setText("屏距 L / m")
    self.param_b.setEnabled(True)
    self.param_a.setRange(0.02, 1.2)
    self.param_b.setRange(0.5, 8.0)
    self._plot_diffraction_animation(fig)
```

```python
def _plot_diffraction_animation(self, fig) -> None:
    data = single_slit_diffraction_frame(
        self.freq_spin.value(),
        self.param_a.value(),
        self.param_b.value(),
        self._current_sound_speed(),
        self.time_value,
    )
    fig.clear()
    ax_top, ax_bottom = fig.subplots(2, 1, height_ratios=[2.0, 1.0])
    ...
```

Use the top axis for wavefront propagation and the bottom axis for the screen intensity build-up. Keep the existing `QTimer` methods and reuse `refresh_plot()` so the page still behaves like the other animated pages.

- [ ] **Step 4: Run the app and verify the page updates**

Run: `python -m app.main`
Expected: the single-slit page opens with animated propagation instead of a static diffraction heatmap.

- [ ] **Step 5: Commit**

```bash
git -C physics add app/pages/advanced_acoustics_page.py
git -C physics commit -m "feat: animate single-slit diffraction page"
```

### Task 4: Verify the full flow and clean up any layout issues

**Files:**
- Modify: `physics/app/pages/advanced_acoustics_page.py`
- Modify: `physics/app/core/advanced_acoustics.py`
- Modify: `physics/tests/test_advanced_acoustics.py`

- [ ] **Step 1: Run the full unit test module**

Run: `python -m unittest discover -s tests -v`
Expected: all tests pass.

- [ ] **Step 2: Run a manual startup check**

Run: `python -m app.main`
Expected: no import errors, no canvas exceptions, and the single-slit mode animates smoothly.

- [ ] **Step 3: Tidy labels and axis titles**

```python
self.param_hint.setText("参数 A：缝宽 a / m；参数 B：屏距 L / m。动画展示的是衍射形成过程，不是实时录音数据。")
```

Ensure titles, legends, and summary text do not overlap on the resized two-panel layout.

- [ ] **Step 4: Commit**

```bash
git -C physics add app/core/advanced_acoustics.py app/pages/advanced_acoustics_page.py tests/test_advanced_acoustics.py
git -C physics commit -m "refactor: finish single-slit diffraction animation"
```

## Spec Coverage Check

- 参数面板保留：Task 3
- 动态展示衍射形成过程：Task 2, Task 3
- 屏幕条纹逐步形成：Task 2, Task 3
- 播放/暂停/重置/导出保持可用：Task 3
- 不影响其它进阶声学模式：Task 3, Task 4
