import datetime

from peewee import *

from ..JsonPYAdaptors.GetGamesResult import *
from ..JsonPYAdaptors.GetPlayerResult import PlayerResult


def generate_schema(db):
    class BaseModel(Model):
        class Meta:
            database = db

    class Player(BaseModel):
        name = CharField(null=True)
        creationDate = DateTimeField(default=datetime.datetime.now)
        lastGame = DateTimeField(default=datetime.datetime.now, null=True)
        login = CharField(null=True)
        password_enc = CharField(null=True)
        telegramId = BigIntegerField(null=True)
        token = CharField(null=True)
        rating = IntegerField(default=1000)
        premium = BooleanField(default=False)

        @staticmethod
        def ToHash(player):
            return {
                "name": player.name,
                "creationDate": player.creationDate,
                "lastGame": player.lastGame,
                "token": player.token,
                "rating": player.rating,
                "premium": player.premium,
                "id": player.id
            }

        @staticmethod
        def ToClass(player):
            rv = PlayerResult()
            rv.name = player.name
            rv.creationDate = player.creationDate
            rv.lastGame = player.lastGame
            rv.token = player.token
            rv.rating = player.rating
            rv.premium = player.premium
            rv.id = player.id
            rv.telegramId = player.telegramId

            return rv

    class Game(BaseModel):
        player1 = ForeignKeyField(Player, related_name="games1", null=False)
        player2 = ForeignKeyField(Player, related_name="games2", null=False)
        start = DateTimeField(default=datetime.datetime.now)

        @staticmethod
        def ToHash(game):
            return {
                "player1": game.player1.id,
                "player2": game.player2.id,
                "start": game.start,
                "gid": game.id,
                "hasEnded": False
            }

        @staticmethod
        def ToClass(game):
            rv = GameResult()
            rv.player1 = game.player1.id
            rv.player2 = game.player2.id
            rv.start = game.start
            rv.gid = game.id
            return rv

    class GameArchieved(BaseModel):
        player1 = ForeignKeyField(Player, related_name="endedgames1", null=False)
        player2 = ForeignKeyField(Player, related_name="endedgames2", null=False)
        gameid = IntegerField()
        length = IntegerField()
        result1 = IntegerField()
        result2 = IntegerField()
        start = DateTimeField()
        end = DateTimeField()
        log = BlobField()

        @staticmethod
        def ToHash(arch):
            return {
                "player1": arch.player1.id,
                "player2": arch.player2.id,
                "gid": arch.gameid,
                "length": arch.length,
                "result1": arch.result1,
                "result2": arch.result2,
                "start": arch.start,
                "end": arch.end,
                "hasEnded": True
            }

        @staticmethod
        def ToClass(arch):
            rv = ArchGameResult()
            rv.player1 = arch.player1.id
            rv.player2 = arch.player2.id
            rv.gid = arch.gameid
            rv.length = arch.length
            rv.result1 = arch.result1
            rv.result2 = arch.result2
            rv.start = arch.start
            rv.end = arch.end
            return rv

    class PersistedGameState(BaseModel):
        state = TextField()

    return Player, Game, GameArchieved, PersistedGameState


class Database:
    def __init__(self, peewee_database):
        self.peewee_database = peewee_database
        self.tables = generate_schema(self.peewee_database)
        self.Player, self.Game, self.GameArchieved, self.PersistedGameState = self.tables


production = Database(SqliteDatabase("hive.db"))
testing = Database(SqliteDatabase("test.db"))