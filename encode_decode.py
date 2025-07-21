import json

# 1. Load the file
with open("sample-template.json", "r") as f:
    data = json.load(f)

# 2. Parse the canvas JSON string (NOT base64!)
canvas_str = data['project']['canvas']
try:
    canvas_json = json.loads(canvas_str)
except json.JSONDecodeError as e:
    print("❌ Failed to parse canvas JSON string:", e)
    exit()

# 3. Define replacements
replacements = {
    "socialxn applications": "my new heading",
    "• Build engaging campaigns": "• Create impactful messages",
    "• Collect user data effortlessly": "• Capture leads with ease",
    "mysite.com": "newsite.com"
}

# 4. Modify the canvas
for obj in canvas_json.get("objects", []):
    if obj.get("type") == "Text" and "text" in obj.get("attrs", {}):
        current_text = obj["attrs"]["text"]
        if current_text in replacements:
            obj["attrs"]["text"] = replacements[current_text]

# 5. Re-serialize the canvas
data['project']['canvas'] = json.dumps(canvas_json)

# 6. Save the updated JSON file
with open("updated-sample-template.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Canvas updated and saved to updated-sample-template.json")
