import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ollama import AsyncClient
import httpx

app = FastAPI(title="Customer Agent")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = "qwen2.5:0.5b"


class CustomerMessage(BaseModel):
    customer_id: str
    message: str
    model: str | None = None


@app.get("/")
def health_check():
    return {
        "status": "running",
        "agent": "customer-agent",
    }


@app.get("/models")
async def get_models():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            response.raise_for_status()

        return {"models": [m["name"] for m in response.json()["models"]]}

    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/message")
async def receive_message(data: CustomerMessage):
    try:
        client = AsyncClient(host=OLLAMA_URL)

        model = data.model or MODEL

        if data.model:
            async with httpx.AsyncClient() as http:
                response = await http.get(f"{OLLAMA_URL}/api/tags")
                response.raise_for_status()

            installed_models = [m["name"] for m in response.json()["models"]]

            if model not in installed_models:
                raise HTTPException(
                    status_code=400,
                    detail=f"Model not installed: {model}",
                )

        response = await client.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a customer support assistant. "
                        "Reply in Persian, briefly and politely. "
                        "Keep answers short and direct."
                    ),
                },
                {
                    "role": "user",
                    "content": data.message,
                },
            ],
            options={
                "num_predict": 128,
            },
            keep_alive="10m",
        )

        ai_response = response.message.content

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama SDK error: {repr(e)}",
        )

    return {
        "customer_id": data.customer_id,
        "model": model,
        "received_message": data.message,
        "ai_response": ai_response,
    }
