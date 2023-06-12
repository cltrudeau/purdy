# tui.steps.py
from copy import deepcopy

from pygments.token import Generic

from purdy.content import Code

# ===========================================================================

class _ListingState:
    def __init__(self, listing):
        self.listing = listing
        self.lines = deepcopy(listing.lines)

# ---------------------------------------------------------------------------

class AppendStep:
    def __init__(self, box, *args):
        self.box = box
        self.code_list = []

        for item in args:
            if isinstance(item, str):
                # Passed a bare string, use the 'plain' parser
                self.code_list.append( Code(text=item, parser='plain') )
            elif isinstance(item, Code):
                self.code_list.append(item)
            else:
                raise ValueError("Unrecognized value to append: ", item)

    def forwards(self):
        self.undo = _ListingState(self.box.listing)
        for code in self.code_list:
            self.box.listing.append(code)

    def backwards(self):
        self.box.listing.lines = self.undo.lines
