
# app_dual.py – Encrypted model loading + admin auth

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from security_config import verify_api_key, admin_router
from lstm_model import TwoLayerLSTM
from decrypt_loader import decrypt_model_npz
import torch
import io
import os

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

# Decrypt model from AES file
decrypted_bytes = decrypt_model_npz("dp_model_real.npz.enc")
weights = torch.load(io.BytesIO(decrypted_bytes), map_location="cpu")
if any(k.startswith("_module.") for k in weights.keys()):
    weights = {k.replace("_module.", "", 1): v for k, v in weights.items()}

# Handle nested LSTM key naming
remapped = {}
for k, v in weights.items():
    if k.startswith("lstm.l"):
        parts = k.split(".")
        layer = parts[1][-1]
        gate = parts[2]
        param = parts[3]
        new_key = f"lstm.{param}_{gate}_l{layer}" if gate in {"ih", "hh"} else k
        remapped[new_key] = v
    else:
        remapped[k] = v
weights = remapped

model = TwoLayerLSTM(input_size=2, hidden_size=64, num_layers=2, output_size=2)
model.load_state_dict(weights)
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
