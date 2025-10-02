import os, json, time, uuid, base64, requests

# Config
COMFYUI_API = "http://192.168.1.82:8188/prompt"
COMFYUI_HISTORY = "http://192.168.1.82:8188/history"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_FILE = os.path.join(BASE_DIR, "..", "workflows", "juggernautXL.json")
WORKFLOW_FILE = os.path.abspath(WORKFLOW_FILE)

OUTPUT_DIR = os.path.join(BASE_DIR, "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- Workflow helpers ---
def load_and_update_workflow(path, positive_prompt, negative_prompt):
    """Load workflow JSON and update prompt text nodes."""
    with open(path, "r") as f:
        workflow = json.load(f)

    workflow["2"]["inputs"]["text"] = positive_prompt
    workflow["3"]["inputs"]["text"] = negative_prompt

    return workflow


def send_to_comfyui(payload):
    resp = requests.post(COMFYUI_API, json={"prompt": payload})
    resp.raise_for_status()
    return resp.json()


def get_history(prompt_id):
    url = f"{COMFYUI_HISTORY}/{prompt_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def wait_for_result(prompt_id: str, timeout: int = 120):
    """Poll history until an image filename appears, then fetch it via /view."""
    start = time.time()

    while time.time() - start < timeout:
        history = get_history(prompt_id)

        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})

            for node_id in ["8", "7"]:
                if node_id in outputs and "images" in outputs[node_id]:
                    img_info = outputs[node_id]["images"][0]

                    filename = img_info["filename"]
                    subfolder = img_info.get("subfolder", "")
                    img_type = img_info.get("type", "output")

                    url = (
                        f"http://192.168.1.82:8188/view"
                        f"?filename={filename}&subfolder={subfolder}&type={img_type}"
                    )
                    resp = requests.get(url)
                    resp.raise_for_status()

                    b64_image = base64.b64encode(resp.content).decode("utf-8")

                    filename_local = f"{uuid.uuid4().hex}.png"
                    filepath = os.path.join(OUTPUT_DIR, filename_local)
                    with open(filepath, "wb") as f:
                        f.write(resp.content)

                    return b64_image, filepath, filename_local

        time.sleep(1)

    raise TimeoutError("Timed out waiting for ComfyUI result.")
