
# app_dual.py – Encrypted model loading + admin auth

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from security_config import verify_api_key, admin_router
from lstm_model import TwoLayerLSTM
from decrypt_loader import decrypt_model_npz
import numpy as np
import torch
import io
import logging

app = FastAPI()

# Allow CORS for local dev and dashboard UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount admin token route
app.include_router(admin_router)

logger = logging.getLogger(__name__)

model = None


@app.on_event("startup")
async def load_model() -> None:
    """Decrypt and load the model on startup.

    Errors are logged so that the API process can stay alive for debugging
    even if decryption fails.
    """
    global model
    model = TwoLayerLSTM(input_size=2, hidden_size=64, num_layers=2, output_size=2)
    try:
        decrypted_bytes = decrypt_model_npz("dp_model_real.npz.enc")
        weights = np.load(io.BytesIO(decrypted_bytes), allow_pickle=True)
        model.load_state_dict({k: torch.tensor(v) for k, v in weights.items()})
    except Exception as exc:  # noqa: BLE001 - want to log any failure
        logger.error("Failed to decrypt or load model", exc_info=exc)
    model.eval()

@app.post("/generate_highres")
async def generate_highres(request: Request, auth=Depends(verify_api_key)):
    body = await request.json()
    num_samples = int(body.get("num_samples", 1))
    output = []
    for _ in range(num_samples):
        z = torch.randn(1, 1250, 2)
        with torch.no_grad():
            sample = model(z).numpy().tolist()
            output.append(sample)
    return {"preview": output}

@app.get("/")
def root():
    return {"message": "VitalSynth API is running with encrypted model."}
