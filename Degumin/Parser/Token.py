from dataclasses import dataclass

from Degumin.Common.File import Range


@dataclass
class Token:
    _type: str
    value: str
    _range: Range
