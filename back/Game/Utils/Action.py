from enum import Enum

class Action(Enum):
    Undefined = 0
    Place = 1
    Move = 2
    Skip = 3
    Concede = 4
    Suggest = 5
    ForceEnd = 6
