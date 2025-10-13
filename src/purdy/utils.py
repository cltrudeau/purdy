# utils.py
from pathlib import Path

# ===========================================================================
# Cosmetic Code Utils
# ===========================================================================

class TextCodeCleaner:
    @classmethod
    def remove_double_blanks(cls, text, trim_whitespace=True):
        """Removes any lines where two or more are blank in a row.

        :param text: Text to process
        :param trim_whitespace: When True (default) a line with only
            whitespace is considered blank, otherwise it only looks for \\n
        """
        lines = text.split('\n')
        output = []

        previous = 'asdf'
        for line in lines:
            if trim_whitespace \
                    and previous.strip() == '' and line.strip() == '':
                continue
            elif previous == '' and line == '':
                    continue

            output.append(line)
            previous = line

        return '\n'.join(output)

    @classmethod
    def flush_left(cls, text):
        """Removes a consistent amount of leading whitespace from the front of
        each line so that at least one line is flushed left.

        .. warning:: will not work with mixed tabs and spaces
        """
        lines = text.split('\n')
        leads = [len(line) - len(line.lstrip()) for line in lines if \
            len(line.strip())]
        if not leads:
            # only blank lines, do nothing
            return text

        min_lead = min(leads)
        output = []
        for line in lines:
            if len(line.lstrip()):
                output.append(line[min_lead:])
            else:
                output.append(line)

        return '\n'.join(output)


class CodeCleaner:
    @classmethod
    def _get_text(cls, filename):
        if isinstance(filename, Path):
            path = filename
        else:
            path = Path(filename).resolve()

        return path.read_text()

    @classmethod
    def remove_double_blanks(cls, filename, trim_whitespace=True):
        """Opens the given file and removes any lines where two or more are
        blank in a row.

        :param filename: Name of file to process or a :class:`pathlib.Path`
            object. File is read as text.
        :param trim_whitespace: When True (default) a line with only
            whitespace is considered blank, otherwise it only looks for \\n
        """
        text = cls._get_text(filename)
        return TextCodeCleaner.remove_double_blanks(text, trim_whitespace)

    @classmethod
    def flush_left(cls, filename):
        """Open the given file and removes a consistent amount of leading
        whitespace from the front of each line so that at least one line is
        flushed left.

        .. warning:: will not work with mixed tabs and spaces

        :param filename: Name of file to process or a :class:`pathlib.Path`
            object. File is read as text.
        """
        text = cls._get_text(filename)
        return TextCodeCleaner.flush_left(text)
