# =============================================================================
# Actions
# =============================================================================

class AppendAll:
    def __init__(self, code_box, code_blob):
        self.code_box = code_box
        self.code_blob = code_blob

    def setup(self, settings):
        for token in self.code_blob.tokens:
            if token.text == '\n':
                # hit a CR, add a new line to our output
                self.code_box.append_newline()
            else:
                self.code_box.append_token(token.colour, token.text)

    def next(self):
        raise StopIteration
