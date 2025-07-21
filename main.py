import base64
import json
import os
import re
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import InferenceClient

app = FastAPI()

# Allow CORS so you can call this from frontend or other apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your Hugging Face API token
HF_TOKEN = "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"  # 🔐 Replace this with your HF token (must be PRO or have credits)
client = InferenceClient(provider="hyperbolic", api_key=HF_TOKEN)

# Prompt to guide the model's response
PROMPT_TEXT = (
    "Describe this image in detail, including its background, components, icons, "
    "style, layout, and coordinates of the text. Return the answer as numbered or bullet points, "
    "and clearly label each section. Do not use \\n or line breaks. Keep output clean and structured."
)

# Helper to extract structured JSON from markdown-like bullets
def extract_structured_json(text):
    result = {}
    matches = re.findall(r"- \*\*(.+?)\*\*:\s*(.+?)(?=(?:- \*\*|$))", text, re.DOTALL)
    for title, content in matches:
        title = title.strip()
        content = content.strip().replace("\\n", " ").replace("\n", " ").strip()
        result[title] = content
    return result

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Read uploaded image and convert to base64
        image_bytes = await file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Prepare request payload for Qwen model
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT_TEXT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }
        ]

        # Call Hugging Face Inference API
        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-VL-7B-Instruct",
            messages=messages
        )

        # Extract and clean output
        raw_output = completion.choices[0].message.content
        structured_output = extract_structured_json(raw_output)

        # Save to local file
        output_file = "output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(structured_output, f, indent=2, ensure_ascii=False)

        # Return JSON + file path
        return {
            "result": structured_output,
            "saved_to": os.path.abspath(output_file)
        }

    except Exception as e:
        return {"error": str(e)}
