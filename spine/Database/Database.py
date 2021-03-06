import datetime
import os

from peewee import *

from spine.Lobby import LobbyRoom
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

    class LobbyModel(BaseModel):
        gid = IntegerField(null=True)
        source = CharField(max_length=100, null=True)
        name = CharField(max_length=200)
        owner_id = IntegerField()
        guest_id = IntegerField(null=True)
        creationDate = DateTimeField()
        duration = IntegerField()
        expirationDate = DateTimeField()
        ownerReady = BooleanField()
        guestReady = BooleanField()
        mosquito = BooleanField()
        ladybug = BooleanField()
        pillbug = BooleanField()
        tourney = BooleanField()

        @staticmethod
        def fields():
            return [
                'gid', 'source', 'name', 'owner_id', 'guest_id', 'creationDate', 'duration', 'expirationDate',
                'ownerReady', 'guestReady', 'mosquito', 'ladybug', 'pillbug', 'tourney'
            ]

        @classmethod
        def from_instance(cls, lobby):
            model = cls()

            model.id = lobby.id
            model.gid = lobby.gid
            model.source = lobby.source
            model.name = lobby.name
            model.owner_id = lobby.owner
            model.guest_id = lobby.guest
            model.creationDate = lobby.creationDate
            model.duration = lobby.duration
            model.expirationDate = lobby.expirationDate
            model.ownerReady = lobby.ownerReady
            model.guestReady = lobby.guestReady
            model.mosquito = lobby.mosquito
            model.ladybug = lobby.ladybug
            model.pillbug = lobby.pillbug
            model.tourney = lobby.tourney

            return model

        def to_instance(self):
            lobby = LobbyRoom()

            lobby.id = self.id
            lobby.gid = self.gid
            lobby.source = self.source
            lobby.name = self.name
            lobby.owner = self.owner_id
            lobby.guest = self.guest_id
            lobby.creationDate = self.creationDate
            lobby.duration = self.duration
            lobby.expirationDate = self.expirationDate
            lobby.ownerReady = self.ownerReady
            lobby.guestReady = self.guestReady
            lobby.mosquito = self.mosquito
            lobby.ladybug = self.ladybug
            lobby.pillbug = self.pillbug
            lobby.tourney = self.tourney

            return lobby

    return Player, Game, GameArchieved, PersistedGameState, LobbyModel


class Database:
    def __init__(self, peewee_database):
        self.peewee_database = peewee_database
        self.tables = generate_schema(self.peewee_database)
        self.Player, self.Game, self.GameArchieved, self.PersistedGameState, self.LobbyModel = self.tables


database_directory = os.getenv('HIVE_DATABASE_DIR') or '.'

production = Database(SqliteDatabase(os.path.join(database_directory, "hive.db")))
testing = Database(SqliteDatabase(os.path.join(database_directory, "test.db")))
