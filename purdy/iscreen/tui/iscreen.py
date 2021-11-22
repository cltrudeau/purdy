"""
TUI Screen (purdy.tui.iscreen.py)
=================================

This module is an Urwid code viewer concrete implementation of a Screen. It is
constructed by :class:`purdy.ui.Screen` depending on its factory.
"""
import urwid

from purdy.colour import COLOURIZERS
from purdy.iscreen.tui.widgets import (CodeWidget, DividingLine,
    TwinContainer, ScrollingListBox, ScrollingIndicator)


UrwidColourizer = COLOURIZERS['urwid']

#import logging
#logging.basicConfig(filename='debug.log', level=logging.DEBUG)
#logger = logging.getLogger()

# =============================================================================
# Window Management
# =============================================================================

class FocusWalker:
    ### Urwid has no call for focusing on a widget, you have to use an index
    # into its parent's container. The FocusWalker finds all of the CodeWidget
    # objects, figures out which one is currently focused and allows for the
    # previous and next item to be focused
    class Node:
        def __init__(self, position, parent=None, parent_position=0):
            self.position = position
            self.parent = parent
            self.parent_position = parent_position

    def __init__(self, root):
        ### Figures out the order things should be focused in. 
        #
        # :param root: root container to look for CodeWidgets within
        #
        self.root = root
        self.focused_index = 0
        self.nodes = []

        current_focus, _ = root.contents[root.focus_position]

        # root is a Pile with either CodeWidgets or Columns in it, where
        # the columns contain CodeWidgets
        for position, content in enumerate(root.contents):
            widget = content[0]
            if isinstance(widget, CodeWidget):
                if widget == current_focus:
                    self.focused_index = len(self.nodes)

                self.nodes.append( self.Node(position) )
            elif isinstance(widget, urwid.Columns):
                index = len(self.nodes)

                self.nodes.append( self.Node(position, widget, 0) )
                self.nodes.append( self.Node(position, widget, 1) )

                if widget == current_focus:
                    if widget.focus_position == 0:
                        self.focused_index = index
                    elif widget.focus_position == 1:
                        self.focused_index = index + 1
                    # else: shouldn't happen

            # else: shouldn't happen

    def focus_next(self):
        # if we're the last item, loop to the next
        position = self.focused_index + 1
        if position >= len(self.nodes):
            position = 0

        self.set_focus(position)

    def focus_prev(self):
        # if we're the first item, loop to the next
        position = self.focused_index - 1
        if position < 0:
            position = len(self.nodes) - 1

        self.set_focus(position)

    def set_focus(self, position):
        # set the focus
        node = self.nodes[position]
        self.root.focus_position = node.position

        if node.parent:
            node.parent.focus_position = node.parent_position


class BaseWindow(urwid.Pile):
    def __init__(self, iscreen, *args, **kwargs):
        self.iscreen = iscreen
        self.parent_screen = iscreen.parent_screen
        self.animation_manager = iscreen.parent_screen.animation_manager
        super(BaseWindow, self).__init__(*args, **kwargs)

    def _next_focus(self):
        walker = FocusWalker(self)
        walker.focus_next()

    def _prev_focus(self):
        walker = FocusWalker(self)
        walker.focus_prev()

    def _close_help(self):
        self.iscreen.loop.widget = self

    def _show_help(self):
        help_box = HelpDialog(self)
        self.iscreen.loop.widget = urwid.Overlay(help_box, self, 
            align='center', valign='middle', width=55, height=20)

    def keypress(self, size, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        if key == '?':
            self._show_help()
            return

        if key in ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10'):
            # let parent handle function keys
            return super(BaseWindow, self).keypress(size, key)

        if key not in self.animation_manager.handled_keys: 
            # handle keys not handled by the animation manager 
            result = super(BaseWindow, self).keypress(size, key)
            if result is None:
                # keypress was handled by child, we're done
                return None
            # else: fall through if super().keypress() didn't deal with it

        if self.parent_screen.movie_mode > -1:
            # Ignore other keypresses in movie mode
            return None

        # --- at this point the keypress was not handled by the children, see
        # if we want to do anything with it
        if key == 'tab':
            self._next_focus()
            return None

        if key == 'shift tab':
            self._prev_focus()

        return self.animation_manager.perform(key)

    def animation_alarm(self, loop, data):
        self.animation_manager.animation_alarm()

    def movie_alarm(self, loop, data):
        self.animation_manager.movie_alarm()

    def auto_forward_alarm(self, loop, data):
        self.animation_manager.auto_forward_alarm()

# =============================================================================
# Screen
# =============================================================================

class ConcreteCodeBox:
    """:class:`purdy.ui.CodeBox` represents a box of code in the 
    :class:`purdy.ui.Screen`. This is an Urwid implementation of it. 

    :param proxy_code_box: the :class:`purdy.ui.CodeBox` representing what is 
                           to be built.
    """
    def __init__(self, proxy_code_box):
        self.proxy_code_box = proxy_code_box
        self.widget = CodeWidget(self, self.proxy_code_box.auto_scroll)

    def build(self, container):
        self.proxy_code_box.listing.set_display('urwid', self.widget)

        if self.proxy_code_box.height == 0:
            container.append(self.widget)
        else:
            # height was specified, return a tuple instead
            container.append( (self.proxy_code_box.height, self.widget) )


class ConcreteTwinCodeBox:
    """:class:`purdy.ui.TwinCodeBox` represents two boxes of code in the 
    :class:`purdy.ui.Screen`, this is an Urwid implementation of it.

    :param proxy: the :class:`purdy.ui.TwinCodeBox` representing what is to be 
                  built.

    """
    def __init__(self, proxy):
        class Side:
            pass

        self.proxy = proxy
        self.left = Side()
        self.left.weight = proxy.left_weight
        self.left.box = ConcreteCodeBox(proxy.left.code_box)

        self.right = Side()
        self.right.weight = proxy.right_weight
        self.right.box = ConcreteCodeBox(proxy.right.code_box)

    def build(self, container):
        # cant' use CodeBox's build() method because we need to pack them into 
        # Urwid # differently
        self.proxy.left.code_box.listing.set_display('urwid', 
            self.left.box.widget)
        self.proxy.right.code_box.listing.set_display('urwid', 
            self.right.box.widget)

        # Combine the widgets from the CodeBoxes into a display container
        render_left = ('weight', self.left.weight, self.left.box.widget)
        render_right = ('weight', self.right.weight, self.right.box.widget)

        twin = TwinContainer([render_left, render_right], dividechars=1)

        if self.proxy.height != 0:
            twin = (self.proxy.height, twin)

        container.append(twin)


class TUIScreen:
    """Concrete, Urwid based implementation of a screen.

    :param parent_screen: :class:`purdy.ui.Screen` object that is creating
                          this concrete implementation

    """
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        self.widgets = []

    def _add_concrete_code_box(self, code_box, constructor):
        size = len(self.widgets)
        if size > 0:
            # not the first box, add a dividing line
            compact = self.parent_screen.code_boxes[size - 1].compact
            div_height = 3
            if compact:
                div_height = 1

            divider = (div_height, DividingLine())
            self.widgets.append(divider)

        box = constructor(code_box)
        box.build(self.widgets)

    def add_code_box(self, code_box):
        self._add_concrete_code_box(code_box, ConcreteCodeBox)

    def add_twin_code_box(self, code_box):
        self._add_concrete_code_box(code_box, ConcreteTwinCodeBox)

    def set_alarm(self, handler, when):
        fn = getattr(self.base_window, handler)
        alarm_handle = self.loop.set_alarm_in(when, fn)
        return alarm_handle

    def remove_alarm(self, alarm_handle):
        self.loop.remove_alarm(alarm_handle)

    def run(self):
        """Calls the main display event loop. Does not return until the UI
        exits."""
        self.base_window = BaseWindow(self, self.widgets)
        window = self.base_window
        if self.parent_screen.max_height:
            # Force a maximum height on the window, put the BaseWindow in a
            # container and fill anything that is bigger than max
            window = urwid.Pile([
                (int(self.parent_screen.max_height), self.base_window),
                urwid.SolidFill(' '),
            ])

        palette = UrwidColourizer.create_urwid_palette()
        self.loop = urwid.MainLoop(window, palette)

        if self.parent_screen.settings['colour'] == 256:
            # don't confuse urwid's screen with ours
            self.loop.screen.set_terminal_properties(colors=256)
            self.loop.screen.reset_default_terminal_palette()

        # as soon as the loop is going invoke the first animation
        self.loop.set_alarm_in(0, self.base_window.auto_forward_alarm)

        # call urwid's main loop, this code doesn't return until the loop
        # exits!!!
        self.loop.run()

# =============================================================================
# Help Dialog
# =============================================================================

class HelpDialog(urwid.Pile):
    def __init__(self, parent):
        self.parent = parent

        ### Define dialog
        header = urwid.Text(('reverse', 'Help'), align = 'center')

        # Body
        index = parent.animation_manager.index + 1
        steps = len(parent.animation_manager.cells)

        walker = urwid.SimpleListWalker([
            urwid.Text(''),
            urwid.Text(('title', 'Keys')),
            urwid.Text(''),
            urwid.Text([('bold', 'q, Q   '), ': Quit']),
            urwid.Text([('bold', '<TAB>  '), ': Switch focused window']),
            urwid.Text([('bold', '⬆ <TAB>'), ': Previous focused window']),
            urwid.Text([('bold', '<LEFT> '), ': Previous step']),
            urwid.Text([('bold', '<RIGHT>'), ': Next step']),
            urwid.Text([('bold', 's      '), ': Next step, skip animation']),
            urwid.Text([('bold', 'S      '), ': Skip to next section marker']),
            urwid.Text(               '         or to the end'),
            urwid.Text(''),
            urwid.Text(('title', 'Multiples')),
            urwid.Text('You can perform multiple s, S, and <LEFT> commands'),
            urwid.Text('by typing a number before the command'),
            urwid.Text(''),
            urwid.Text(('title', 'State')),
            urwid.Text(f'Step {index} of {steps}'),
        ])

        scroller = ScrollingIndicator()
        listbox = ScrollingListBox(scroller, walker)
        layout = [listbox, (1, scroller)]
        body = urwid.Columns(layout)

        # Footer
        footer = urwid.Text(('bold', "<ENTER> to close"), align="center")

        # Layout
        layout = urwid.Frame(body, header, footer, 'body')
        line_box = urwid.LineBox(layout)
        
        super().__init__([line_box])

    def keypress(self, size, key):
        if key == 'enter':
            self.parent._close_help()

        super().keypress(size, key)
