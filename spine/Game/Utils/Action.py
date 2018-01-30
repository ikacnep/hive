from enum import IntEnum


class Action(IntEnum):
    Undefined = 0

    Place = 1
    Move = 2
    Skip = 3
    Concede = 4
    Suggest = 5
    ForceEnd = 6

    CreateGame = 7
    GetGames = 8

    GetPlayer = 9
    CreatePlayer = 10
    ModifyPlayer = 11
    GetOrCreatePlayer = 12

    def Name(self):
        return self.name.lower()
