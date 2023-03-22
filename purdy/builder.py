from typing import (Iterable, Iterator, Union, List, Callable, Optional, Any,
    Tuple)
from purdy.actions import (AppendTypewriter, Append, Suffix, Wait, Clear,
    Insert, Replace, Remove, Shell, InsertTypewriter, SuffixTypewriter,
    AppendPrompt, Highlight, HighlightChain, Fold, StopMovie, Transition,
    Sleep, RunFunction, Section)
from purdy.content import Code
from purdy.ui import VirtualCodeBox, Screen


class ActionsBuilder(Iterable):
    """Collects all actions to be called on a :class:`purdy.ui.Screen`.
    Once all actions are created the instance of this class can be passed
    to the :class:`purdy.ui.Screen.run()` method.

    :param screen: screen containing the code boxes the actions should be
                   added to

    :param lexer_name: name of the lexer to be used, which must be one of the
                       following:

                        - con: Python 3 Console
                        - py3: Python 3 Source
                        - bash, Bash Console

    Example
    =======

    >>> from purdy.ui import SimpleScreen
    >>> screen = SimpleScreen(starting_line_number=-1)
    >>> actions = (
    ...     ActionsBuilder(code_box, "bash")
    ...     .append_typewriter(text="$ ls ~/.pyenv/versions/")
    ...     .append(text="2.7.15 3.9.0 3.9.1")
    ... )
    >>> screen.run(actions)
    """

    def __init__(self, screen: Screen, lexer_name: str) -> None:
        self.__screen = screen
        self.__code_box = self.__screen.code_boxes[0]
        self.__lexer_name = lexer_name
        self.__actions = []

    def __iter__(self) -> Iterator[Any]:
        return iter(self.__actions)

    def switch_to_code_box(self, index: int) -> "ActionsBuilder":
        """Switches to another code box on screen so the following actions
        will be executed there

        :param index: index of the code box where the following actions
        should be executed
        :return: self
        """
        self.__code_box = self.__screen.code_boxes[index]
        return self

    def _add_action(self, action: Any) -> "ActionsBuilder":
        self.__actions.append(action)
        return self

    def _create_code(self, filename: str = "", text: str = "", 
            code: Code = None) -> Optional[Code]:

        if filename or text or code:
            return code or Code(filename=filename, text=text, 
                lexer_name=self.__lexer_name)

    def insert(self, position: int, filename: str = "", text: str = "", 
            code: Code = None) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Insert` action

        :param position: line number to insert code at. Position is 1-indexed.
                         Content is pushed down, so a value of "1" inserts at 
                         the beginning. Negative indices are supported. A
                         value of "0" will append the code to the bottom.

        :param filename: name of a file to read for :class:`purdy.content.Code` 
                         content.  If both this and `text` is given,
                         `filename` is used first

        :param text: text to read for :class:`purdy.content.Code` content.

        :param code: a :class:`purdy.content.Code` object containing the source
                     code to insert. If all `code`, `filename` and `text` are 
                     given, `code` will be used first.

        :return: self
        """
        return self._add_action(Insert(self.__code_box, position, 
            self._create_code(filename, text, code)))

    def append(self, filename: str = "", text: str = "", 
            code: Code = None) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Append` action

        :param filename: name of a file to read for :class:`purdy.content.Code` 
                         content.  If both this and `text` is given,
                         `filename` is used first

        :param text: text to read for :class:`purdy.content.Code` content.

        :param code: a :class:`purdy.content.Code` object containing the source
                     code to insert. If all `code`, `filename` and `text` are 
                     given, `code` will be used first.

        :return: self
        """
        return self._add_action(Append(self.__code_box,
                self._create_code(filename, text, code)))

    def replace(self, position: int, filename: str = "", text: str = "", 
            code: Code = None) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Replace` action

        :param position: line number to replace the code at. Position is 
                         1-indexed.  Negative indices are supported.

        :param filename: name of a file to read for :class:`purdy.content.Code` 
                         content. If both this and `text` is given, `filename`
                         is used first

        :param text: text to read for :class:`purdy.content.Code` content.

        :param code: a :class:`purdy.content.Code` object containing the source
                     code to insert. If all `code`, `filename` and `text` are 
                     given, `code` will be used first.

        :return: self
        """
        return self._add_action(Replace(self.__code_box, position, 
            self._create_code(filename, text, code)))

    def remove(self, position: int, size: int) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Remove` action

        :param position: line number to replace the code at. Position is 
                         1-indexed.  Negative indices are supported.

        :param size: number of lines to remove.

        :return: self
        """
        return self._add_action(Remove(self.__code_box, position, size))

    def clear(self) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Clear` action

        :return: self
        """
        return self._add_action(Clear(self.__code_box))

    def suffix(self, position: int, source: str) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Suffix` action

        :param position: line number to replace the code at. Position is 
                         1-indexed.  Negative indices are supported.

        :param source: string containing content to append to the line

        :return: self
        """
        return self._add_action(Suffix(self.__code_box, position, source))

    def shell(self, cmd: str) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Shell` action

        :param cmd: string containing the shell command and its parameters.
                    Example: ``ls -la``.

        :return: self
        """
        return self._add_action(Shell(self.__code_box, cmd))

    def append_typewriter(self, filename: str = "", text: str = "", 
            code: Code = None) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.AppendTypewriter` action

        :param filename: name of a file to read for :class:`purdy.content.Code` 
                         content.  If both this and `text` is given,
                         `filename` is used first

        :param text: text to read for :class:`purdy.content.Code` content.

        :param code: a :class:`purdy.content.Code` object containing the source
                     code to insert. If all `code`, `filename` and `text` are
                     given, `code` will be used first.

        :return: self
        """
        return self._add_action(AppendTypewriter(self.__code_box, 
            self._create_code(filename, text, code)))

    def insert_typewriter(self, position: int, filename: str = "", 
            text: str = "", code: Code = None) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.InsertTypewriter` action

        :param position: line number to insert the code at. Position is 
                         1-indexed.

        :param filename: name of a file to read for :class:`purdy.content.Code` 
                         content. If both this and `text` is given, `filename`
                         is used first

        :param text: text to read for :class:`purdy.content.Code` content.

        :param code: a :class:`purdy.content.Code` object containing the source
                     code to insert. If all `code`, `filename` and `text` are 
                     given, `code` will be used first.

        :return: self
        """
        return self._add_action(InsertTypewriter(self.__code_box, position, 
            self._create_code(filename, text, code)))

    def suffix_typewriter(self, position: int, source: str) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.SuffixTypewriter` action

        :param position: line number to insert the code at. Position is 
                         1-indexed.  Negative indices are supported.

        :param source: a string to be appended to the given line

        :return: self
        """
        return self._add_action(SuffixTypewriter(self.__code_box, position, 
            source))

    def append_prompt(self, code: Code, response: str ) -> "ActionsBuilder":
        """This action is used to show a prompt and its response. It appends the
        content of a :class:`purdy.content.Code` object to a
        :class:`purdy.ui.CodeBox` as a prompt, waits for the 'right arrow' key,
        then uses the typewriter animation to add the response to the same line.

        :param code: a :class:`purdy.content.Code` object containing the prompt
                     code to insert.

        :param response: text to place after the prompt
        """
        return self._add_action(AppendPrompt(self.__code_box, code, response))

    def highlight(self, spec: Union[int, str, Iterable[int]], 
            highlight_on: bool) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Highlight` action

        :param spec: either a string containing comma separated and/or hyphen
                     separated integers (e.g. "1,3,7-9") or a list of integers
                     specifying the lines in the code box to highlight. Line
                     numbers are 1-indexed

        :param highlight_on: True to turn highlighting on, False to turn it off

        :return: self
        """
        return self._add_action(Highlight(self.__code_box, spec, highlight_on))

    def highlight_chain(self, 
            spec_list: List[Union[str, List[int]]]) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.HighlightChain` action

        :param spec_list: a list of highlight specs (see :class:`Highlight` for
                          details on a spec)

        :return: self
        """
        return self._add_action(HighlightChain(self.__code_box, spec_list))

    def fold(self, position: int, end=-1) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Fold` action

        :param position: line number to begin the fold at. Position is 
                         1-indexed.

        :param end: line number to finish the folding at, inclusive. A value of
                    -1 can be used to fold to the end of the box. Defaults to
                    -1.

        :return: self
        """
        return self._add_action(Fold(self.__code_box, position, end))

    def wait(self) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Wait` action

        :return: self
        """
        return self._add_action(Wait())

    def stop_movie(self) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.StopMovie` action

        :return: self
        """
        return self._add_action(StopMovie())

    def transition(self, filename: str = "", text: str = "", code: Code = None,
        code_box_to_copy: VirtualCodeBox = None) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Transition` action

        :param filename: name of a file to read for :class:`purdy.content.Code` 
                         content. If both this and `text` is given, `filename`
                         is used first

        :param text: text to read for :class:`purdy.content.Code` content.

        :param code: a :class:`purdy.content.Code` object containing the source
                     code to insert. If all `code`, `filename` and `text` are 
                     given, `code` will be used first.

        :param code_box_to_copy: a code box containing rendered code to copy 
                                 into this one to display. This is typically a
                                 :class:`VirtualCodeBox`. Should not be used
                                 at the same time as code parameter.

        :return: self
        """
        return self._add_action(Transition(self.__code_box,
                self._create_code(filename, text, code), code_box_to_copy))

    def sleep(self, 
            time: Union[float, Tuple[float, float]]) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.Sleep` action

        :param time: amount of time to sleep given in seconds, or a tuple
                     specifying lower and upper bound of random time in seconds 

        :return: self
        """
        return self._add_action(Sleep(time))

    def run_function(self, fn: Callable, 
            undo: Optional[Callable], *args, **kwargs) -> "ActionsBuilder":
        """Adds an :class:`purdy.actions.RunFunction` action

        :param fn: function to be called
        :param undo: function to be called when this Action is undone
        :param *args, **kwargs: any remaining arguments are passed to the
                                functions when they are called

        :return: self
        """
        return self._add_action(RunFunction(fn, undo, *args, **kwargs))

    def section(self) -> 'ActionsBuilder':
        """Adds a :class:`purdy.actions.Section` action

        :return: self
        """
        return self._add_action(Section())
