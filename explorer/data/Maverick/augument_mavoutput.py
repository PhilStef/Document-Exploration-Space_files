import json
import os
import re
from datetime import datetime
from ollama import Client
from tqdm import tqdm

# Set up Ollama client
ollama = Client(host='http://localhost:11434')
model_name = "llama3.2"

# Load MavOutput.json
input_path = os.path.join(os.path.dirname(__file__), "mavOutput.json")
with open(input_path, "r") as f:
    data = json.load(f)

augmented = []

for entry in tqdm(data, desc="Augmenting documents"):
    doc_id = entry.get("id")
    title = entry.get("title")
    contents = entry.get("contents")

    prompt = f"""You are an intelligence analyst.
Here is a document:

{contents}

Please extract the following:
- A brief summary of the document.
- Key named entities (people, places, organizations).
- 3-5 relevant topics, where each topic is at most 2 words long.

Respond in this JSON format:

{{
  "summary": "...",
  "entities": ["..."],
  "topics": ["...", "...", "..."]
}}"""

    try:
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response['message']['content'].strip()

        # Extract JSON using regex
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in model response.")

        json_str = json_match.group(0)
        parsed = json.loads(json_str)
        augmented.append({
            "id": doc_id,
            "title": title,
            "summary": parsed.get("summary"),
            "entities": parsed.get("entities", []),
            "topics": parsed.get("topics", [])
        })

    except Exception as e:
        print(f"\n❌ Error processing doc {doc_id} ({title}): {e}")
        print("Model response:")
        print(repr(content))
        continue

# Save to augmentedMavOutput.json
timestamp = datetime.now().strftime('%m-%d_%H-%M-%S')
output_path = os.path.join(os.path.dirname(__file__), f"augmentedMavOutput_{timestamp}.json")
with open(output_path, "w") as f:
    json.dump(augmented, f, indent=2)

print(f"\n✅ Done! Saved {len(augmented)} augmented entries to augmentedMavOutput.json")