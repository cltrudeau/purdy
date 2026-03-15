# tokens.py
from pygments.token import Token

# ---------------------------------------------------------------------------

# Create new token types using Pygment's tuple magic
HighlightOn = Token.HighlightOn
HighlightOff = Token.HighlightOff
Fold = Token.Fold
LineNumber = Token.LineNumber
TextualOutput = Token.TextualOutput

# ---------------------------------------------------------------------------

def token_is_a(token1, token2):
    """Returns true if token1 is the same type as or a child type of token2"""
    if token1 == token2:
        return True

    parent = token1.parent
    while(parent != None):
        if parent == token2:
            return True

        parent = parent.parent

    return False


def token_ancestor(token, ancestor_list):
    """Tokens are hierarchical, in some situations you need to translate a
    token into one from a known list, e.g. turning a Pygments
    `Token.Literal.Number.Integer` into a `Number`. This method takes a token
    and a list of approved ancestors and attempts to make the map. If no
    ancestor is found then a generic "Token" object is returned

    :param token: token to translate into an approved ancestor
    :param ancestor_list: list of approved ancestor tokens
    """
    if token in ancestor_list:
        return token

    # token not in the approved list, search its ancestors
    token = token.parent
    while(token != None):
        if token in ancestor_list:
            return token

        token = token.parent

    # something went wrong with our lookup, return the default
    return Token
