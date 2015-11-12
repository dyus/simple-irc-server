# coding: utf-8

import asyncio

async def irc_server():
    await asyncio.start_server(handle_connection, 'localhost', 8000)

async def handle_connection(reader, writer):
    while True:
        data = await reader.read(8192)
        if not data:
            break
        print(data)
        writer.write(data)

loop = asyncio.get_event_loop()
loop.run_until_complete(irc_server())
try:
    loop.run_forever()
finally:
    loop.close()