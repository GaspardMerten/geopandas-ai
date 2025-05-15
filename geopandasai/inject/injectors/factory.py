from typing import Type

from .base import ACodeInjector
from .print_inject import PrintCodeInjector


def code_inject_factory(
    injector: Type[ACodeInjector] = PrintCodeInjector,
) -> ACodeInjector:
    return injector()
