from enum import Enum, auto


class States(Enum):
    MAIN_MENU = auto()
    CLASS_SELECTION = auto()
    BASE_CLASS_SELECTION = auto()
    COMPETITION_SELECTION = auto()
    BUG_REPORT_WAIT = auto()
    FEATURE_REPORT_WAIT = auto()
