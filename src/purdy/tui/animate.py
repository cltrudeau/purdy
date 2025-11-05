# purdy.tui.animate.py
import asyncio
import typing

from dataclasses import dataclass
from enum import Enum

from textual.content import Content as TContent

# ===========================================================================
# Cells and Cell Management
#
# These define the possible steps that can happen during screen animation

def _content_to_repr(content):
    if isinstance(content, TContent):
        return f"Content({repr(content.markup)}), "

    return f"str({content}), "


class UndoableCell:
    def __init__(self, ignore_auto_scroll=False):
        self.ignore_auto_scroll = ignore_auto_scroll
        self.forwards_map = {}
        self.backwards_map = {}

    def forwards(self):
        for codebox, after in self.forwards_map.items():
            codebox.update(after, self.ignore_auto_scroll)

    def backwards(self):
        for codebox, back in self.backwards_map.items():
            codebox.update(back)


class Cell(UndoableCell):
    def __init__(self, codebox, after, ignore_auto_scroll=False):
        super().__init__(ignore_auto_scroll)
        self.codebox = codebox
        self.forwards_map[self.codebox] = after

    @property
    def after(self):
        return self.forwards_map[self.codebox]

    @property
    def before(self):
        try:
            return self.backwards_map[self.codebox]
        except:
            return ""

    def __repr__(self):
        result = f"Cell(codebox={self.codebox.id}, after="
        result += _content_to_repr(self.after)
        result += " before="
        result += _content_to_repr(self.before)

        return result


@dataclass
class MoveByCell:
    codebox: typing.Any
    amount: int


@dataclass
class PauseCell:
    pause: float


class WaitCell:
    pass


@dataclass
class DebugCell:
    content: str


class TransitionCell(UndoableCell):
    def __init__(self, codebox, after, effect_cls, effect_kwargs):
        super().__init__()
        self.codebox = codebox
        self.forwards_map[self.codebox] = after
        self.effect_cls = effect_cls
        self.effect_kwargs = effect_kwargs

    def __repr__(self):
        result = f"TransitionCell(codebox={self.codebox.id}, after="
        result += _content_to_repr(self.forwards_map[self.codebox])
        result += " before="
        result += _content_to_repr(self.before)

        return result

    @property
    def before(self):
        try:
            return self.backwards_map[self.codebox]
        except:
            return ""

    async def run(self, animation_controller):
        container = self.codebox.widget.container
        overlay = self.codebox.widget.overlay

        self.effect = self.effect_cls(container, callback=self.callback,
            post_callback=animation_controller.transition_complete,
            **self.effect_kwargs)
        overlay.mount(self.effect)
        self.worker = animation_controller.app.run_worker(self.effect.run(),
            exclusive=True)

    async def cancel(self):
        self.worker.cancel()
        self.effect.remove()
        self.forwards()

    async def callback(self):
        self.forwards()
        self.codebox.widget.vs.scroll_to(y=0, animate=False)


class ScreenTransitionCell(UndoableCell):
    def __init__(self, control, changes, effect_cls, effect_kwargs):
        super().__init__()
        self.control = control
        self.effect_cls = effect_cls
        self.effect_kwargs = effect_kwargs

        for codebox, after in changes.items():
            self.forwards_map[codebox] = after

    async def run(self, animation_controller):
        container = self.control.container.inner
        overlay = self.control.container.overlay

        self.effect = self.effect_cls(container, callback=self.callback,
            post_callback=animation_controller.transition_complete,
            **self.effect_kwargs)
        overlay.mount(self.effect)
        self.worker = animation_controller.app.run_worker(self.effect.run(),
            exclusive=True)

    async def cancel(self):
        self.worker.cancel()
        self.effect.remove()
        self.forwards()

    async def callback(self):
        self.forwards()

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

        # Loop through and calculate the "before" states, also mark the first
        # Wait cell in our collection
        self.first_wait = None
        before_cells = {}
        for index, cell in enumerate(cell_list):
            if isinstance(cell, WaitCell) and self.first_wait is None:
                # Found first wait
                self.first_wait = index

            if isinstance(cell, UndoableCell):
                for codebox in cell.forwards_map.keys():
                    if codebox in before_cells:
                        prev = before_cells[codebox]
                        cell.backwards_map[codebox] = prev.forwards_map[codebox]

                    before_cells[codebox] = cell

    # --- Coroutines
    async def pause_running(self, amount):
        await asyncio.sleep(amount)
        self.wait_state = None
        await self.forwards()

    async def transition_complete(self):
        # Called by transition effect when it is done
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

            if isinstance(cell, DebugCell):
                # Ignore it
                continue
            elif isinstance(cell, MoveByCell):
                cell.codebox.widget.vs.scroll_relative(y=cell.amount,
                    speed=15)
                continue
            elif isinstance(cell, PauseCell):
                # Pause directive, kick off the timer and leave
                self.wait_state = self.State.PAUSE
                self.worker = self.app.run_worker(
                    self.pause_running(cell.pause))
                return
            elif isinstance(cell, TransitionCell):
                self.wait_state = self.State.TRANSITION
                await cell.run(self)
                return
            elif isinstance(cell, ScreenTransitionCell):
                self.wait_state = self.State.TRANSITION
                await cell.run(self)
                return
            elif isinstance(cell, WaitCell):
                # Wait until the next time forwards is called
                self.wait_state = self.State.WAIT
                return

            # Perform cell action
            self.wait_state = None
            cell.forwards()
            self.app.set_focus(cell.codebox.widget.vs)

    async def skip(self):
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
            if isinstance(cell, DebugCell):
                # Ignore it
                continue
            elif isinstance(cell, MoveByCell):
                cell.codebox.widget.vs.scroll_relative(y=cell.amount,
                    animate=False)
                continue
            elif isinstance(cell, PauseCell):
                # Ignore pauses during skip
                continue
            if isinstance(cell, (ScreenTransitionCell, TransitionCell)):
                # Skip animation, but perform replacement
                cell.forwards()
                continue
            elif isinstance(cell, WaitCell):
                # Skipping done
                self.wait_state = self.State.WAIT
                return

            # Perform cell actions
            self.wait_state = None
            cell.forwards()
            self.app.set_focus(cell.codebox.widget.vs)

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
        if start >= len(cell_list):
            start = len(cell_list) - 1

        end = 0
        if self.first_wait is not None:
            end = self.first_wait

        print("***", start, end, len(cell_list))
        for self.current in range(start, end - 1, -1):
            cell = cell_list[self.current]
            if isinstance(cell, DebugCell):
                # Ignore it
                continue
            elif isinstance(cell, MoveByCell):
                scroll_by = -1 * cell.amount
                cell.codebox.widget.vs.scroll_relative(y=scroll_by)
                continue
            if isinstance(cell, PauseCell):
                # Ignore pauses during backwards
                continue
            elif isinstance(cell, WaitCell):
                # Done moving backwards, set to next cell
                self.wait_state = self.State.WAIT
                return

            # Perform cell actions. TransitionCells get handled here as
            # well, as they don't animate going backwards
            self.wait_state = None
            cell.backwards()
            self.app.set_focus(cell.codebox.widget.vs)

# ===========================================================================

# Module level container for cell actions
cell_list = []
