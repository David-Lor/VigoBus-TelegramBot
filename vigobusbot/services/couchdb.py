import asyncio

import aiocouch
from aiocouch.exception import ConflictError

from vigobusbot.settings_handler import couchdb_settings
from vigobusbot.utils import Singleton, SetupTeardown
from vigobusbot.logger import logger

__all__ = ["CouchDB", "ConflictError"]


class CouchDB(Singleton, SetupTeardown):
    connection: aiocouch.CouchDB
    db_sent_messages: aiocouch.Database = None
    db_user_stops: aiocouch.Database = None

    def __init__(self):
        self.connection = aiocouch.CouchDB(
            server=couchdb_settings.url,
            user=couchdb_settings.user,
            password=couchdb_settings.password.get_secret_value(),
        )

    async def setup(self):
        await self.connection.check_credentials()
        self.db_sent_messages, self.db_user_stops = await asyncio.gather(
            self._get_db(couchdb_settings.db_sent_messages),
            self._get_db(couchdb_settings.db_user_stops),
        )

    async def teardown(self):
        logger.debug("Closing CouchDB connection...")
        await self.connection.close()
        logger.info("CouchDB closed")

    async def _get_db(self, name: str) -> aiocouch.Database:
        if couchdb_settings.create_databases:
            return await self.connection.create(name, exists_ok=True)
        # noinspection PyUnresolvedReferences
        return await self.connection[name]

    @classmethod
    async def create_doc(cls, db: aiocouch.Database, doc_id: str, doc_data: dict, exists_ok: bool = False):
        doc = await db.create(id=doc_id, data=doc_data, exists_ok=exists_ok)
        await doc.save()
        return doc

    @classmethod
    async def update_doc(cls, db: aiocouch.Database, doc_id: str, doc_data: dict):
        """Update the doc matching by id, with the given data.
        Any data given is overriden in the found document.
        If document not found, create a new one.
        """
        try:
            doc = await db.get(id=doc_id)
            doc.update(doc_data)
            await doc.save()
            return doc
        except aiocouch.NotFoundError:
            return await cls.create_doc(db=db, doc_id=doc_id, doc_data=doc_data, exists_ok=False)
