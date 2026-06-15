from enum import Enum


class InteractionMode(Enum):
    SELECT_CENTER = 0
    ADD_POINT = 1
    MOVE_POINT = 2
    DELETE_POINT = 3


class MovePointMode(Enum):
    DRAG_AND_DROP = 0
    CLICK_TO_MOVE = 1
