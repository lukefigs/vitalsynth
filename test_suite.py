import io
import numpy as np
import torch
from fastapi.testclient import TestClient
from jose import jwt

from app_dual import app
from decrypt_loader import decrypt_model_npz
from security_config import SECRET_KEY, ALGORITHM

client = TestClient(app)

API_KEY_HEADER = {"X-API-Key": "dev-secret-key"}


def test_generate_highres_output_shape_content():
    response = client.post(
        "/generate_highres",
        headers=API_KEY_HEADER,
        json={"num_samples": 2},
    )
    assert response.status_code == 200
    data = response.json()["preview"]
    assert len(data) == 2
    first = data[0]
    assert len(first) == 1
    assert len(first[0]) == 1250
    assert len(first[0][0]) == 2
    assert isinstance(first[0][0][0], float)


def test_aes_decryption_loads_model():
    decrypted = decrypt_model_npz("dp_model_real.npz.enc")
    state = torch.load(io.BytesIO(decrypted), map_location="cpu")
    assert isinstance(state, dict)
    assert "_module.lstm.weight_ih_l0" in state


def test_generated_signal_fidelity():
    response = client.post(
        "/generate_highres",
        headers=API_KEY_HEADER,
        json={"num_samples": 1},
    )
    assert response.status_code == 200
    arr = np.array(response.json()["preview"], dtype=float)
    assert arr.std() > 0.0


def test_admin_login_returns_valid_jwt():
    resp = client.post(
        "/admin/token",
        data={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    assert token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "admin"
