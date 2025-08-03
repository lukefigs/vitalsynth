
import requests
import numpy as np
import os

class VitalSynthClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def health(self):
        return requests.get(f"{self.base_url}/").json()

    def generate(self, num_samples=10, edge_cases=False, out_file=None):
        payload = {
            "num_samples": num_samples,
            "edge_cases": edge_cases
        }
        response = requests.post(f"{self.base_url}/generate", json=payload)
        response.raise_for_status()
        data = response.json()["data"]
        arr = np.array(data)
        if out_file:
            np.save(out_file, arr)
        return arr

    def generate_plus(self, num_samples=10, edge_cases=True, format="npy", out_file="synthetic_out"):
        data = self.generate(num_samples, edge_cases)
        if format == "npy":
            np.save(f"{out_file}.npy", data)
        elif format == "csv":
            flat = data.reshape(data.shape[0], -1)
            np.savetxt(f"{out_file}.csv", flat, delimiter=",")
        else:
            raise ValueError("Format must be 'npy' or 'csv'")
        return data

    def save_csv(self, data, out_file="synthetic.csv"):
        flat = data.reshape(data.shape[0], -1)
        np.savetxt(out_file, flat, delimiter=",")
