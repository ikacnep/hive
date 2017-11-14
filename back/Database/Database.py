from peewee import *
import datetime

db = SqliteDatabase("hive.db")

class BaseModel(Model):
    class Meta:
        database = db

class Player(BaseModel):
    name = CharField(null=True)
    creationDate = DateTimeField(default=datetime.datetime.now)
    lastGame = DateTimeField(default=datetime.datetime.now, null=True)
    login = CharField(null=True)
    password = CharField(null=True)
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

class Game(BaseModel):
    player1 = ForeignKeyField(Player, related_name="games1", null=False)
    player2 = ForeignKeyField(Player, related_name="games2", null=False)
    start = DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def ToHash(game):
        return {
            "player1":game.player1.id,
            "player2":game.player2.id,
            "start":game.start,
            "gid":game.id,
            "hasEnded":False
        }

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
            "player1":arch.player1.id,
            "player2":arch.player2.id,
            "gid":arch.gameid,
            "length":arch.length,
            "result1":arch.result1,
            "result2":arch.result2,
            "start":arch.start,
            "end":arch.end,
            "hasEnded":True
        }