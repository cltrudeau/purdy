from enum import Enum

# =============================================================================

class TypingMode(Enum):
    ALL_AT_ONCE = 0
    PROMPTED = 1


class Lexer(Enum):
    CONSOLE = 'con'
    PYTHON = 'py3'

# =============================================================================

settings = {
    # whether to wait for keyboard input to start typing or all at once
    'typing_mode':TypingMode.PROMPTED,

    # which Pygments lexer to use for highlightling content
    'lexer':Lexer.CONSOLE,

    # delay between characters appearing on screen, specified in milliseconds
    'delay':130,

    # range of random time in milliseconds to change the delay; makes typing
    # look more natural
    'delay_variance':30,
}
