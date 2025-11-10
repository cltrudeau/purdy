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
    """Contains and controls content to be displayed to the screen. Wraps the
    display widget and includes the action methods for the purdy
    animations."""

    def __init__(self, id, row_spec, box_spec):
        self.id = id
        self.box_spec = box_spec
        self.last_after = None

        self.widget = CodeWidget(border=box_spec.border, title=box_spec.title)
        self.widget.styles.row_span = row_spec.height
        self.widget.styles.column_span = box_spec.width

        self.doc = Document()

        if box_spec.line_number is not None:
            self.doc.line_numbers_enabled = True
            self.doc.starting_line_number = box_spec.line_number

    def __repr__(self):
        return f"CodeBox({self.id})"

    def update(self, content, ignore_auto_scroll=False):
        """Updates the content of the widget, typically shouldn't be called
        directly."""
        self.widget.code_display.update(content)

        if not ignore_auto_scroll and self.box_spec.auto_scroll:
            # Scroll down without any animation, we're already near the bottom
            self.widget.vs.scroll_end(animate=False)

    def _process_content(self, content):
        if isinstance(content, Code):
            self.last_parser = content.parser

    # === Animation Actions
    #
    # --- Editing Actions
    def append(self, content):
        """Action: appends content to the :class:`CodeBox`

        :param content: Textual Markup,
            :class:`~purdy.tui.tui_content.EscapeText`, or a
            :class:`~purdy.content.Code` object

        :returns: this :class:`CodeBox` so action calls can be chained
        """
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
        """Action: wipes this :class:`CodeBox`

        :returns: this :class:`CodeBox` so action calls can be chained
        """
        self.doc = Document()
        animate.cell_list.append(animate.Cell(self, ""))
        return self

    def replace(self, content):
        """Action: replaces the content in this :class:`CodeBox` with that
        provided

        :param content: Textual Markup,
            :class:`~purdy.tui.tui_content.EscapeText`, or a
            :class:`~purdy.content.Code` object

        :returns: this :class:`CodeBox` so action calls can be chained
        """
        if isinstance(content, str):
            self.doc = Document(TextSection(content))
        else:
            self.doc = Document(content)

        after = to_textual(self.doc)
        animate.cell_list.append(animate.Cell(self, after))
        return self

    def transition(self, content=None, speed=1):
        """Action: performs a transition wipe animation then replaces the
        content in this :class:`CodeBox` with that provided

        :param content: Textual Markup,
            :class:`~purdy.tui.tui_content.EscapeText`, or a
            :class:`~purdy.content.Code` object

        :returns: this :class:`CodeBox` so action calls can be chained
        """
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

    def prompt(self, prompt, answer, animate_answer=True,
            delay=0.13, delay_variance=0.03):
        """Appends two pieces of Textual markup into the :class:`CodeBox`,
        first the prompt value, then waits, then animates the typing of the
        answer value.  The answer appears on the same line as the prompt
        unless you explicitly include a newline.

        .. warning:: This method only accepts Textual markup. It does not support EscapedText. Text with markup characters will need to be escaped manually

        :param prompt: text to prompt with
        :param answer: the answer to append
        :param animate_answer: when True (default) use a typewriter animation
            for the answer
        :param delay: Length of time to sleep between characters. Defaults to
            0.13 seconds
        :param delay_variance: amount of random variability in the typing
            delay. Defaults to 0.03 seconds

        :returns: this :class:`CodeBox` so action calls can be chained
        """
        # Explicit type check seeing as EscapeText inherits from str
        if not type(prompt) is str:
            raise ValueError("Prompt must strictly be a string")
        if not type(answer) is str:
            raise ValueError("Answer must strictly be a string")

        # If there is already a text section add to it, otherwise create one
        if len(self.doc) > 0 and isinstance(self.doc[-1], TextSection):
            self.doc[-1].lines.append(prompt)
        else:
            self.doc.append(TextSection(prompt))

        # Add the prompt
        after = to_textual(self.doc)
        animate.cell_list.append(animate.Cell(self, after))
        animate.cell_list.append(animate.WaitCell())

        if not animate_answer:
            # Don't animate the answer
            self.doc[-1].lines[-1] += answer
            after = to_textual(self.doc)
            animate.cell_list.append(animate.Cell(self, after))
            return self

        # Add the answer typing animation: put the prompt in a section for the
        # animation calculation, then just use the what it returns
        section = TextSection(answer)
        render_state = self._pre_render(len(section.lines))
        steps = textual_typewriterize(render_state, section)

        for step in steps:
            # Append, subtracting the newline
            after = deepcopy(render_state.content)[:-1] + step.text
            animate.cell_list.append(animate.Cell(self, after))
            self.pause(delay, delay_variance)

        # Final value should be the whole thing
        self.doc[-1].lines[-1] += answer
        render_state = self._pre_render()
        animate.cell_list.append(animate.Cell(self, render_state.content))
        return self

    def typewriter(self, code, skip_comments=True, skip_whitespace=True,
            delay=0.13, delay_variance=0.03):
        """Action: performs a typing animation with the content in given
        :class:`~purdy.content.Code` object. Note that unlike most actions
        this one does not support Textual Markup, use
        :func:`CodeBox.text_typewriter` for that instead.

        :param code: :class:`~purdy.content.Code` content to animate
        :param skip_comments: When True (default) a comment is animated as a
            single item instead of typing it
        :param skip_whitespace: When True (default) any block of whitespace is
            treated as a single item instead of each character within it
        :param delay: Length of time to sleep between characters. Defaults to
            0.13 seconds
        :param delay_variance: amount of random variability in the typing
            delay. Defaults to 0.03 seconds

        :returns: this :class:`CodeBox` so action calls can be chained
        """
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
        """Action: performs a typing animation on Textual Markup or
        :class:`~purdy.tui.tui_content.EscapeText`.

        :param content: Content to animate
        :param delay: Length of time to sleep between characters. Defaults to
            0.13 seconds
        :param delay_variance: amount of random variability in the typing
            delay. Defaults to 0.03 seconds

        :returns: this :class:`CodeBox` so action calls can be chained
        """
        if isinstance(content, (str, EscapeText)):
            section = TextSection(content)
        else:
            section = content

        render_state = self._pre_render(len(section.lines))
        steps = textual_typewriterize(render_state, section)

        for step in steps:
            after = deepcopy(render_state.content) + step.text
            animate.cell_list.append(animate.Cell(self, after))

            self.pause(delay, delay_variance)

        # Final value should be the whole thing
        self.doc.append(section)
        render_state = self._pre_render()
        animate.cell_list.append(animate.Cell(self, render_state.content))
        return self

    # --- GUI Actions
    def move_by(self, amount):
        """Action: scrolls this :class:`CodeBox` by the given amount

        :param amount: number of characters to scroll down, supports negative
            numbers for scrolling up

        :returns: this :class:`CodeBox` so action calls can be chained
        """
        animate.cell_list.append(animate.MoveByCell(self, amount))
        return self

    def debug(self, content):
        animate.cell_list.append(animate.DebugCell(content))
        return self

    # --- Timing actions
    def pause(self, pause, pause_variance=None):
        """Action: pause before next animation

        :param pause: seconds to pause for
        :param pause_variance: random amount to vary the pause by, defaults to
            None

        :returns: this :class:`CodeBox` so action calls can be chained
        """
        if pause_variance is not None:
            pause = random.uniform(pause, pause + pause_variance)

        animate.cell_list.append(animate.PauseCell(pause))
        return self

    def wait(self):
        """Action: wait for a right arrow or skip command before proceeding to
        the next animation

        :returns: this :class:`CodeBox` so action calls can be chained
        """
        animate.cell_list.append(animate.WaitCell())
        return self

    # --- Formatting actions
    def set_numbers(self, starting_num):
        """Action: turn line numbering on for this :class:`CodeBox`

        :param starting_num: value to start the numbering with

        :returns: this :class:`CodeBox` so action calls can be chained
        """
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
        """Action: issue highlight commands to a :class:`~purdy.content.Code`
        block. See inside of this :class:`CodeBox`. See
        :func:`~purdy.content.Code.highlight` for details on highlight
        specifiers.

        :param args: series of highlight specifiers
        :param section_indicator: Each thing added to the :class:`CodeBox` is
            considered a section. This argument specifies the index of the
            section to apply the highlighting to. Defaults to None, meaning
            use the last section.  It is up to you to make sure the section is
            the kind that supports highlighting.
        """
        # Turn highlighting on and re-render
        if section_index is None:
            code = self.doc[-1]
        else:
            code = self.doc[section_index]

        code.highlight(*args)
        after = to_textual(self.doc)

        animate.cell_list.append(animate.Cell(self, after,
            ignore_auto_scroll=True))
        return self

    def highlight_chain(self, *args, section_index=None):
        """Action: Issue a series of highlight commands in sequence.
        Highlights the first, waits, turns it off, then highlights the next.
        Only works with :class:`~purdy.content.Code` blocks. See
        :func:`~purdy.content.Code.highlight` for details on highlight
        specifiers.

        :param args: series of highlight specifiers. Each argument can also
            be a list to activate a set of highlight specifiers together
        :param section_indicator: Each thing added to the :class:`CodeBox` is
            considered a section. This argument specifies the index of the
            section to apply the highlighting to. Defaults to None, meaning
            use the last section.  It is up to you to make sure the section is
            the kind that supports highlighting.

        :returns: this :class:`CodeBox` so action calls can be chained
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
            animate.cell_list.append(animate.Cell(self, after,
                ignore_auto_scroll=True))
            animate.cell_list.append(animate.WaitCell())

            code.highlight_off(*specifiers)
            after = to_textual(self.doc)
            animate.cell_list.append(animate.Cell(self, after,
                ignore_auto_scroll=True))

        return self

    def highlight_off(self, *args, section_index=None):
        """Issue highlight_off commands to a :class:`~purdy.content.Code`
        block. See :func:`~purdy.content.Code.highlight_off` for details on
        highlight specifiers.

        :param args: series of highlight specifiers. Each argument can also
            be a list to deactivate a set of highlight specifiers together
        :param section_indicator: The index number of the section to apply the
            highlighting to. Defaults to None, meaning use the last section.
            It is up to you to make sure the section is the kind that supports
            highlighting.

        :returns: this :class:`CodeBox` so action calls can be chained
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
        """Action: remove highlighting from all :class:`~purdy.content.Code`
        sections within this :class:`CodeBox`

        :returns: this :class:`CodeBox` so action calls can be chained
        """
        # Turn all highlighting off and re-render
        for section in self.doc:
            if isinstance(section, Code):
                section.highlight_all_off()

        after = to_textual(self.doc)
        animate.cell_list.append(animate.Cell(self, after,
            ignore_auto_scroll=True))
        return self
