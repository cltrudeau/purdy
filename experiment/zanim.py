#!/usr/bin/env python
import asyncio
import random

from dataclasses import dataclass
from enum import Enum

from rich.color import Color
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment, Segments
from rich.style import Style, StyleType

from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Vertical, VerticalScroll
from textual.widgets import Static
from textual.worker import WorkerState

from textual_effects import Curtain

# ===========================================================================
# Animation Cells
# ===========================================================================

@dataclass
class Cell:
    box: 'typing.Any'
    before: str
    after: str


@dataclass
class PauseCell:
    pause: float


class WaitCell:
    pass


class TransitionCell:
    def __init__(self, box, before, after, overlay, effect_holder, effect_cls,
            effect_kwargs):
        self.box = box
        self.before = before
        self.after = after
        self.overlay = overlay
        self.effect_holder = effect_holder
        self.effect_cls = effect_cls
        self.effect_kwargs = effect_kwargs

    async def run(self, control):
        self.effect = self.effect_cls(self.effect_holder,
            callback=self.callback, post_callback=control.curtain_complete,
            **self.effect_kwargs)
        self.overlay.mount(self.effect)
        self.worker = control.app.run_worker(self.effect.run(), exclusive=True)

    async def cancel(self):
        self.worker.cancel()
        self.effect.remove()
        self.box.update(self.after)

    async def callback(self):
        self.box.update(self.after)

# ===========================================================================
# Animation Control
# ===========================================================================

class CellManager(list):
    def __init__(self):
        self.app = app
        self.last_after = {}

    def append_cell(self, box, content):
        if len(self) != 0 and box in self.last_after:
            before = self.last_after[box]
        else:
            before = ""

        after = before + content
        self.append(Cell(box, before, after))
        self.last_after[box] = after
        return self

    def replace_cell(self, box, content):
        if len(self) != 0 and box in self.last_after:
            before = self.last_after[box]
        else:
            before = ""

        after = content
        self.append(Cell(box, before, after))
        self.last_after[box] = after
        return self

    def curtain_cell(self, box, content, overlay, effect_holder):
        if len(self) != 0 and box in self.last_after:
            before = self.last_after[box]
        else:
            before = ""

        after = content
        cell = TransitionCell(box, before, after, overlay, effect_holder,
            Curtain, {"color":"red"})
        self.append(cell)
        self.last_after[box] = after
        return self

    def pause_cell(self, pause, pause_variance=None):
        if pause_variance is not None:
            pause = random.uniform(pause, pause + pause_variance)

        self.append(PauseCell(pause))
        return self

    def wait_cell(self):
        self.append(WaitCell())
        return self


class Control:
    class State(Enum):
        PAUSE = "p"
        TRANSITION = "t"
        WAIT = "w"
        DONE = "d"

    def __init__(self, app, cell_manager):
        self.app = app
        self.cell_manager = cell_manager
        self.current = None
        self.worker = None
        self.wait_state = None

        # Find the first Wait cell in our collection
        self.first_wait = None
        for index, cell in enumerate(cell_manager):
            if isinstance(cell, WaitCell):
                self.first_wait = index
                break

    # --- Coroutines
    async def pause_running(self, amount):
        await asyncio.sleep(amount)
        self.wait_state = None
        print("woke from pause")

        await self.forwards()

    async def curtain_complete(self):
        # Called by Curtain effect when it is done
        self.wait_state = None
        print("curtain complete")
        await self.forwards()

    async def forwards(self):
        if self.current is not None and self.current >= len(self.cell_manager):
            # Ignore call, we're done
            return

        if self.wait_state in [self.State.PAUSE, self.State.TRANSITION]:
            # Ignore forwards during pause or animations, make them use skip
            return

        while True:
            if self.current is None:
                # Haven't started yet, initialize
                self.current = -1

            # Current cell is the last one to do something, increment
            self.current += 1
            if self.current >= len(self.cell_manager):
                # All cells processed, can exit the worker
                print("ran out of cells")
                self.state = self.State.DONE
                return

            cell = self.cell_manager[self.current]
            print("Top of loop:", cell, self.wait_state)

            if isinstance(cell, PauseCell):
                # Pause directive, kick off the timer and leave
                print("hit pause")
                self.wait_state = self.State.PAUSE
                self.worker = self.app.run_worker(
                    self.pause_running(cell.pause))
                return
            elif isinstance(cell, TransitionCell):
                print("hit transition")
                self.wait_state = self.State.TRANSITION
                await cell.run(self)
                return
            elif isinstance(cell, WaitCell):
                # Wait until the next time forwards is called
                print("hit wait")
                self.wait_state = self.State.WAIT
                return
            else:
                # Perform cell action
                self.wait_state = None
                cell.box.update(cell.after)

    async def skip(self):
        if self.current is not None and self.current >= len(self.cell_manager):
            return

        if self.wait_state == self.State.PAUSE:
            self.worker.cancel()
            self.wait_state = None

        if self.wait_state == self.State.TRANSITION:
            cell = self.cell_manager[self.current]
            await cell.cancel()
            self.wait_state = None

        while True:
            if self.current is None:
                # Haven't started yet, initialize
                self.current = -1

            # Current cell is the last one to do something, increment
            self.current += 1
            if self.current >= len(self.cell_manager):
                # All cells processed, can exit the worker
                print("ran out of cells")
                self.state = self.State.DONE
                return

            cell = self.cell_manager[self.current]
            if isinstance(cell, PauseCell):
                # Ignore pauses during skip
                continue
            if isinstance(cell, TransitionCell):
                # Skip animation, but perform replacement
                cell.box.update(cell.after)
                continue
            elif isinstance(cell, WaitCell):
                # Skipping done
                self.wait_state = self.State.WAIT
                return
            else:
                # Perform cell actions
                self.wait_state = None
                cell.box.update(cell.after)

    async def backwards(self):
        print("backwards()", self.current)
        if self.current is None:
            # Can't go backwards when nothing ever started
            return

        if self.wait_state == self.State.PAUSE:
            self.worker.cancel()
        elif self.wait_state == self.State.DONE:
            # We were done, undo to the previous wait
            self.current = len(self.cell_manager) - 1

        start = self.current - 1
        if start < 0:
            # First state was a Wait, that's weird, let's ignore it
            return

        end = 0
        if self.first_wait is not None:
            end = self.first_wait

        for self.current in range(start, end, -1):
            cell = self.cell_manager[self.current]
            print("   undoing", cell)
            if isinstance(cell, PauseCell):
                # Ignore pauses during backwards
                print("Skipping pause")
                continue
            elif isinstance(cell, WaitCell):
                # Done moving backwards, set to next cell
                self.wait_state = self.State.WAIT
                print("Hit previous wait", self.current)
                return
            else:
                # Perform cell actions. TransitionCells get handled here as
                # well, as they don't animate going backwards
                self.wait_state = None
                cell.box.update(cell.before)
                print("Did undo")

# ===========================================================================
# App
# ===========================================================================

class ZAnimate(App):
    CSS = """
        VerticalScroll {
            height: 10;
            border: solid white;
        }

        #effect_holder {
            layers: below above;
            height: 10;
        }

        #box_holder {
            layer: below;
        }

        .box {
            layer: below;
        }

        #overlay {
            layer: above;
            visibility: hidden;
        }
    """
    def __init__(self):
        super().__init__()
        self.count = 0
        self.content = ""

    def compose(self) -> ComposeResult:
        with Container(id="effect_holder") as self.effect_holder:
            self.overlay = Container(id="overlay")
            yield self.overlay

            with Container(id="box_holder") as self.box_holder:
                with VerticalScroll():
                    self.box1 = Static("", classes="box")
                    yield self.box1

        with VerticalScroll():
            self.box2 = Static("")
            yield self.box2

        manager = CellManager()
        (manager
            .append_cell(self.box1, "123\n")
            .append_cell(self.box2, "abc\n")
            .wait_cell()

            .append_cell(self.box1, "456\n")
            .replace_cell(self.box2, "def\n")
            .wait_cell()

            .curtain_cell(self.box1, "789\n", self.overlay, self.effect_holder)
            .replace_cell(self.box2, "")
            .append_cell(self.box2, "A\n")
            .pause_cell(1)
            .append_cell(self.box2, "B\n")
            .pause_cell(1)
            .append_cell(self.box2, "C\n")
            .pause_cell(1)
            .append_cell(self.box2, "D\n")
            .pause_cell(1)
            .append_cell(self.box2, "E\n")
            .wait_cell()

            .append_cell(self.box1, "fin\n")
            .append_cell(self.box2, "ished\n")
        )

        self.control = Control(self, manager)

    async def on_mount(self):
        # Activate up to the first wait point (has to be here rather than
        # compose() because the call is async)
        await self.control.forwards()

    async def on_key(self, event):
        key = event.key
        if key == "q":
            exit()
        elif key == "right":
            await self.control.forwards()
        elif key == "left":
            await self.control.backwards()
        elif key == "s":
            await self.control.skip()


if __name__ == "__main__":
    app = ZAnimate()
    app.run()
