"""
Wigets (purdy.wigets.py)
========================

Widgets for displaying. These are called and managed through the Screen
classes in :mod:`purdy.ui`.

"""
import urwid

# =============================================================================
# Widgets
# =============================================================================

class DividingLine(urwid.Filler):
    tab_focusable = False

    def __init__(self):
        divider = urwid.Divider('-')

        super(DividingLine, self).__init__(divider)

# -----------------------------------------------------------------------------
# CodeWidget -- box that displays code

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

    def keypress(self, size, key):
        if key == 'up' and self.focus_position == 0:
            # don't want arrow up to change parent's focus, eat this key
            return None

        if key == 'down' and self.focus_position + 1 >= len(self.body):
            # don't want arrow down to change parent's focus, eat this key
            return None

        return super().keypress(size, key)


class CodeWidget(urwid.Columns):
    """Urwid widget that displays the code. This implements the methods of
    :class:`purdy.content.RenderHook` and is registered against a
    :class:`purdy.ui.CodeBox` and :class:`purdy.content.Listing`. As changes
    are made to the listing they will be rendered this widget.

    The widget wraps an urwid ListBox, with each line in the box being a line
    of code. It also provides indiciators on the right side of the screen as
    to whether there is content above or below the current screen. If the
    parent :class:`Screen` implementation has multiple instances of this class
    active, the scroll area will also indicate which code box is focused. 

    The up and down arrows as well as the page-up and page-down buttons are
    supported. If there are multiple code widgets, tab key will change the
    focus.
    """
    tab_focusable = True

    # CodeWidget is a Column collection containing a ListBox of Text for the
    # code and a side bar with indicators about focus and scroll position
    def __init__(self, screen, auto_scroll):
        """Constructor. These objects should only be constructed by a parent
        :class:`Screen` object.

        :param screen: the :class:`Screen` building this code box
        """
        self.screen = screen
        self.auto_scroll = auto_scroll

        # urwid does weird things when trying to focus an empty listing, never
        # allow it to be empty
        self.is_empty = True
        self.walker = urwid.SimpleListWalker([urwid.Text(''), ])

        scroller = ScrollingIndicator()
        self.listbox = ScrollingListBox(scroller, self.walker)

        layout = [self.listbox, (1, scroller)]

        super(CodeWidget, self).__init__(layout)

    #--- RenderHook methods
    def line_inserted(self, listing, position, line):
        markup = listing.render_line(line)
        index = position - 1

        if self.is_empty:
            self.walker.contents[0] = urwid.Text(markup)
            self.is_empty = False
        else:
            self.walker.contents.insert(index, urwid.Text(markup))

        if self.auto_scroll:
            # if auto scrolling, change focus to last inserted item
            self.listbox.set_focus(index)

    def line_removed(self, listing, position):
        if len(self.walker.contents) == 1:
            self.is_empty = True
            self.walker.contents[0] = urwid.Text('')
        else:
            del self.walker.contents[position - 1]

        # urwid crashes if the focus is set outside of the range and you
        # try to do other operations to the box before returning to the
        # event loop, fix this by setting the focus to the last item
        size = len(self.walker.contents)
        if size > 0:
            self.listbox.set_focus(size - 1)

    def line_changed(self, listing, position, line):
        markup = listing.render_line(line)
        index = position - 1
        self.walker.contents[index].set_text(markup)

        if self.auto_scroll:
            # if auto scrolling, change focus to last inserted item, needed in
            # case the line height has change
            self.listbox.set_focus(index)

    def clear(self):
        self.is_empty = True
        self.walker.contents.clear()
        self.walker.contents.insert(0, urwid.Text(''))


class TwinContainer(urwid.Columns):
    ### A column with the tab_focusable attribute so the BaseWindow class
    # knows to do tab focus changes on it
    tab_focusable = True
