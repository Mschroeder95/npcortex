# npcortex
A backend API for creating and interacting with an Ai Game.

## Build
```Bash
docker-compose up --build -d
docker-compose exec ollama sh -c 'ollama pull $OLLAMA_MODEL && ollama pull $OLLAMA_EMBED_MODEL'
docker-compose exec minio sh -c 'mc alias set myminio http://127.0.0.1:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD'
docker-compose exec minio sh -c 'mc admin accesskey create myminio/ $MINIO_ROOT_USER --access-key $MINIO_ACCESS_KEY --secret-key $MINIO_SECRET_KEY'
```

## Delete A Non-Empty Bucket
```Bash
docker-compose exec minio sh -c 'mc alias set myminio http://127.0.0.1:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD'
docker-compose exec minio sh -c 'mc rm -r --force data/<bucket-path>'
```