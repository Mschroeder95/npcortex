import os
from config import STATIC_DIR
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import talk, collection, embed, npc, file

app = FastAPI(title="NPCortex")
os.makedirs(f'{STATIC_DIR}', exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name=STATIC_DIR)
app.include_router(talk.router)
app.include_router(collection.router)
app.include_router(embed.router)
app.include_router(npc.router)
app.include_router(file.router)