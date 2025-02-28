import pathlib
from pydantic import BaseModel
from anywidget.experimental import widget
from typing import Literal
from psygnal import evented
import dataclasses

"""
class Matrix(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "matrix.js"
    _css = pathlib.Path(__file__).parent / "matrix.css"
    matrix = traitlets.List().tag(sync=True)
    colors = traitlets.List(default_value=["white"], allow_none=True).tag(sync=True)
    origin = traitlets.List(default_value=None, allow_none=True).tag(sync=True)
    coordinate_system = traitlets.Unicode(default_value="x,y").tag(
        sync=True
    )  # "x,y" or "row,column"
"""


@widget(
    esm=(pathlib.Path(__file__).parent / "matrix.js").read_text(),
    css=(pathlib.Path(__file__).parent / "matrix.css").read_text(),
)
@evented
@dataclasses.dataclass
class Matrix:
    matrix: list[list[int]]
    # colors: list[str | tuple[int, int, int] | tuple[int, int, int, int]] | None = [
    #    "white"
    # ]
    # origin: tuple[int, int] | None = None
    # coordinate_system: Literal["x,y", "row,column"] = "x,y"
