# purdy.tui.codebox.py
import random
from dataclasses import dataclass

from pygments.token import Generic
from textual.content import Content
from textual.markup import escape as textual_escape
from textual_transitions import Curtain

from purdy.content import Code, MultiCode
from purdy.parser import token_is_a
from purdy.renderers.textual import to_textual
from purdy.tui import animate
from purdy.tui.widgets import CodeWidget
from purdy.typewriter import (code_typewriterize, string_typewriterize,
    textual_typewriterize)

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
# Code Abstraction
# =============================================================================

class TText(str):
    def render(self):
        return Content.from_markup(self)


class Document:
    """Container for things being displayed in a :class:`CodeBox`."""
    def __init__(self):
        self.items = []

    def append(self, content):
        if isinstance(content, Code):
            if not self.items:
                # Empty
                self.items.append(MultiCode(content))
            elif isinstance(self.items[-1], MultiCode):
                # Last thing is MultiCode
                self.items[-1].extend(content)
            else:
                # Last thing wasn't MultiCode, need new MultiCode
                self.items.append(MultiCode(content))
        elif isinstance(content, TText):
            self.items.append(content)
        elif isinstance(content, str):
            self.items.append(content)
        else:
            raise ValueError("Unrecognizable content")

    def replace(self, content):
        if isinstance(content, Code):
            self.items = [MultiCode(content), ]
        elif isinstance(content, TText):
            self.items = [content, ]
        elif isinstance(content, str):
            self.items = [content, ]
        else:
            raise ValueError("Unrecognizable content")

    def render(self):
        result = ""
        for item in self.items:
            if isinstance(item, MultiCode):
                result += to_textual(item)
            elif isinstance(item, TText):
                result += item.render()
            elif isinstance(item, str):
                text = textual_escape(item)
                result += Content.from_markup(text)
            else:
                raise ValueError(f"Unrecognizable content in doc {item}")

        return result

# -----------------------------------------------------------------------------

class CodeBox:
    def __init__(self, row_spec, box_spec):
        self.box_spec = box_spec
        self.last_after = None

        self.holder = CodeWidget(border=box_spec.border)
        self.holder.styles.row_span = row_spec.height
        self.holder.styles.column_span = box_spec.width

        self.doc = Document()

    def __repr__(self):
        return "CodeBox()"

    def update(self, content):
        self.holder.code_display.update(content)

        if self.box_spec.auto_scroll:
            # Scroll down without any animation, we're already near the bottom
            self.holder.vs.scroll_end(animate=False)

    def _process_content(self, content):
        if isinstance(content, Code):
            self.last_parser = content.parser

    # === Animation Actions
    #
    # --- Editing Actions
    def append(self, content):
        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        self.doc.append(content)
        after = self.doc.render()
        animate.cell_list.append(animate.Cell(self, before, after))
        self.last_after = after
        return self

    def clear(self):
        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        self.doc = Document()
        animate.cell_list.append(animate.Cell(self, before, ""))
        self.last_after = ""
        return self

    def replace(self, content):
        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        self.doc.replace(content)
        after = self.doc.render()
        animate.cell_list.append(animate.Cell(self, before, after))
        self.last_after = after
        return self

    def transition(self, content=None, speed=1):
        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        self.doc = Document()
        if content is None:
            self.doc = Document()
            after = ""
        else:
            self.doc.append(content)
            after = self.doc.render()

        tx = animate.TransitionCell(self, before, after, Curtain,
            {"seconds":speed})
        animate.cell_list.append(tx)
        self.last_after = after
        return self

    # --- Typewriter actions
    def typewriter(self, content, skip_comments=True, skip_whitespace=True,
            delay=0.13, delay_variance=0.03):
        if not isinstance(content, Code):
            raise ValueError("Code only! Use text_typewriter instead")

        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        self.doc.append(content)
        typewriter_steps = code_typewriterize(content, skip_comments,
            skip_whitespace)

        # Adding the content to the doc made sure there was a MultiCode as the
        # last item, remove the last Code object from it, and then iterate
        # through each of the typewriter versions with it
        del self.doc.items[-1][-1]
        for code in typewriter_steps:
            self.doc.items[-1].append(code)
            after = self.doc.render()
            animate.cell_list.append(animate.Cell(self, before, after))

            if token_is_a(code.lines[-1].parts[-1].token, Generic.Prompt):
                # Wait at prompts, pause at everything else
                self.wait()
            else:
                self.pause(delay, delay_variance)

            before = after
            del self.doc.items[-1][-1]

        # Add the content back in after the last pass of the for-loop
        self.doc.append(content)
        self.last_after = after
        return self

    def text_typewriter(self, content, delay=0.13, delay_variance=0.03):
        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        if isinstance(content, TText):
            results = textual_typewriterize(content)
            for item in results:
                self.doc.append(TText(item))
                after = self.doc.render()
                animate.cell_list.append(animate.Cell(self, before, after))

                self.pause(delay, delay_variance)

                # Will replace the last item next time through
                before = after
                del self.doc.items[-1]

            # Final value should be the whole thing
            self.doc.append(TText(content))
            after = self.doc.render()
        else: # Should be a plain string
            results = string_typewriterize(content)
            for item in results:
                self.doc.append(item)
                after = self.doc.render()
                animate.cell_list.append(animate.Cell(self, before, after))

                self.pause(delay, delay_variance)

                # Will replace the last item next time through
                before = after
                del self.doc.items[-1]

            # Final value should be the whole thing
            self.doc.append(content)
            after = self.doc.render()

        self.last_after = after
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

    # --- Highlight actions
    def _code_from_container_indicator(self, container_indicator):
        ### See `highlight` docstring for explanation on container_indicator
        if container_indicator is None:
            # Assume last thing in doc is a MultiCode object and use its last
            # `Code` object
            return self.doc.items[-1][-1]
        elif isinstance(container_indicator, int):
            return self.doc.items[-1][container_indicator]

        # else: tuple indicating index of MultiCode and index of Code within it
        return self.doc.items[container_indicator[0]][container_indicator[1]]

    def highlight(self, *args, container_indicator=None):
        """Issue highlight commands to a :class:`Code` block. See
        :func:`Code.highlight` for details on highlight specifiers.

        There can be multiple :class:`MultiCode` objects in the rendering
        document, and multiple :class:`Code` objects within the `MultiCode`.
        Use `container_indicator` to specify which `Code` block to apply the
        highlighting to. It defaults to `None`. For `None` or an integer, it
        assumes the last item in the document is a `MultiCode` object and
        either uses the last `Code` object in it, or the one given by the
        number. You can also pass in a tuple containing an index into the
        document and an index into the `MultiCode` object to reference.

        :param args: series of highlight specifiers
        :param container_indicator: which `Code` block to highlight

        """
        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        # Turn highlighting on and re-render
        code = self._code_from_container_indicator(container_indicator)
        code.highlight(*args)
        after = self.doc.render()

        animate.cell_list.append(animate.Cell(self, before, after))
        self.last_after = after
        return self

    def highlight_off(self, *args, container_indicator=None):
        """Issue highlight_off commands to a :class:`Code` block. See
        :func:`Code.highlight_off` for details on highlight specifiers.

        There can be multiple :class:`MultiCode` objects in the rendering
        document, and multiple :class:`Code` objects within the `MultiCode`.
        Use `container_indicator` to specify which `Code` block to apply the
        highlighting to. It defaults to `None`. For `None` or an integer, it
        assumes the last item in the document is a `MultiCode` object and
        either uses the last `Code` object in it, or the one given by the
        number. You can also pass in a tuple containing an index into the
        document and an index into the `MultiCode` object to reference.

        :param args: series of highlight specifiers
        :param container_indicator: which `Code` block to highlight

        """
        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        # Turn highlighting off and re-render
        code = self._code_from_container_indicator(container_indicator)
        code.highlight_off(*args)
        after = self.doc.render()

        animate.cell_list.append(animate.Cell(self, before, after))
        self.last_after = after
        return self

    def highlight_all_off(self):
        """Removes all highlighting from all :class:`MultiCode` containers"""
        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        # Turn all highlighting off and re-render
        for item in self.doc.items:
            if isinstance(item, MultiCode):
                for code in item:
                    code.highlight_all_off()

        after = self.doc.render()

        animate.cell_list.append(animate.Cell(self, before, after))
        self.last_after = after
        return self
