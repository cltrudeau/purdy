# tui.steps.py
from copy import deepcopy
from logging import getLogger

from pygments.token import Generic

from purdy.content import Code

logger = getLogger(__name__)

# ===========================================================================

class _ListingState:
    def __init__(self, listing):
        self.listing = listing
        self.lines = deepcopy(listing.lines)

# ---------------------------------------------------------------------------

class _Undoable:
    def __init__(self, box):
        self.box = box
        self.undo = None

    def backward(self):
        self.box.listing.replace_lines(self.undo.lines)


class AppendStep(_Undoable):
    def __init__(self, box, *args):
        super().__init__(box)
        self.code_list = []

        for item in args:
            if isinstance(item, str):
                # Passed a bare string, use the 'plain' parser
                self.code_list.append( Code(text=item, parser='plain') )
            elif isinstance(item, Code):
                self.code_list.append(item)
            else:
                raise ValueError("Unrecognized value to append: ", item)

    def __str__(self):
        output = [f"   AppendStep: {self.box.name}"]
        for code in self.code_list:
            output.append(f"      Code: {code.parser.spec.name}")
            for line in code.source.split("\n"):
                output.append(f"         {line}")

        return "\n".join(output)

    def forward(self):
        self.undo = _ListingState(self.box.listing)

        for code in self.code_list:
            self.box.listing.append_code(code)


class HighlightStep(_Undoable):
    def __init__(self, box, *args):
        super().__init__(box)
        self.highlights = args

    def __str__(self):
        return f"   HighlightStep: {self.box.name} {self.highlights}"

    def forward(self):
        self.undo = _ListingState(self.box.listing)
        self.box.listing.highlight(*self.highlights)


class HighlightOffStep(_Undoable):
    def __init__(self, box, *args):
        super().__init__(box)
        self.highlights = args

    def __str__(self):
        return f"   HighlightOffStep: {self.box.name} {self.highlights}"

    def forward(self):
        self.undo = _ListingState(self.box.listing)
        self.box.listing.highlight_off(*self.highlights)
