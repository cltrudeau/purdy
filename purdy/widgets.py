"""
Wigets (purdy.wigets.py)
------------------------

Widgets for displaying. These are called and managed through the Screen
classes in :mod:`purdy.ui`.

"""

import urwid

from purdy.content import TokenLookup

# =============================================================================
# Widgets
# =============================================================================

class AppendableText(urwid.AttrMap):
    ### Text-like widget that supports highlighting

    def __init__(self, markup):
        self.text_widget = urwid.Text('')
        self.set_text(markup)
        super(AppendableText, self).__init__(self.text_widget, 'empty')

    def set_text(self, markup):
        # urwid.Text supports three formats for markup: 1) plain text, 2)
        # tuple of palette attribute name and text, or 3) a list contain items
        # which are #1 or #2; to make things easier, convert it to a list
        self.markup = markup
        if isinstance(markup, str) or isinstance(markup, tuple):
            self.markup = [markup]

        self.text_widget.set_text(self.markup)

    def append(self, markup):
        self.markup.append(markup)
        self.set_text(self.markup)

    def set_highlight(self, highlight):
        if highlight:
            from purdy.ui import highlight_mapper
            self.set_attr_map(highlight_mapper)
        else:
            self.set_attr_map({})

# -----------------------------------------------------------------------------

class DividingLine(urwid.Filler):
    tab_focusable = False

    def __init__(self):
        divider = urwid.Divider('-')
        super(DividingLine, self).__init__(divider, valign='top', top=1, 
            bottom=1)

# -----------------------------------------------------------------------------
# Code Box -- box that displays code

class ScrollingIndicator(urwid.Frame):
    def __init__(self):
        self.up = urwid.Text(' ')
        self.down = urwid.Text(' ')

        # create this Frame with a solid fill in the middle and the up and
        # down Text widgets as the header and footer
        super(ScrollingIndicator, self).__init__(urwid.SolidFill(' '), 
            header=self.up, footer=self.down)

    def set_up(self, is_up, focus):
        if is_up and focus:
            self.up.set_text('▲')
        elif is_up and not focus:
            self.up.set_text('△')
        else:
            self.down.set_text(' ')

    def set_down(self, is_down, focus):
        if is_down and focus:
            self.down.set_text('▼')
        elif is_down and not focus:
            self.down.set_text('▽')
        else:
            self.down.set_text(' ')

    def set_focus_only(self, focus):
        if focus: 
            self.up.set_text('▮')
        else: 
            self.up.set_text('▯')


class ScrollingListBox(urwid.ListBox):
    def __init__(self, scroll_indicator, *args, **kwargs):
        self.scroll_indicator = scroll_indicator
        super(ScrollingListBox, self).__init__(*args, **kwargs)

    def render(self, size, focus):
        result = super(ScrollingListBox, self).render(size, focus)

        # ends_visible() returns a list with the words "top" and/or "bottom"
        # in it if the top and/or bottom of the list box is visible
        #
        # set our scrolling indicators based on what is visible
        visible = self.ends_visible(size)
        if 'top' in visible and 'bottom' in visible:
            self.scroll_indicator.set_focus_only(focus)
        else:
            self.scroll_indicator.set_up('top' not in visible, focus)
            self.scroll_indicator.set_down('bottom' not in visible, focus)

        return result


class CodeBox(urwid.Columns):
    """Widget that displays the code. Actions use the methods in this class to
    change the text being displayed.

    The widget wraps an urwid ListBox, with each line in the box being a line
    of code. It also provides indiciators on the right side of the screen as
    to whether there is content above or below the current screen. If the
    parent :class:`Screen` implementation has multiple instances of this class
    active, the scroll area will also indicate which code box is focused. 

    The up and down arrows as well as the page-up and page-down buttons are
    supported. If there are multiple code boxes, tab key will change the
    focus.

    Each line of the code box displays text through the :class:`urwid.Text`
    widget. The methods in the this class for displaying content use urwid's
    markup tuple for determing the appearance of text. If you are writing new
    actions, you generally don't need to understand the markup language, just
    pass in the :class:`CodeLine.markup <purdy.content.CodeLine>` 
    attribute from the line in your :class:`Code <purdy.content.Code>` object.
    """
    tab_focusable = True

    # CodeBox is ListBox of Text with code in it accompanied by a side bar
    # with indicators about focus and scroll position
    def __init__(self, screen, show_line_numbers, auto_scroll):
        """Constructor. These objects should only be constructed by a parent
        :class:`Screen` object.

        :param screen: the :class:`Screen` building this code box

        :param show_line_numbers: True if this box is to display line numbers
        """
        self.screen = screen
        self.show_line_numbers = show_line_numbers
        self.line_number = 1
        self.auto_scroll = auto_scroll
        self.body = urwid.SimpleListWalker([])

        scroller = ScrollingIndicator()
        self.listbox = ScrollingListBox(scroller, self.body)

        layout = [self.listbox, (1, scroller)]

        super(CodeBox, self).__init__(layout)

    def clear(self):
        # clears the list and starts fresh
        self.body.contents.clear() 

    def get_markup(self, position):
        """Returns the markup at the given position (removes any line numbers
        first.

        :returns: markup at the given position (1-indexed)
        """
        markup = self.body.contents[position - 1].markup

        if self.show_line_numbers:
            # remove the first tuple with the line number in it
            markup = markup[1:]

        return markup

    # --- Add Lines
    def add_line(self, markup=['']):
        """Appends an empty line to the end of the code listing

        :param markup: markup to put in the line, defaults to empty
        """
        self.add_line_at(len(self.body.contents) + 1, markup)

    def add_line_at(self, position, markup=['']):
        """Inserts a new empty line in the code box

        :param position: line number to insert at (1-indexed), pushes any
            existing content down; i.e. position=1 inserts at the top of the
            list
        :param markup: markup to put in the newly inserted line, defaults to
                       empty
        """
        if self.show_line_numbers:
            markup = [TokenLookup.line_number_markup(position), ] +  markup

        self.body.contents.insert(position - 1, AppendableText(markup))

        # scroll to the new content
        if self.auto_scroll:
            self.listbox.set_focus(position - 1)

    def fix_line_numbers(self, position):
        """Fixes line numbers after adding new lines to the code box"""
        line_no = position
        for widget in self.body.contents[line_no - 1:]:
            markup = widget.markup

            # this should only be called in show_line_numbers mode, so we can
            # assume that the first part of the markup is the line number
            # chunk
            #
            # re-build the markup, replacing the line number chunk with a new
            # one
            text = TokenLookup.line_number_markup(line_no)
            new_markup = [text, ] + markup[1:]
            widget.set_text(new_markup)

            line_no += 1

    # --- Change lines
    def set_last_line(self, markup):
        """Changes the last line in the code box to have the given markup 

        :param markup: new markup tuple for the line
        """
        self.body.contents[-1].set_text(markup)

    def set_line(self, position, markup):
        """Changes the given line in the code box to have the given markup 

        :param position: line number to change (1-indexed)
        :param markup: new markup tuple for the line
        """
        if self.show_line_numbers:
            markup = [TokenLookup.line_number_markup(position), ] + list(markup)

        self.body.contents[position - 1].set_text(markup)


class TwinContainer(urwid.Columns):
    tab_focusable = True
