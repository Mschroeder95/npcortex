from fastapi import FastAPI
from routes import chat, embed, npc, file, game, generate

app = FastAPI(title="NPCortex")
app.include_router(chat.router)
app.include_router(embed.router)
app.include_router(npc.router)
app.include_router(file.router)
app.include_router(game.router)
app.include_router(generate.router)