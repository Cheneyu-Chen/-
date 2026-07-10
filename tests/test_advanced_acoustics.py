from __future__ import annotations

import unittest

import numpy as np

from app.core.advanced_acoustics import single_slit_diffraction_frame


class SingleSlitDiffractionFrameTest(unittest.TestCase):
    def test_returns_named_arrays_and_geometry(self) -> None:
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
        self.assertEqual(frame["screen_x"].shape, frame["screen_intensity"].shape)
        self.assertGreaterEqual(float(np.min(frame["screen_intensity"])), 0.0)
        self.assertLessEqual(float(np.max(frame["screen_intensity"])), 1.0)

    def test_screen_intensity_changes_with_time_phase(self) -> None:
        frame_a = single_slit_diffraction_frame(
            frequency=800.0,
            slit_width=0.35,
            screen_distance=2.5,
            sound_speed=343.0,
            time_phase=0.0,
            resolution=120,
        )
        frame_b = single_slit_diffraction_frame(
            frequency=800.0,
            slit_width=0.35,
            screen_distance=2.5,
            sound_speed=343.0,
            time_phase=0.25,
            resolution=120,
        )

        self.assertNotAlmostEqual(
            float(frame_a["field"][60, 80]),
            float(frame_b["field"][60, 80]),
        )
        self.assertGreater(
            float(np.max(np.abs(frame_a["screen_intensity"] - frame_b["screen_intensity"]))),
            1e-3,
        )
