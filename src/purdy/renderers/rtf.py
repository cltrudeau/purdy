# renderers/rtf.py
import struct

from pygments.token import Token, Whitespace

from purdy.content import Code, MultiCode
from purdy.parser import HighlightOn, HighlightOff
from purdy.renderers.formatter import StrFormatter

# ===========================================================================
# RTF Specific Utilities
# ===========================================================================

class RTFFormatter(StrFormatter):
    def __init__(self, rtf_doc):
        super().__init__()
        self.newline = "\\\n"
        self.escape = self.rtf_encode
        self.rtf_doc = rtf_doc

    @classmethod
    def rtf_encode(cls, text):
        """RTF uses a weird UTF-16 decimal escape sequence for encoding unicode.
        This method take a string and returns an RTF encoded version of it."""
        output = []
        data = text.encode('utf-16le')
        length = len(data) // 2

        # use struct.unpack to turn the pairs of bytes into decimal unicode
        # escape numbers
        parts = struct.unpack(f'<{length}H', data)
        index = 0
        size = len(parts)

        while index < size:
            num = parts[index]

            if num <= 127:
                # regular ascii
                letter = chr(num)

                # Escape characters that are used by RTF
                if letter == '\\':
                    output.append('\\\\')
                elif letter in '{}':
                    output.append('\\' + letter)
                else:
                    output.append(letter)
            elif num <= 256:
                # extended ascii, use hex notation
                output.append(f"\\'{num:2x}" )
            elif num < 55296:
                # 0xD800 (55296) is the the boundary for two-word encoding, less
                # than this means it is a single item
                output.append(f"\\uc0\\u{num}")
            else:
                # greater than 0xD800, means two words
                index += 1
                next_num = parts[index]
                output.append(f"\\uc0\\u{num} \\u{next_num}")

            index += 1

        return ''.join(output)

    def tag_open(self, fg, bg, attrs):
        tag = ""
        if fg:
            index, _ = self.rtf_doc.colour_table[fg]
            tag += fr"\cf{index} "
        if bg:
            index, _ = self.rtf_doc.colour_table[bg]
            tag += fr"\cb{index} "

        if "bold" in attrs:
            tag += r"\b "

        if "italic" in attrs:
            tag += r"\i "

        return tag

    def tag_close(self, attrs):
        tag = ""
        if "italic" in attrs:
            tag += r"\i0 "

        if "bold" in attrs:
            tag += r"\b0 "

        # Return colouring fg to auto and bg to background
        tag += r"\cf0 \cb1"
        return tag

    def _map_tag(self, token, fg, bg, attrs, exceptions):
        if token in exceptions:
            self.tag_map[token] = exceptions[token]
            return

        # Default handling
        if not (fg or bg or attrs):
            # No formatting
            self.tag_map[token] = "{text}"
            return

        tag = self.tag_open(fg, bg, attrs)
        tag += "{text}"
        tag += self.tag_close(attrs)
        tag += "\n"

        self.tag_map[token] = tag


class RTFDoc(list):
    PREAMBLE = r"{\rtf1\ansi\ansicpg1252" + "\n"
    FONT_TABLE = r"{\fonttbl\f0\fnil\fcharset0 %s;}" + "\n"
    FONT_SPEC = r'\f0\fs28' + '\n'

    def __init__(self, background, container, fontname="RobotoMono-Regular"):
        """RTF uses a look-up table for colouring. This class builds a table
        for lookups and provides mapping utilities."""
        self.has_background = background is not None
        self.fontname = fontname

        self.colour_table = {}
        if self.has_background:
            # Colour 0 is "auto", start counting at 1
            self.colour_table[background] = (1, self.rgb_to_rtf(background))
        else:
            # Default to white
            self.colour_table[background] = (1, self.rgb_to_rtf("ffffff"))

        for code in container:
            for token, value in code.theme.colour_map.items():
                if not value:
                    continue

                if isinstance(value, tuple):
                    # Add the fg and bg colours
                    self._set_colour(value[0])
                    self._set_colour(value[1])
                else:
                    # Single value, add it
                    self._set_colour(value)

    def _set_colour(self, value):
        if not value or value in self.colour_table:
            return

        # Value not in the colour table, create a new one
        pos = len(self.colour_table) + 1
        self.colour_table[value] = (pos, self.rgb_to_rtf(value))

    @classmethod
    def rgb_to_rtf(cls, colour):
        """Translates a three or six digit RGB hex value into the RTF
        equivalent."""
        double_it = lambda colour, index: f"0x{colour[index]}{colour[index]}"

        if len(colour) == 3:
            red = int(double_it(colour, 0), base=16)
            green = int(double_it(colour, 1), base=16)
            blue = int(double_it(colour, 2), base=16)
        else:
            red = int(f"0x{colour[0:2]}", base=16)
            green = int(f"0x{colour[2:4]}", base=16)
            blue = int(f"0x{colour[4:6]}", base=16)

        return fr'\red{red}\green{green}\blue{blue}'

    @property
    def header_string(self):
        result = self.PREAMBLE
        result += self.FONT_TABLE % self.fontname

        # Colour table
        result += r"{\colortbl;"

        colour_list = list(self.colour_table.values())
        colour_list.sort()

        for _, rtf_colour in colour_list:
            result += f"{rtf_colour};"

        result += "}\n"

        # Font table
        result += self.FONT_SPEC + "\n"

        # Set background colour (\cb0 is the default colour, \cb1 is the first
        # colour in our table which has been set to the background)
        if self.has_background:
            result += r"\chsdng10000\chcbpat0\cb1" + "\n"

        return result

    def render(self):
        output = self.header_string
        output += "\n".join(self)
        output += "}\n"
        return output

# ===========================================================================

def to_rtf(container):
    """Transforms tokenized content in a :class:`Code` object into a string
    representation of RTF.

    :param container: `Code` or :class:`MultiCode` object to render
    """
    result = ""
    if isinstance(container, Code):
        container = MultiCode(container)

    doc = RTFDoc(container.background, container)

    for code_index in range(0, len(container)):
        code = container[code_index]
        formatter = RTFFormatter(doc)

        code_tag_exceptions = {
            Token:      r"\cf0 {text}" + "\n",
            Whitespace: r"\cf0 {text}" + "\n",
        }

        hl_colour = code.theme.colour_map[HighlightOn]
        if isinstance(hl_colour, str):
            index, _ = doc.colour_table[hl_colour]
            code_tag_exceptions.update({
                HighlightOn:  fr"\cf{index} " + "{text}\n",
                HighlightOff: r"\cf0" + "\n",
            })
        else:
            # Close tag using the auto colour (0) for fg & bg, pass thru attrs
            code_tag_exceptions.update({
                HighlightOn:  formatter.tag_open(*hl_colour) + "{text}",
                HighlightOff: formatter.tag_close(hl_colour[2]),
            })

        formatter.create_tag_map(code.theme, code_tag_exceptions)

        ancestor_list = code.theme.colour_map.keys()
        for line in formatter.get_decorated_lines(container, code_index):
            doc.append(formatter.format_line(line, ancestor_list))

        result += doc.render()

    return result
