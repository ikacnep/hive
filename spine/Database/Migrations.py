from playhouse.migrate import SqliteMigrator, migrate

from .Database import production as db


def _lobby_add_expiration_date(migrator):
    columns = db.peewee_database.get_columns('LobbyModel')
    columns = set(column.name for column in columns)

    if 'expirationDate' in columns:
        return 0

    column = db.LobbyModel.expirationDate
    column.null = True

    migrate(migrator.add_column('LobbyModel', 'expirationDate', column))

    for lobby_model in db.LobbyModel.select():
        lobby = lobby_model.to_instance()
        lobby.update_expiration_date()
        new_model = lobby.from_instance()

        for field in db.LobbyModel.fields():
            setattr(lobby_model, field, getattr(new_model, field))

        lobby_model.update()

    migrate(migrator.drop_not_null('LobbyModel', 'expirationDate'))

    return 1


def migrate_everything():
    migrator = SqliteMigrator(db.peewee_database)

    migrations_done = 0

    for table in db.tables:
        if not table.table_exists():
            table.create_table()

    with db.peewee_database.transaction():
        migrations_done += _lobby_add_expiration_date(migrator)


    return migrations_done
