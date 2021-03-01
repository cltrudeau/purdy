from typing import Iterable, Iterator, Union, List, Callable, Optional

from purdy.actions import (
    AppendTypewriter,
    Append,
    Suffix,
    Wait,
    Clear,
    Action,
    Insert,
    Replace,
    Remove,
    Shell,
    InsertTypewriter,
    SuffixTypewriter,
    Highlight,
    HighlightChain,
    Fold,
    StopMovie,
    Transition,
    Sleep,
    RunFunction,
)
from purdy.content import Code
from purdy.ui import VirtualCodeBox


class ActionsBuilder(Iterable):
    def __init__(self, screen, lexer_name: str) -> None:
        self.__screen = screen
        self.__code_box = self.__screen.code_boxes[0]
        self.__lexer_name = lexer_name
        self.__actions = []

    def __iter__(self) -> Iterator[Action]:
        return iter(self.__actions)

    def switch_to_code_box(self, index: int) -> "ActionsBuilder":
        self.__code_box = self.__screen.code_boxes[index]
        return self

    def _add_action(self, action: Action) -> "ActionsBuilder":
        self.__actions.append(action)
        return self

    def insert(self, position: int, code: str) -> "ActionsBuilder":
        return self._add_action(Insert(self.__code_box, position, code))

    def append(self, text: str = "", filename: str = "") -> "ActionsBuilder":
        return self._add_action(
            Append(
                self.__code_box,
                Code(filename, text, self.__lexer_name),
            )
        )

    def replace(self, position: int, code: str) -> "ActionsBuilder":
        return self._add_action(Replace(self.__code_box, position, code))

    def remove(self, position: int, size: int) -> "ActionsBuilder":
        return self._add_action(Remove(self.__code_box, position, size))

    def clear(self) -> "ActionsBuilder":
        return self._add_action(Clear(self.__code_box))

    def suffix(self, position: int, source: str) -> "ActionsBuilder":
        return self._add_action(Suffix(self.__code_box, position, source))

    def shell(self, cmd: str) -> "ActionsBuilder":
        return self._add_action(Shell(self.__code_box, cmd))

    def append_typewriter(self, text: str = "", filename: str = "") -> "ActionsBuilder":
        return self._add_action(
            AppendTypewriter(
                self.__code_box,
                Code(filename, text, self.__lexer_name),
            )
        )

    def insert_typewriter(self, position: int, code: str) -> "ActionsBuilder":
        return self._add_action(InsertTypewriter(self.__code_box, position, code))

    def suffix_typewriter(self, position: int, source: str) -> "ActionsBuilder":
        return self._add_action(SuffixTypewriter(self.__code_box, position, source))

    def highlight(
        self, spec: Union[str, List[int]], highlight_on: bool
    ) -> "ActionsBuilder":
        return self._add_action(Highlight(self.__code_box, spec, highlight_on))

    def highlight_chain(
        self, spec_list: List[Union[str, List[int]]]
    ) -> "ActionsBuilder":
        return self._add_action(HighlightChain(self.__code_box, spec_list))

    def fold(self, position: int, end=-1) -> "ActionsBuilder":
        return self._add_action(Fold(self.__code_box, position, end))

    def wait(self) -> "ActionsBuilder":
        return self._add_action(Wait())

    def stop_movie(self) -> "ActionsBuilder":
        return self._add_action(StopMovie())

    def transition(
        self, text: str, filename: str, code_box_to_copy: VirtualCodeBox
    ) -> "ActionsBuilder":
        return self._add_action(
            Transition(
                self.__code_box,
                Code(filename, text, self.__lexer_name),
                code_box_to_copy,
            )
        )

    def sleep(self, time: Union[float, int]) -> "ActionsBuilder":
        return self._add_action(Sleep(time))

    def run_function(
        self, fn: Callable, undo: Optional[Callable], *args, **kwargs
    ) -> "ActionsBuilder":
        return self._add_action(RunFunction(fn, undo, *args, **kwargs))
