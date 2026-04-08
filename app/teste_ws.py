import asyncio
import websockets

async def teste():
    uri = "ws://127.0.0.1:8000/chat/ws/1"
    async with websockets.connect(uri) as ws:
        print("Ligado!")
        await ws.send("O meu computador não liga")
        resposta = await ws.recv()
        print("IA:", resposta)

asyncio.run(teste())