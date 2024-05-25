import asyncio
from vigobusbot.services.couchdb import CouchDB
from vigobusbot.services.elasticsearch import ElasticSearch
from vigobusbot.persistence.stops import StopsCouchDBRepository, StopsElasticSearchRepository
from vigobusbot.utils import async_gather_limited


async def amain():
    couchdb = CouchDB.get_instance(initialize=True)
    elasticsearch = ElasticSearch.get_instance(initialize=True)
    await asyncio.gather(couchdb.setup(), elasticsearch.setup())

    try:
        stops = await StopsCouchDBRepository.get_all_stops()
        stops_coros = [
            StopsElasticSearchRepository.save_stop(stop)
            for stop in stops
        ]

        await async_gather_limited(*stops_coros, limit=30)

    finally:
        await asyncio.gather(couchdb.teardown(), elasticsearch.teardown())

if __name__ == '__main__':
    asyncio.run(amain())
