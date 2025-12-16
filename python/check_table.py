import asyncio
from app.client.mysql_client import MySQLClient

async def get_table_structure():
    client = MySQLClient()
    await client.connect()
    result = await client.execute_query('DESCRIBE inscriptions')
    await client.disconnect()
    print('Inscriptions表结构:')
    for row in result:
        print(row)

asyncio.run(get_table_structure())