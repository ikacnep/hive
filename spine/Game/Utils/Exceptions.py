class HiveError(Exception):
    pass


class ActionImpossible(HiveError):
    pass


class NoActions(HiveError):
    pass


class FigureMiss(HiveError):
    pass


class UnknownAction(HiveError):
    pass


class PlayerIDException(HiveError):
    pass


class PlayerNotFoundException(HiveError):
    pass


class GameNotFoundException(HiveError):
    pass


class PlayerCreationException(HiveError):
    pass


class PlayerModificationException(HiveError):
    pass

class QuickGameCreationException(HiveError):
    pass

class LobbyNotFoundException(HiveError):
    pass

class QuickGameNotFoundException(HiveError):
    pass

class CannotJoinLobbyException(HiveError):
    pass

class AccessException(HiveError):
    pass