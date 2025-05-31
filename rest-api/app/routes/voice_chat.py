from datetime import timedelta
import io
import os
import tempfile
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse, StreamingResponse
from constants import HIGH_LEVEL_TAG
from clients import minio_client
from gradio_client import Client, handle_file
from .chat import post_chat, ChatRequest

router = APIRouter(tags=[HIGH_LEVEL_TAG])

client = Client("http://f5tts:7860/")


@router.get("/voice-chat")
async def get_voice_chat(
    game_name: str = Query(..., description="The game that the NPC belongs to."),
    npc_name: str = Query(..., description="The NPC you want to talk to."),
    voice: str = Query(..., description="The voice to use."),
    words: str = Query(..., description="What would you like to say?")
):
    # 1) Fetch from MinIO into a temp file
    try:
        obj = minio_client.get_object("default", f"voices/{voice}.wav")
        data = obj.read()
        obj.close()
        obj.release_conn()
    except Exception as e:
        raise HTTPException(404, f"MinIO error: {e}")

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    try:
        tmp.write(data)
        tmp.flush()
    finally:
        tmp.close()

    chat_response = await post_chat(ChatRequest(game_name=game_name, npc_name=npc_name, words=words))
    if(voice == 'jane'):
        ref_text = 'And so it begins'
    elif(voice == 'john'):
        ref_text = 'Subscribe to my channel'
    elif(voice == 'faras'):
        ref_text = 'ah ha a new face, what brings you to this forsaken place?'
    elif(voice == 'british'):
        ref_text = 'what can I do for you?'
    # 2) Call your Gradio TTS
    try:
        prediction = client.predict(
            ref_audio_input=handle_file(tmp.name),
            ref_text_input=ref_text,
            gen_text_input=chat_response.npc_response,
            remove_silence=False,
            randomize_seed=True,
            seed_input=0,
            cross_fade_duration_slider=0.15,
            nfe_slider=32,
            speed_slider=1,
            api_name="/basic_tts",
        )
    finally:
        os.unlink(tmp.name)

    # 3) Unwrap tuples
    if isinstance(prediction, tuple):
        prediction = prediction[0]

    # 4a) If it's a file path → stream it inline
    if isinstance(prediction, str) and os.path.exists(prediction):
        return FileResponse(
            path=prediction,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'inline; filename="{os.path.basename(prediction)}"',
                "Accept-Ranges": "bytes",
            },
        )

    # 4b) If it's raw bytes → stream inline
    if isinstance(prediction, (bytes, bytearray)):
        return StreamingResponse(
            io.BytesIO(prediction),
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'inline; filename="generated.wav"',
                "Accept-Ranges": "bytes",
            },
        )

    # 4c) If it's a list of file paths
    if (
        isinstance(prediction, list)
        and prediction
        and isinstance(prediction[0], str)
        and os.path.exists(prediction[0])
    ):
        file_path = prediction[0]
        return FileResponse(
            path=file_path,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'inline; filename="{os.path.basename(file_path)}"',
                "Accept-Ranges": "bytes",
            },
        )

    raise HTTPException(500, f"Unexpected Gradio output type: {type(prediction)}")
