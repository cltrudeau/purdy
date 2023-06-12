# purdy.utils.py

def string_length_split(text, size):
    """Splits a string into one or more pieces each being `size` in length."""
    return [ text[i:i+size] for i in range(0, len(text), size)]
