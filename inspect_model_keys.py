
import torch

def main():
    path = "dp_model_real.npz"
    print(f"Loading model from: {path}")
    try:
        state_dict = torch.load(path, map_location="cpu")
        print(f"\n🔑 Found {len(state_dict)} keys in model:\n")
        for k in list(state_dict.keys())[:50]:
            print(f"- {k}")
        if len(state_dict) > 50:
            print("\n...output truncated (showing first 50 keys)...")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")

if __name__ == "__main__":
    main()
