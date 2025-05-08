import ipynbname

from .base import ACodeInjector
from .jupyter_inject import JupyterCodeInjector
from .python_inject import PythonCodeInjector


def code_inject_factory() -> ACodeInjector:
    try:
        ipynbname.path()
        return JupyterCodeInjector()
    except FileNotFoundError:
        return PythonCodeInjector()
