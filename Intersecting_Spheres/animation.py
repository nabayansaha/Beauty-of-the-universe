"""Manim animation: two unit spheres, distance d from 0 → 2, with running avg V."""

from manim import *
import numpy as np

SCALE = 2.8
LENS_COLOR = "#ff6b4a"


def lens_volume(d: float) -> float:
    d = float(np.clip(d, 0.0, 2.0))
    return (PI / 12) * (2 - d) ** 2 * (d + 4)


def avg_volume(d: float) -> float:
    """Mean of V(t) for t ~ Uniform(0, d); equals E[V]=π/2 once d≥2."""
    d = float(np.clip(d, 0.0, 2.0))
    if d < 1e-8:
        return lens_volume(0.0)
    # (1/d) ∫₀ᵈ V = (π/12)(d³/4 - 6d + 16)
    return (PI / 12) * (d**3 / 4 - 6 * d + 16)


class IntersectingSpheres(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-40 * DEGREES, zoom=0.32)
        self.camera.background_color = "#0b1020"

        d_tracker = ValueTracker(0.0)
        # Max d seen so far — avg freezes at π/2 after the first full sweep.
        max_d = ValueTracker(0.0)

        def track_max_d(_mob=None):
            max_d.set_value(max(max_d.get_value(), d_tracker.get_value()))

        d_tracker.add_updater(track_max_d)

        def center_b_pos():
            return RIGHT * d_tracker.get_value() * SCALE

        sphere_a = Sphere(radius=SCALE, resolution=(24, 48))
        sphere_a.set_color(BLUE_B)
        sphere_a.set_opacity(0.15)
        sphere_a.set_stroke(BLUE_C, width=0.5, opacity=0.4)

        sphere_b = Sphere(radius=SCALE, resolution=(24, 48))
        sphere_b.set_color(TEAL_B)
        sphere_b.set_opacity(0.15)
        sphere_b.set_stroke(TEAL_C, width=0.5, opacity=0.4)
        sphere_b.add_updater(lambda m: m.move_to(center_b_pos()))

        # Intersection highlight: orange ellipsoid fitted to the lens bounds.
        lens = Sphere(radius=SCALE, resolution=(20, 40))
        lens.set_color(LENS_COLOR)
        lens.set_opacity(0.75)
        lens.set_stroke(LENS_COLOR, width=0.3, opacity=0.9)
        lens.save_state()

        def update_lens(mob):
            d = float(np.clip(d_tracker.get_value(), 0.0, 2.0))
            dist = d * SCALE
            mob.restore()
            if dist >= 2 * SCALE - 1e-3:
                mob.set_opacity(0.0)
                return
            half = dist / 2.0
            width = max(2 * SCALE - dist, 1e-3)
            r_yz = float(np.sqrt(max(SCALE * SCALE - half * half, 0.0)))
            mob.stretch_to_fit_width(width)
            mob.stretch_to_fit_height(max(2 * r_yz, 1e-3))
            mob.stretch_to_fit_depth(max(2 * r_yz, 1e-3))
            mob.move_to(RIGHT * half)

        lens.add_updater(update_lens)

        center_a = Dot3D(ORIGIN, color=WHITE, radius=0.08)
        center_b = always_redraw(
            lambda: Dot3D(center_b_pos(), color=WHITE, radius=0.08)
        )
        connector = always_redraw(
            lambda: Line3D(
                ORIGIN,
                center_b_pos() if d_tracker.get_value() > 1e-3 else RIGHT * 1e-3 * SCALE,
                color=YELLOW_A,
                thickness=0.04,
            )
        )

        title = Text("Intersecting Unit Spheres", font_size=32, color=WHITE)
        title.to_corner(UL, buff=0.4)

        hud = always_redraw(
            lambda: VGroup(
                Text(f"d = {d_tracker.get_value():.2f}", font_size=32, color=YELLOW_A),
                Text(
                    f"V(d) = {lens_volume(d_tracker.get_value()):.3f}",
                    font_size=32,
                    color=BLUE_A,
                ),
                Text(
                    f"avg V = {avg_volume(max_d.get_value()):.3f}",
                    font_size=32,
                    color=GREEN_A,
                ),
            )
            .arrange(DOWN, aligned_edge=RIGHT, buff=0.18)
            .to_corner(UR, buff=0.4)
        )

        self.add_fixed_in_frame_mobjects(title, hud)
        self.add(sphere_a, sphere_b, lens, center_a, center_b, connector)

        self.begin_ambient_camera_rotation(rate=0.08)
        self.play(
            FadeIn(sphere_a),
            FadeIn(sphere_b),
            FadeIn(lens),
            FadeIn(title),
            run_time=2,
        )
        self.play(d_tracker.animate.set_value(2.0), run_time=14, rate_func=smooth)
        self.wait(1.2)
        self.play(d_tracker.animate.set_value(0.0), run_time=12, rate_func=smooth)
        self.wait(1.5)
        lens.clear_updaters()
        d_tracker.remove_updater(track_max_d)
        self.stop_ambient_camera_rotation()
