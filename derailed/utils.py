"""
MIT License

Copyright (c) 2022 VincentRPS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from typing import Any, Literal, TypeVar

V = TypeVar('V')


class UndefinedType:
    __slots__ = ()

    def __bool__(self) -> Literal[False]:
        return False

    def __getstate__(self) -> Any:
        return False

    def __repr__(self) -> str:
        return 'UNDEFINED'

    def __reduce__(self) -> str:
        return 'UNDEFINED'

    def __str__(self) -> str:
        return 'UNDEFINED'


UNDEFINED = UndefinedType()


def replace_undefined(**kwargs: V) -> dict[str, V]:
    return {k: v for k, v in kwargs.items() if v != UNDEFINED}
