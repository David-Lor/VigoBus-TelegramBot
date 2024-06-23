import asyncio
import time

from vigobusbot.settings_handler import couchdb_settings
from vigobusbot.services.couchdb import CouchDB

STOPS_IDS = ['100', '1000', '10061', '1010', '1020', '1030', '1040', '1050', '1060', '1070', '110', '1110', '1120', '1130', '1140', '1150', '1160', '120', '1200', '1210', '1220', '1230', '1240', '1250', '1260', '1270', '1280', '1290', '130', '1300', '1310', '1320', '1330', '1340', '1350', '1360', '1380', '1390', '140', '1400', '1410', '14101', '14102', '14105', '14106', '14107', '14108', '14111', '14112', '14113', '14117', '14119', '14121', '14122', '14123', '14124', '14125', '14126', '14127', '14128', '14129', '14131', '14132', '14133', '14134', '14135', '14136', '14137', '14138', '14139', '14140', '14141', '14142', '14143', '14144', '14150', '14152', '14153', '14154', '14156', '14157', '14161', '14162', '14163', '14164', '14165', '14166', '14167', '14168', '14169', '14170', '14171', '14173', '14174', '14175', '14177', '14178', '14179', '14180', '14181', '14182', '14183', '14184', '14185', '14186', '14187', '14188', '14189', '14190', '14191', '14192', '14193', '14194', '14195', '14196', '14197', '14198', '14199', '1420', '14200', '14201', '14202', '14203', '14204', '14205', '14206', '14207', '14208', '14209', '14210', '14211', '14212', '14213', '14214', '14215', '14216', '14217', '14218', '14219', '14220', '14221', '14222', '14223', '14224', '14225', '14226', '14227', '14228', '14231', '14232', '14233', '14236', '14237', '14238', '14240', '14241', '14242', '14243', '14244', '14245', '14247', '14248', '14249', '14250', '14251', '14252', '14253', '14255', '14256', '14257', '14258', '14259', '14260', '14261', '14263', '14264', '14267', '14268', '14270', '14271', '14273', '14274', '14277', '14278', '14279', '14280', '14281', '14287', '14288', '14289', '14290', '14291', '14294', '14295', '14296', '14299', '1430', '14300', '14301', '14302', '14304', '14307', '14308', '14309', '14310', '14311', '14314', '14315', '14317', '14318', '14319', '14320', '14321', '14322', '14323', '14324', '14325', '14326', '14328', '14329', '14330', '14331', '14333', '14335', '14336', '14337', '14345', '14346', '14347', '14348', '14349', '14350', '14353', '14354', '14355', '14356', '14357', '14358', '14359', '14360', '14361', '14362', '14364', '14365', '14372', '14373', '14374', '14376', '14377', '14378', '14381', '14383', '14384', '14385', '14386', '14387', '14388', '14389', '14390', '14391', '14392', '14393', '14395', '14396', '14397', '14398', '1440', '14401', '14402', '14403', '14404', '14406', '14408', '14409', '14410', '14411', '14412', '14413', '14414', '14415', '14416', '14419', '14420', '14421', '14422', '14425', '14475', '1450', '1460', '1470', '1480', '14890', '14892', '14893', '14894', '14895', '14896', '14897', '14898', '14899', '1490', '14900', '14901', '14902', '14903', '14905', '14906', '14907', '14908', '14909', '14910', '14911', '150', '1500', '15001', '15002', '15003', '15004', '1510', '1520', '1530', '1540', '1550', '1560', '1570', '1580', '1590', '160', '1600', '1610', '1620', '1630', '1640', '1650', '1660', '1670', '1680', '1690', '170', '1710', '1720', '1730', '1740', '1750', '1760', '1770', '1780', '1790', '180', '1800', '1810', '1820', '1830', '1840', '1850', '1860', '1870', '1880', '1890', '190', '1900', '1910', '1920', '1930', '1940', '195', '1950', '1960', '1970', '1980', '1990', '20', '200', '2000', '20001', '20002', '20009', '20010', '20011', '20012', '20013', '20018', '20019', '20020', '20021', '20022', '20023', '20024', '20025', '20026', '20027', '20029', '20030', '20041', '20042', '20043', '20044', '20045', '20046', '20047', '20048', '20049', '20050', '20051', '20052', '20053', '20054', '20057', '20058', '20059', '20060', '20061', '20062', '20071', '20072', '20075', '20076', '20077', '20078', '20079', '20080', '20081', '20082', '20083', '20084', '20085', '20086', '20087', '20089', '20090', '20091', '20094', '20095', '20096', '20099', '2010', '20100', '20102', '20103', '20104', '20105', '20106', '20107', '20110', '20111', '20112', '20113', '20114', '20115', '20116', '20117', '20118', '20119', '20124', '20125', '20126', '20127', '20130', '20132', '20136', '20137', '20139', '20141', '20142', '20143', '20144', '20145', '20146', '20154', '20155', '20156', '20157', '20158', '20159', '20160', '20165', '20166', '20167', '20168', '20169', '20170', '20171', '20172', '20173', '20174', '20177', '20178', '20180', '20186', '20187', '20188', '20189', '20190', '20191', '20192', '20193', '20194', '20195', '20196', '20197', '20198', '20199', '2020', '20200', '20201', '20203', '20209', '20210', '20211', '20212', '20213', '20215', '20216', '20219', '20220', '2030', '2040', '2060', '2070', '2080', '2090', '210', '2100', '2110', '2130', '2140', '2150', '2160', '2170', '2180', '2190', '220', '2200', '2210', '2220', '2230', '2240', '2250', '2260', '2270', '2280', '2290', '230', '2300', '2310', '2320', '2330', '2340', '2350', '2360', '2370', '2380', '2390', '240', '2410', '2420', '2430', '2440', '2450', '2460', '2490', '250', '2500', '2510', '2520', '2540', '2550', '2560', '2570', '2580', '2590', '260', '2600', '2610', '2620', '2630', '2640', '270', '2735', '2740', '2750', '2760', '2770', '2780', '2790', '280', '2800', '2810', '2820']


async def tst_parallel():
    # This method is faster than tst_bulk_get
    r = await asyncio.gather(*[
        CouchDB.get_instance().db_stops.get(id=str(stop_id))
        for stop_id in STOPS_IDS
    ])
    print("Result (first):", r[0])


async def tst_bulk_get():
    first_doc = True
    async for doc in CouchDB.get_instance().db_stops.all_docs.ids(ids=[str(stop_id) for stop_id in STOPS_IDS]):
        if first_doc:
            print("Read doc:", doc)
            first_doc = False


async def tst_coro(coro):
    init = time.time()
    print("Running", coro.__name__)
    await coro()
    elapsed = time.time() - init
    print("Completed", coro.__name__, "Elapsed:", elapsed, "s")


async def amain():
    await CouchDB.get_instance(initialize=True).setup()
    try:
        await tst_coro(tst_parallel)
        await tst_coro(tst_bulk_get)
    finally:
        await CouchDB.get_instance().teardown()


if __name__ == '__main__':
    asyncio.run(amain())