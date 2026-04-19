"""
Core paradigm logic: Display visual cues and record keyboard responses.

This module provides a simple reaction time paradigm where:
1. A fixation cross is shown
2. After a random delay, a colored cue appears
3. The participant presses a key as fast as possible
4. Both cue onset and key press are sent as LSL markers
"""

import random
import time
from dataclasses import dataclass, field

import pyglet
from pylsl import StreamInfo, StreamOutlet
from typing import Optional
from fire import Fire
from myparadigm.utils.logging import logger


# deactivate debug for optimal performance
pyglet.options["debug_gl"] = False


@dataclass
class TrialConfig:
    """Configuration for a single trial."""

    n_trials: int = 10
    cue_duration: float = 0.5  # seconds
    min_delay: float = 1.0  # minimum delay before cue
    max_delay: float = 3.0  # maximum delay before cue
    response_keys: list[str] = field(default_factory=lambda: ["space"])


# Note: This is a very simple example. In a more complex or time-critical application
#       you would want to optimize the drawing code, e.g. by grouping shapes into batches,
#       pre-rendering static elements, etc.
def draw_fixation(window: pyglet.window.Window) -> None:  # type: ignore
    """Draw a fixation cross at the center of the window."""
    cx, cy = window.width // 2, window.height // 2
    size = 50
    pyglet.shapes.Line(
        cx - size, cy, cx + size, cy, thickness=3, color=(255, 255, 255)
    ).draw()
    pyglet.shapes.Line(
        cx, cy - size, cx, cy + size, thickness=3, color=(255, 255, 255)
    ).draw()


def draw_cue(window: pyglet.window.Window) -> None:  # type: ignore
    """Draw a green circle cue at the center of the window."""
    cx, cy = window.width // 2, window.height // 2
    radius = 50
    pyglet.shapes.Circle(cx, cy, radius, color=(0, 255, 0)).draw()


def draw_reaction_time(window: pyglet.window.Window, rt: float) -> None:  # type: ignore
    """Draw the reaction time as text feedback."""
    label = pyglet.text.Label(
        f"RT: {rt:.3f} s",
        font_size=44,
        x=window.width // 2,
        y=window.height // 2 - 100,
        anchor_x="center",
        anchor_y="center",
    )
    label.draw()


def draw_instructions(window: pyglet.window.Window) -> None:  # type: ignore
    """Draw instructions for the participant."""
    instructions = (
        "Welcome to the Reaction Time Paradigm!\n\n"
        "Instructions:\n"
        "1. Focus on the fixation cross.\n"
        "2. After a random delay, a green circle will appear.\n"
        "3. Press the SPACE key as quickly as possible when you see the circle.\n"
        "4. Your reaction time will be displayed after each trial.\n\n"
        "\n"
        "Press Space key to start. Press ESC to exit at any time."
    )
    label = pyglet.text.Label(
        instructions,
        font_size=44,
        x=window.width // 2,
        y=window.height // 2,
        anchor_x="center",
        anchor_y="center",
        multiline=True,
        width=1000,
    )
    label.draw()


class Paradigm:
    """
    Visual cue paradigm with keyboard response recording.

    Parameters
    ----------
    stream_name : str
        Name of the LSL marker stream to create.
    config : TrialConfig, optional
        Trial configuration parameters.
    """

    def __init__(
        self, stream_name: str = "paradigm_markers", config: TrialConfig | None = None
    ):
        self.stream_name = stream_name
        self.config = config or TrialConfig()
        self.outlet: Optional[StreamOutlet] = None
        self.window: Optional[pyglet.window.Window] = None  # type: ignore
        self._running = False
        self._trial_idx = 0
        self._state = "instruction"  # instruction, fixation, cue, response
        self._cue_onset_time: float = 0.0
        self.last_reaction_time: float = 0.0

        self.last_frame: float = 0.0

    def _setup_lsl(self) -> None:
        """Create LSL marker stream outlet."""
        info = StreamInfo(
            name=self.stream_name,
            type="Markers",
            channel_count=1,
            nominal_srate=0,  # irregular rate
            channel_format="string",  # type: ignore
            source_id=f"{self.stream_name}_paradigm",
        )
        self.outlet = StreamOutlet(info)

    def _send_marker(self, marker: str) -> None:
        """Send a marker to the LSL stream."""
        if self.outlet:
            self.outlet.push_sample([marker])

        # also log the marker
        logger.info(f"Sent marker: {marker}")

    def _create_window(self) -> None:
        """Create the pyglet window."""

        # double buffer for accurate main loop frames >> Note: Optimal performance for the mainloop / screen rendering
        # will be system/OS specific. Always test and optimize for your setup. This is just a reasonable default.
        config = pyglet.gl.Config(double_buffer=True, depth_size=16)

        self.window = pyglet.window.Window(
            width=1200,
            height=800,
            resizable=True,
            # fullscreen=True,
            caption="Reaction Time Paradigm",
            config=config,
        )

        # ----------------------------------------------------------------------
        # register `on_draw` event handler: called whenever the window needs
        #   to be redrawn this is where we render the current screen output
        #   depending on the state of the paradigm (instruction, fixation, cue,
        #   feedback)
        # ----------------------------------------------------------------------

        @self.window.event  # type: ignore
        def on_draw():
            self._on_draw()

        # ----------------------------------------------------------------------
        # register `on_key_press` event handler: called whenever a key press
        # ----------------------------------------------------------------------

        @self.window.event  # type: ignore
        def on_key_press(symbol, modifiers):
            self._on_key_press(symbol)

    def _on_draw(self) -> None:
        """Render the current state."""
        self.window.clear()  # type: ignore
        now = time.perf_counter()
        logger.debug(
            f"Drawing state: {self._state}, frame_time_s={now - self.last_frame:.4f}"
        )
        self.last_frame = now

        match self._state:
            case "instructions":
                draw_instructions(self.window)
            case "fixation":
                draw_fixation(self.window)
            case "cue":
                draw_cue(self.window)
            case "response":
                draw_reaction_time(self.window, self.last_reaction_time)

    def _on_key_press(self, symbol: int) -> None:
        """Handle key press events."""
        key_name = pyglet.window.key.symbol_string(symbol).lower()
        logger.info(f"Key pressed: {key_name} in state {self._state}")

        if key_name == "escape":
            self.stop()
            return

        if self._state == "cue" and key_name in self.config.response_keys:
            self.last_reaction_time = time.perf_counter() - self._cue_onset_time
            self._send_marker(
                f"response,key={key_name},rt={self.last_reaction_time:.4f}"
            )
            self._state = "response"
            pyglet.clock.schedule_once(lambda dt: self._next_trial(), 0.5)

        if (
            self._state == "instructions" and key_name in "space"
        ):  # transition to fixation
            self._state = "fixation"
            pyglet.clock.schedule_once(self._start_trial, 0.5)

    def _start_trial(self, dt: float = 0) -> None:
        """Start a new trial with fixation."""
        if not self._running or self._trial_idx >= self.config.n_trials:
            self.stop()
            return

        self._state = "fixation"
        self._send_marker(f"trial_start,trial={self._trial_idx}")

        # Schedule cue onset after random delay
        delay = random.uniform(self.config.min_delay, self.config.max_delay)
        pyglet.clock.schedule_once(self._show_cue, delay)

    def _show_cue(self, dt: float) -> None:
        """Show the visual cue."""
        self._state = "cue"
        self._cue_onset_time = time.perf_counter()
        self._send_marker(f"cue_onset,trial={self._trial_idx}")

        # Schedule timeout if no response
        pyglet.clock.schedule_once(self._timeout, self.config.cue_duration + 2.0)

    def _timeout(self, dt: float) -> None:
        """Handle response timeout."""
        if self._state == "cue":
            self._send_marker(f"timeout,trial={self._trial_idx}")
            self._next_trial()

    def _next_trial(self) -> None:
        """Move to the next trial."""
        self._trial_idx += 1
        pyglet.clock.unschedule(self._timeout)  # no longer check for the timeout
        pyglet.clock.schedule_once(self._start_trial, 1.0)  # start the next trial

    def run(self, n_trials: int | None = None) -> int:
        """
        Run the paradigm.

        Parameters
        ----------
        n_trials : int, optional
            Number of trials to run. Overrides config if provided.
        """
        if n_trials is not None:
            self.config.n_trials = n_trials

        self._setup_lsl()
        self._create_window()
        self._running = True
        self._trial_idx = 0

        self._send_marker("paradigm_start")
        self._state = "instructions"
        pyglet.app.run()

        return 0  # we will call the run method via the Dareplane wrapper. Such functions should either return int, tuple[threading.Thread, threading.Event], or subprocess.Popen.

    def stop(self) -> None:
        """Stop the paradigm."""
        self._running = False
        self._send_marker("paradigm_end")
        pyglet.app.exit()
        if self.window:
            self.window.close()


def cli(n_trials: int = 3, log_level: str = "INFO"):
    logger.setLevel(log_level.upper())
    paradigm = Paradigm()
    paradigm.run(n_trials=n_trials)


if __name__ == "__main__":
    # Quick test run
    Fire(cli)
