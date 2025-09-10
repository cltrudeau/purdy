# purdy.tui.animate.py
import asyncio
import typing

from dataclasses import dataclass
from enum import Enum

# ===========================================================================
# Cells and Cell Management
#
# These define the possible steps that can happen during screen animation

@dataclass
class Cell:
    codebox: typing.Any  # should be CodeBox, but that causes a circular
                         # reference and pyflakes doesn't handle string based
                         # typing, so once again, pretending Python can have
                         # type safety is just so much fun
    before: str
    after: str


@dataclass
class PauseCell:
    pause: float


class WaitCell:
    pass


class TransitionCell:
    def __init__(self, codebox, before, after, effect_cls, effect_kwargs):
        self.codebox = codebox
        self.before = before
        self.after = after
        self.effect_cls = effect_cls
        self.effect_kwargs = effect_kwargs

    async def run(self, control):
        effect_holder = self.codebox.holder.effect_holder
        overlay = self.codebox.holder.overlay

        self.effect = self.effect_cls(effect_holder, callback=self.callback,
            post_callback=control.curtain_complete, **self.effect_kwargs)
        overlay.mount(self.effect)
        self.worker = control.app.run_worker(self.effect.run(), exclusive=True)

    async def cancel(self):
        self.worker.cancel()
        self.effect.remove()
        self.codebox.update(self.after)

    async def callback(self):
        self.codebox.update(self.after)

# ===========================================================================
# Animation Controller
# ===========================================================================

class AnimationController:
    class State(Enum):
        PAUSE = "p"
        TRANSITION = "t"
        WAIT = "w"
        DONE = "d"

    def __init__(self, app):
        self.app = app
        self.current = None
        self.worker = None
        self.wait_state = None

        # Find the first Wait cell in our collection
        self.first_wait = None
        for index, cell in enumerate(cell_list):
            if isinstance(cell, WaitCell):
                self.first_wait = index
                break

    # --- Coroutines
    async def pause_running(self, amount):
        await asyncio.sleep(amount)
        self.wait_state = None
        await self.forwards()

    async def curtain_complete(self):
        # Called by Curtain effect when it is done
        self.wait_state = None
        await self.forwards()

    async def forwards(self):
        if self.current is not None and self.current >= len(cell_list):
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
            if self.current >= len(cell_list):
                # All cells processed, can exit the worker
                self.state = self.State.DONE
                return

            cell = cell_list[self.current]

            if isinstance(cell, PauseCell):
                # Pause directive, kick off the timer and leave
                self.wait_state = self.State.PAUSE
                self.worker = self.app.run_worker(
                    self.pause_running(cell.pause))
                return
            elif isinstance(cell, TransitionCell):
                self.wait_state = self.State.TRANSITION
                await cell.run(self)
                return
            elif isinstance(cell, WaitCell):
                # Wait until the next time forwards is called
                self.wait_state = self.State.WAIT
                return
            else:
                # Perform cell action
                self.wait_state = None
                cell.codebox.update(cell.after)

    async def skip(self):
        if self.current is not None and self.current >= len(cell_list):
            return

        if self.wait_state == self.State.PAUSE:
            self.worker.cancel()
            self.wait_state = None

        if self.wait_state == self.State.TRANSITION:
            cell = cell_list[self.current]
            await cell.cancel()
            self.wait_state = None

        while True:
            if self.current is None:
                # Haven't started yet, initialize
                self.current = -1

            # Current cell is the last one to do something, increment
            self.current += 1
            if self.current >= len(cell_list):
                # All cells processed, can exit the worker
                self.state = self.State.DONE
                return

            cell = cell_list[self.current]
            if isinstance(cell, PauseCell):
                # Ignore pauses during skip
                continue
            if isinstance(cell, TransitionCell):
                # Skip animation, but perform replacement
                cell.codebox.update(cell.after)
                continue
            elif isinstance(cell, WaitCell):
                # Skipping done
                self.wait_state = self.State.WAIT
                return
            else:
                # Perform cell actions
                self.wait_state = None
                cell.codebox.update(cell.after)

    async def backwards(self):
        if self.current is None:
            # Can't go backwards when nothing ever started
            return

        if self.wait_state == self.State.PAUSE:
            self.worker.cancel()
        elif self.wait_state == self.State.DONE:
            # We were done, undo to the previous wait
            self.current = len(cell_list) - 1

        start = self.current - 1
        if start < 0:
            # First state was a Wait, that's weird, let's ignore it
            return

        end = 0
        if self.first_wait is not None:
            end = self.first_wait

        for self.current in range(start, end - 1, -1):
            cell = cell_list[self.current]
            if isinstance(cell, PauseCell):
                # Ignore pauses during backwards
                continue
            elif isinstance(cell, WaitCell):
                # Done moving backwards, set to next cell
                self.wait_state = self.State.WAIT
                return
            else:
                # Perform cell actions. TransitionCells get handled here as
                # well, as they don't animate going backwards
                self.wait_state = None
                cell.codebox.update(cell.before)

# ===========================================================================

# Module level container for cell actions
cell_list = []
