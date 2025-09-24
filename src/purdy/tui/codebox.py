# purdy.tui.codebox.py
import random
from copy import deepcopy
from dataclasses import dataclass

from textual_transitions import Curtain

from purdy.content import Code, Document, RenderState
from purdy.renderers.textual import (TextualFormatter, to_textual,
    _CODE_TAG_EXCEPTIONS)
from purdy.tui import animate
from purdy.tui.widgets import CodeWidget
from purdy.tui.tui_content import EscapeText, TextSection
from purdy.tui.typewriter import code_typewriterize, textual_typewriterize

# =============================================================================
# Specs Used to Define The Layout
# =============================================================================

@dataclass
class BoxSpec:
    """Used to describe each text area in the app that will be showing
    code.

    :param width: relative width based on other boxes in the row. For example,
        row_specs=[Box_Spec(2), BoxSpec(1)] results in a single row where the
        first box takes up 2/3rds of the space.

    :param line_number: Starting line number for code displayed in the box.
        Defaults to None

    :param auto_scroll: True to scroll down when content gets added

    :param border: A string specifying which borders are on for this box.
        Expects the letters "t", "b", "l", "r" in any order for turning on the
        top, bottom, left, and right borders respectively. Defaults to no
        borders.
    """
    width: int
    line_number: int = None
    auto_scroll: bool = False
    border: str = ""
    title: str = ""


@dataclass
class RowSpec:
    """Container for a row of :class:`BoxSpec` objects to describe a row in
    the display grid.

    :param height: relative height of this row in comparison to others in the
        grid. For example [RowSpec(2, ...), RowSpec(1,...)] produces two rows
        with the first taking up 2/3rds of the height of the screen.

    :param boxes: a list of :class:`BoxSpec` objects in this row
    """
    height: int
    boxes: list

# =============================================================================
# Code Abstractions
# =============================================================================

class CodeBox:
    def __init__(self, id, row_spec, box_spec):
        self.id = id
        self.box_spec = box_spec
        self.last_after = None

        self.widget = CodeWidget(border=box_spec.border, title=box_spec.title)
        self.widget.styles.row_span = row_spec.height
        self.widget.styles.column_span = box_spec.width

        self.doc = Document()

    def __repr__(self):
        return f"CodeBox({self.id})"

    def update(self, content):
        self.widget.code_display.update(content)

        if self.box_spec.auto_scroll:
            # Scroll down without any animation, we're already near the bottom
            self.widget.vs.scroll_end(animate=False)

    def _process_content(self, content):
        if isinstance(content, Code):
            self.last_parser = content.parser

    # === Animation Actions
    #
    # --- Editing Actions
    def append(self, content):
        if isinstance(content, str):
            # If there is already a text section add to it, otherwise create
            # one
            if len(self.doc) > 0 and isinstance(self.doc[-1], TextSection):
                self.doc[-1].lines.append(content)
            else:
                self.doc.append(TextSection(content))
        else:
            # Must be Code
            self.doc.append(content)

        after = to_textual(self.doc)
        animate.cell_list.append(animate.Cell(self, after))
        return self

    def clear(self):
        self.doc = Document()
        animate.cell_list.append(animate.Cell(self, ""))
        return self

    def replace(self, content):
        if isinstance(content, str):
            self.doc = Document(TextSection(content))
        else:
            self.doc = Document(content)

        after = to_textual(self.doc)
        animate.cell_list.append(animate.Cell(self, after))
        return self

    def transition(self, content=None, speed=1):
        if content is None:
            self.doc = Document()
            after = ""
        else:
            if isinstance(content, str):
                self.doc = Document(TextSection(content))
            else:
                self.doc = Document(content)

            after = to_textual(self.doc)

        tx = animate.TransitionCell(self, after, Curtain, {"seconds":speed})
        animate.cell_list.append(tx)
        return self

    # --- Typewriter actions
    def _pre_render(self, future_length=0):
        render_state = RenderState(self.doc, future_length=future_length)

        for section in self.doc:
            formatter = TextualFormatter(section, _CODE_TAG_EXCEPTIONS)
            render_state.formatter = formatter
            section.render(render_state)

        return render_state

    def typewriter(self, code, skip_comments=True, skip_whitespace=True,
            delay=0.13, delay_variance=0.03):
        if not isinstance(code, Code):
            raise ValueError("Code only! Use text_typewriter instead")

        render_state = self._pre_render(len(code.lines))
        steps = code_typewriterize(render_state, code, skip_comments,
            skip_whitespace)

        for step, state in steps:
            if isinstance(step, animate.WaitCell):
                animate.cell_list.append(step)
            else:
                after = deepcopy(render_state.content) + step
                animate.cell_list.append(animate.Cell(self, after))

                match state:
                    case "P":
                        self.pause(delay, delay_variance)
                    case "W":
                        animate.cell_list.append(animate.WaitCell())
                    # fall-through has no action

        # Final value should be the whole thing
        self.doc.append(code)
        render_state = self._pre_render()
        animate.cell_list.append(animate.Cell(self, render_state.content))
        return self

    def text_typewriter(self, content, delay=0.13, delay_variance=0.03):
        if isinstance(content, (str, EscapeText)):
            section = TextSection(content)
        else:
            section = content

        render_state = self._pre_render(len(section.lines))
        steps = textual_typewriterize(render_state, section)

        for step in steps:
            after = deepcopy(render_state.content) + step
            animate.cell_list.append(animate.Cell(self, after))

            self.pause(delay, delay_variance)

        # Final value should be the whole thing
        self.doc.append(section)
        render_state = self._pre_render()
        animate.cell_list.append(animate.Cell(self, render_state.content))
        return self

    # --- GUI Actions
    def move_by(self, amount):
        animate.cell_list.append(animate.MoveByCell(self, amount))
        return self

    def debug(self, content):
        animate.cell_list.append(animate.DebugCell(content))
        return self

    # --- Timing actions
    def pause(self, pause, pause_variance=None):
        if pause_variance is not None:
            pause = random.uniform(pause, pause + pause_variance)

        animate.cell_list.append(animate.PauseCell(pause))
        return self

    def wait(self):
        animate.cell_list.append(animate.WaitCell())
        return self

    # --- Formatting actions
    def set_numbers(self, starting_num):
        if starting_num is None:
            self.doc.line_numbers_enabled = False
            self.doc.starting_line_number = 1
        else:
            self.doc.line_numbers_enabled = True
            self.doc.starting_line_number = starting_num

        after = to_textual(self.doc)

        animate.cell_list.append(animate.Cell(self, after))
        return self

    # --- Highlight actions
    def highlight(self, *args, section_index=None):
        """Issue highlight commands to a :class:`Code` block. See
        :func:`Code.highlight` for details on highlight specifiers.

        :param args: series of highlight specifiers
        :param section_indicator: The index number of the section to apply the
            highlighting to. Defaults to None, meaning use the last section.
            It is up to you to make sure the section is the kind that supports
            highlighting.
        """
        # Turn highlighting on and re-render
        if section_index is None:
            code = self.doc[-1]
        else:
            code = self.doc[section_index]

        code.highlight(*args)
        after = to_textual(self.doc)

        animate.cell_list.append(animate.Cell(self, after))
        return self

    def highlight_chain(self, *args, section_index=None):
        """Issue a series of highlight commands in sequence. Highlights the
        first, waits, turns it off, then highlights the next. Only works with
        :class:`Code` blocks. See :func:`Code.highlight` for details on
        highlight specifiers.

        :param args: series of highlight specifiers. Each argument can also
            be a list to activate a set of highlight specifiers together
        :param section_indicator: The index number of the section to apply the
            highlighting to. Defaults to None, meaning use the last section.
            It is up to you to make sure the section is the kind that supports
            highlighting.
        """
        # Turn highlighting on and re-render
        if section_index is None:
            code = self.doc[-1]
        else:
            code = self.doc[section_index]

        for arg in args:
            if isinstance(arg, list):
                specifiers = arg
            else:
                specifiers = [arg]

            code.highlight(*specifiers)
            after = to_textual(self.doc)
            animate.cell_list.append(animate.Cell(self, after))
            animate.cell_list.append(animate.WaitCell())

            code.highlight_off(*specifiers)
            after = to_textual(self.doc)
            animate.cell_list.append(animate.Cell(self, after))

        return self

    def highlight_off(self, *args, section_index=None):
        """Issue highlight_off commands to a :class:`Code` block. See
        :func:`Code.highlight_off` for details on highlight specifiers.

        :param args: series of highlight specifiers. Each argument can also
            be a list to deactivate a set of highlight specifiers together
        :param section_indicator: The index number of the section to apply the
            highlighting to. Defaults to None, meaning use the last section.
            It is up to you to make sure the section is the kind that supports
            highlighting.
        """
        # Turn highlighting off and re-render
        if section_index is None:
            code = self.doc[-1]
        else:
            code = self.doc[section_index]

        code.highlight_off(*args)
        after = to_textual(self.doc)

        animate.cell_list.append(animate.Cell(self, after))
        return self

    def highlight_all_off(self):
        """Removes all highlighting from all :class:`Code` containers"""
        # Turn all highlighting off and re-render
        for section in self.doc:
            if isinstance(section, Code):
                section.highlight_all_off()

        after = to_textual(self.doc)
        animate.cell_list.append(animate.Cell(self, after))
        return self
