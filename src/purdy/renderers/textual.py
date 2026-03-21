# renderers/textual.py
from pygments.token import Token, Whitespace
from textual.content import Content

from purdy.parser import CodeLine, CodePart
from purdy.renderers.formatter import conversion_handler, Formatter
from purdy.tokens import (HighlightOn, HighlightOff, TextualOutput, token_is_a,
    token_ancestor)

# ===========================================================================

def textual_highlighter(line, cutpoints):
    # Parse the Textual markup, split it at the cutpoints, then insert
    # highlight tokens
    content = Content.from_markup(line.parts[0].text)

    output = CodeLine(line.lexer_spec, has_newline=line.has_newline)

    # Handle anything before the first cutpoint
    first_cutpoint_start = cutpoints[0][0]
    if first_cutpoint_start != 0:
        # First cutpoint isn't at the beginning, insert what we have
        output.parts.append(
            CodePart(TextualOutput, content[0:first_cutpoint_start].markup))

    # Highlight each cutpoint section
    for cutpoint in cutpoints:
        end = cutpoint[0] + cutpoint[1]
        output.parts.append(CodePart(HighlightOn, ""))
        output.parts.append(
            CodePart(TextualOutput, content[cutpoint[0]:end].markup))
        output.parts.append(CodePart(HighlightOff, ""))

    # Handle anything after the last cutpoint
    last_cutpoint_end = cutpoints[-1][0] + cutpoints[-1][1]
    if last_cutpoint_end < len(content.plain):
        output.parts.append(
            CodePart(TextualOutput, content[last_cutpoint_end:].markup))

    return output

# ===========================================================================

class TextualFormatter(Formatter):
    def _map_tag(self, token, fg, bg, attrs, exceptions):
        if token in exceptions:
            self.tag_map[token] = exceptions[token]
            return

        # Default handling
        if not (fg or bg or attrs):
            # No formatting
            self.tag_map[token] = "$text"
            return

        # Use f-string to inject rich markup, but raw string to insert the
        # brace brackets expected by .format_doc()
        self.tag_map[token] = f"[#{fg} {attrs}]$text[/]"

    def render_code_line(self, render_state, line):
        # Textual really doesn't like piecemeal creation of content or
        # strings, and they way the code works elsewhere you can just append a
        # close attr, but here you can't
        #
        # You need to construct a single string for the Content.from_markup
        # method, which means having to be a bit hacky, creating then
        # re-parsing the individual pieces

        part_map = {}
        counter = 0
        markup = ""

        for part in line.parts:
            if token_is_a(part.token, TextualOutput):
                # Embed TextualOutput directly so that the content doesn't get
                # escaped
                markup += part.text
                continue

            token = token_ancestor(part.token, self.ancestor_list)

            name = f"text_{counter}"
            dname = "$" + name

            try:
                # Get the tag from the general map and replace $text with
                # the counted version
                marker = self.tag_map[token]
                marker = marker.replace("$text", dname)
            except KeyError:
                # No map tags, use just the placeholder for the content
                marker = dname

            # Store the text for Content's kwargs and update our markup
            # string
            part_map[name] = part.text
            markup += marker

            counter += 1

        if line.has_newline:
            markup += self.newline

        # Now get Textual to render that mess
        render_state.content += Content.from_markup(markup, **part_map)

    def part_to_content(self, token, value):
        token = token_ancestor(token, self.ancestor_list)
        part_map = {
            "text": value,
        }

        try:
            # Use the tag from the general map
            markup = self.tag_map[token]
        except KeyError:
            # No map tags, use just the placeholder for the content
            markup = "$text"

        # Get Textual to render that mess
        return Content.from_markup(markup, **part_map)


_CODE_TAG_EXCEPTIONS = {
    Token:              "$text",
    Whitespace:         "$text",

    # Purdy tokens
    HighlightOn:        "[on #444444]$text",
    HighlightOff:       "[/on #444444]",
}

# ===========================================================================

def to_textual(container):
    """Transforms tokenized content in a :class:`Code` or :class:`Document`
    object into a string with Textual library formatting.

    :param container: :class:`Code` or :class:`Document` object to translate
    """
    return conversion_handler(TextualFormatter, container, _CODE_TAG_EXCEPTIONS)
