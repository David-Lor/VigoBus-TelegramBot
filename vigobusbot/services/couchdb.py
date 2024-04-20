import aiocouch

from vigobusbot.settings_handler import couchdb_settings
from vigobusbot.utils import Singleton


class CouchDB(Singleton):
    def __init__(self):
        self.connection = aiocouch.CouchDB(
            server=couchdb_settings.url,
            user=couchdb_settings.user,
            password=couchdb_settings.password.get_secret_value(),
        )

    async def initialize(self):
        await self.connection.check_credentials()

    async def close(self):
        await self.connection.close()
