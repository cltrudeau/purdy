"""
Wigets (purdy.wigets.py)
------------------------

Widgets for displaying. These are called and managed through the Screen
classes in :mod:`purdy.ui`.

"""
import urwid

# =============================================================================
# Widgets
# =============================================================================

class DividingLine(urwid.Filler):
    tab_focusable = False

    def __init__(self, compact=False):
        divider = urwid.Divider('-')
        margin = 1
        if compact:
            margin = 0

        super(DividingLine, self).__init__(divider, valign='top', top=margin, 
            bottom=margin)

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
        self.walker = urwid.SimpleListWalker([])

        scroller = ScrollingIndicator()
        self.listbox = ScrollingListBox(scroller, self.walker)

        layout = [self.listbox, (1, scroller)]

        super(CodeWidget, self).__init__(layout)

    #--- RenderHook methods
    def line_appended(self, listing, line):
        markup = listing.render_line(line)
        self.walker.contents.append( TextPlus(markup) )

        if self.auto_scroll:
            # if auto scrolling, change focus to end of list
            position = len(self.walker.contents) - 1
            self.listbox.set_focus(position)

    def line_inserted(self, listing, position, line):
        markup = listing.render_line(line)
        index = position - 1
        self.walker.contents.insert(index, TextPlus(markup))

        if self.auto_scroll:
            # if auto scrolling, change focus to last inserted item
            self.listbox.set_focus(index)

    def line_removed(self, listing, position):
        del self.walker.contents[position - 1]

    def line_changed(self, listing, position, line):
        markup = listing.render_line(line)
        index = position - 1
        self.walker.contents[index].set_text(markup)

    def clear(self):
        self.walker.contents.clear()


class TwinContainer(urwid.Columns):
    ### A column with the tab_focusable attribute so the BaseWindow class
    # knows to do tab focus changes on it
    tab_focusable = True

# -----------------------------------------------------------------------------

class TextPlus(urwid.Text):
    """Extended version of urwid.Text"""

    @classmethod
    def combine_markup(self, first, second, same_markup=False):
        """Creates a new markup list combining the first and second piece of
        markup. 

        :param first: first markup to combine, may be text, tuple or list
        :param second: second markup to combine, may be text, tuple or list
        :param same_markup: if True, "second" parameter must be text and it is
                            markup attributes are set the same as the last
                            attributed text in "first". If "second" is not
                            text this value is ignored
        """
        markup = []
        if isinstance(first, list):
            markup.extend(first)
        else:
            markup = [first, ]

        if isinstance(second, list):
            markup.extend(second)
        else:
            if isinstance(second, str) and same_markup:
                # combine second with last item in first using the same markup
                # attributes as that item
                if isinstance(markup[-1], str):
                    # last part of first is a string, just combine
                    markup[-1] = markup[-1] + second
                else:
                    # last part of first is a tuple, create a new tuple with
                    # the same attribute and combined text
                    markup[-1] = (markup[-1][0], markup[-1][1] + second)
            else:
                # second is a tuple or same_markup == False, just append it
                markup.append(second)

        return markup

    def get_markup(self):
        """urwid.Text.get_text() returns the text and a run length encoding of
        attributes, this method returns markup instead. The markup returned is
        always in a list, even if the content of the widget is only text, the
        result will be a list with a single text item.
        """
        markup = []
        text, attrs = self.get_text()

        start = 0
        for attr in attrs:
            name = attr[0]
            size = attr[1]
            chunk = text[start:start+size]
            if name:
                markup.append( (name, chunk) )
            else:
                markup.append( chunk )

            start += size

        return markup

    def set_line_number(self, number):
        markup = self.get_markup()
        if not markup[0][0].startswith('line_number'):
            # no line number in our markup, do nothing
            return

        # replace the value of the line number
        markup[0] = (markup[0][0], str(number))
        self.set_text(markup)
