from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace, Punctuation, Text, Literal

from purdy.parser import FoldedCodeLine, token_ancestor

# =============================================================================
# HTML Colourizer: augments code with colour specified using HTML style tags

import html

_code_palette = {
    Token:              '',
    Whitespace:         '',
    Comment:            'color: #8f5902; font-style: italic;',
    Keyword:            'color: #2048a7; font-weight: bold;',
    Operator:           'color: #ce5c00; font-weight: bold;',
    Name:               'color: #000000;',
    Name.Builtin:       'color: #3465a4;',
    Name.Function:      'color: #000000;',
    Name.Class:         'color: #000000;',
    Name.Exception:     'color: #cc0000; font-weight: bold;',
    Name.Decorator:     'color: #5c35cc; font-weight: bold;',
    Name.Variable:      '',
    Name.Constant:      '',
    Name.Attribute:     '',
    Name.Tag:           '',
    Punctuation:        'color: #000000; font-weight: bold;',
    String:             'color: #4e9a06;',
    String.Doc:         'color: #8f5902; font-style: italic;',
    Number:             'color: #0000cf; font-weight: bold;',
    Generic.Prompt:     'color: #8f5902;',
    Generic.Error:      'color: #ef2929;',
    Generic.Traceback:  'color: #a40000; font-weight: bold;',
    Error:              'color: #ef2929;',
}

_xml_palette = dict(_code_palette)
_xml_palette.update({
    Name.Attribute: 'color: #2048a7; font-weight: bold;',
    Name.Tag:       'color: #3465a4;',
    Keyword:        'color: #3465a4;',
    Punctuation:    'color: #3465a4;',
})

_doc_palette = dict(_xml_palette)
_doc_palette.update({
    Generic.Emph:   'color: #ef2929;',
    Generic.Strong: 'color: #a40000; font-weight: bold;',
    Literal:        'color: #3465a4;',
    Generic.Heading:'color: #3465a4;',
    Generic.Subheading:'color: #3465a4;',
})

class HTMLColourizer:
    palettes = {
        'code':_code_palette,
        'xml':_xml_palette,
        'doc':_doc_palette,
    }

    highlight = 'background-color:#ddd; '

    @classmethod
    def colourize(cls, code_line):
        """Returns a text string with ANSI colour escapes corresponding to the
        tokens sent in

        :param code_line: a :class:`CodeLine` object to colourize
        """
        if isinstance(code_line, FoldedCodeLine):
            return '<span style="color: #000; font-weight: bold;">⋮</span>'

        palette = code_line.lexer.palette
        ancestor_list = cls.palettes[palette].keys()

        output = []

        if code_line.line_number >= 0:
            output.append( HTMLColourizer.line_number(code_line.line_number) )
        
        if code_line.highlight:
            output.append(f'<span style="{cls.highlight}">')

        for part in code_line.parts:
            text = html.escape(part.text)
            key = token_ancestor(part.token,   ancestor_list)
            style = cls.palettes[palette][key]

            if style:
                output.append(f'<span style="{style}">{text}</span>')
            else:
                output.append(text)

        if code_line.highlight:
            output.append('</span>')

        return ''.join(output)

    @classmethod
    def line_number(cls, num):
        """Returns a colourized version of a line number"""
        style = ('color: #333; display: inline-block; min-width: 4ex;'
            'text-align: right; padding-right: 1ex;')
        return f'<span style="{style}">{num}</span>'

