# npcortex
A backend API for creating and interacting with an Ai Game.

## Build
```powershell
docker-compose up --build -d
docker-compose exec ollama sh -c 'ollama pull $OLLAMA_MODEL && ollama pull $OLLAMA_EMBED_MODEL && ollama pull $OLLAMA_CHAT_MODEL'
docker-compose exec minio sh -c 'mc alias set myminio http://127.0.0.1:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD'
docker-compose exec minio sh -c 'mc admin accesskey create myminio/ $MINIO_ROOT_USER --access-key $MINIO_ACCESS_KEY --secret-key $MINIO_SECRET_KEY'
```

## Logging into MINIO
The username and password are in the .env file

## Delete A Non-Empty MinIO Bucket
```powershell
docker-compose exec minio sh -c 'mc alias set myminio http://127.0.0.1:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD'
docker-compose exec minio sh -c 'mc rm -r --force data/<bucket-path>'
```

## Want to load a new model?
- WARNING (this will delete any NPCortex data that you have created)
- make sure that the embed model is compatiable with embedding.
- update the .env with your selected models.

```powershell
docker compose down
docker compose down -v
```
- restart your terminal
```powershell
docker-compose up --build -d
docker-compose exec ollama sh -c 'ollama pull $OLLAMA_MODEL && ollama pull $OLLAMA_EMBED_MODEL && ollama pull $OLLAMA_CHAT_MODEL'
docker-compose exec minio sh -c 'mc alias set myminio http://127.0.0.1:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD'
docker-compose exec minio sh -c 'mc admin accesskey create myminio/ $MINIO_ROOT_USER --access-key $MINIO_ACCESS_KEY --secret-key $MINIO_SECRET_KEY'
```



# Features
- Player context management and creation
- custom game rules
- custom character stats for npc and players
- custom resposne format
- .wav in .wav out chat interface
- character image generation
- location/setting image generation