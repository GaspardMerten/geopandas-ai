import json
import re
from typing import Callable, Optional

import ipynbname

from .base import ACodeInjector


class JupyterCodeInjector(ACodeInjector):
    def inject(
        self,
        pattern: re.Pattern,
        function_call: Callable[[Optional[re.Match]], str],
        import_statement: str,
    ):
        from IPython import get_ipython

        filename = ipynbname.path()

        with open(filename, "r") as f:
            jupyter_source = json.load(f)

        match = None
        match_index = None
        for index, cell in enumerate(jupyter_source["cells"]):
            if cell["cell_type"] == "code":
                cell_code = "".join(cell["source"])
                match = pattern.search(cell_code)
                if match:
                    match_index = index
                    match = match
                    break

        if match_index is None:
            raise ValueError("No match found for the pattern in the code.")

        # Modify the code cell
        code_cell = "".join(jupyter_source["cells"][match_index]["source"])

        if import_statement not in code_cell:
            code_cell = f"{import_statement}\n{code_cell}"

        if "JupyterLab" in str(get_ipython()):
            print(
                "JupyterLab detected, code will not be updated directly in the notebook. Please click on 'File -> Reload notebook from disk' to see updated code."
            )

        code_cell = code_cell.replace(match.group(0), function_call(match))

        ipython = get_ipython()
        ipython.run_line_magic("reload_ext", "autoreload")
        ipython.run_line_magic("autoreload", "2")

        # Optional: also update file on disk
        jupyter_source["cells"][match_index]["source"] = code_cell.splitlines(True)
        with open(filename, "w") as f:
            f.write(json.dumps(jupyter_source, indent=4))
