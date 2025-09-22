from collections import OrderedDict

from .ace import AceHtml
from .atlas import AtlasHtml
from .test import TestHtml

PRESETS_MAP = OrderedDict(
    [
        ("Atlas", AtlasHtml),
        ("TEST", TestHtml),
        ("Ace", AceHtml),
    ],
)
