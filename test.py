import asyncio, websockets, json

async def test_ws():
    uri = "ws://192.168.68.135:8188/ws"
    async with websockets.connect(uri) as ws:
        while True:
            msg = await ws.recv()
            print("Received:", msg)

asyncio.run(test_ws())
