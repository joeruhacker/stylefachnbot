import base64, time, requests
from config import FASHN_API_KEY

BASE_URL = "https://api.fashn.ai/v1"

def _b64(img: bytes, mime="jpeg") -> str:
    return f"data:image/{mime};base64," + base64.b64encode(img).decode()

class FashnClient:
    def __init__(self, key: str = FASHN_API_KEY):
        self.h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def run(self, model_bytes: bytes, garment_bytes: bytes, category="auto") -> str:
        body = {
            "model_image":   _b64(model_bytes),
            "garment_image": _b64(garment_bytes),
            "category":      category,
            "mode":          "balanced",
            "output_format": "jpeg",
        }
        r = requests.post(f"{BASE_URL}/run", json=body, headers=self.h, timeout=30)
        r.raise_for_status()
        return r.json()["id"]

    def poll(self, pred_id: str, timeout=60) -> str:
        t0 = time.time()
        while time.time() - t0 < timeout:
            r = requests.get(f"{BASE_URL}/status/{pred_id}", headers=self.h, timeout=15)
            r.raise_for_status()
            d = r.json()
            match d["status"]:
                case "completed": return d["output"][0]
                case "failed":    raise RuntimeError(d.get("error", "FASHN failed"))
            time.sleep(3)
        raise TimeoutError("FASHN timed out")