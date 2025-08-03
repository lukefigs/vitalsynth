
# clean_and_encrypt_model.py

import torch
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from lstm_model import TwoLayerLSTM

# --- Load and Reformat Model ---
print("🔄 Loading model from dp_model_real.npz...")
model = TwoLayerLSTM(input_size=2, hidden_size=64, num_layers=2, output_size=2)
data = np.load("dp_model_real.npz", allow_pickle=True)
state_dict = {k: torch.tensor(v) for k, v in data.items()}
model.load_state_dict(state_dict)

# --- Save Clean .npz ---
print("💾 Saving cleaned dp_model_real_clean.npz...")
clean_state = {k: v.numpy() for k, v in model.state_dict().items()}
np.savez("dp_model_real_clean.npz", **clean_state)

# --- Encrypt Clean File ---
print("🔐 Encrypting with AES-256...")
key = b"12345678901234567890123456789012"  # replace with your actual 32-byte key
cipher = AES.new(key, AES.MODE_CBC)
iv = cipher.iv

with open("dp_model_real_clean.npz", "rb") as f:
    raw = f.read()

ct = cipher.encrypt(pad(raw, AES.block_size))

with open("dp_model_real_clean.npz.enc", "wb") as f:
    f.write(iv + ct)

print("✅ Done: Saved as dp_model_real_clean.npz.enc")
