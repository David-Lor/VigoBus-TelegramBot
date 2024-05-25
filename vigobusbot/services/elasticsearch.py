import elasticsearch

from vigobusbot.utils import Singleton, SetupTeardown
from vigobusbot.settings_handler import elastic_settings
from vigobusbot.logger import logger


class ElasticSearch(Singleton, SetupTeardown):

    def __init__(self):
        self.client = elasticsearch.AsyncElasticsearch(
            hosts=str(elastic_settings.url),
            basic_auth=elastic_settings.basic_auth_tuple,
        )

    async def setup(self):
        logger.debug("Initializing ElasticSearch...")
        # Create Stops index
        await self.create_index(
            name=elastic_settings.stops_index,
            mappings={
                "properties": {
                    "name": {
                        "type": "text",
                        "analyzer": "spanish"
                    }
                }
            }
        )
        logger.info("ElasticSearch initialized")

    async def teardown(self):
        logger.debug("Closing ElasticSearch...")
        await self.client.close()
        logger.info("ElasticSearch closed")

    async def create_index(self, name: str, mappings: dict, **kwargs):
        if not await self.client.indices.exists(index=name):
            await self.client.indices.create(index=name, mappings=mappings, **kwargs)
