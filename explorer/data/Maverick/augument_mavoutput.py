import json
import os
import re
import time
from datetime import datetime
from ollama import Client
from tqdm import tqdm

# Set up Ollama client
ollama = Client(host='http://localhost:11434')
model_name = "llama3.2"
MAX_RETRIES = 3  # Number of retry attempts for each document
RETRY_DELAY = 1  # Delay between retries in seconds

# Load MavOutput.json
input_path = os.path.join(os.path.dirname(__file__), "mavOutput.json")
with open(input_path, "r") as f:
    data = json.load(f)

augmented = []
failed_docs = []

for entry in tqdm(data, desc="Augmenting documents"):
    doc_id = entry.get("id")
    title = entry.get("title")
    date = entry.get("date")
    contents = entry.get("contents")

    prompt = f"""You are an intelligence analyst.
Here is a document:

{contents}

Please extract the following:
- A brief summary of the document.
- Key named entities as tuples of type and name. This could be an 'ORG', 'CARDINAL', 'DATE', 'GPE', 'PERSON', 'MONEY', 'PRODUCT', 'TIME', 'PERCENT', 'WORK_OF_ART', 'QUANTITY', 'NORP', 'LOC', 'EVENT', 'ORDINAL', 'FAC', 'LAW', 'LANGUAGE' or any other appropriate concept.
- 3-5 relevant topics, where each topic is at most 2 words long.

Respond using only valid JSON format with no extra characters.

Please follow this format:

{{
  "summary": "...",
  "entities": [
    {{
    "type": "<type of entity>", 
    "name": "<the name of the identified thing>", 
    }},    
    "..."
    ],
  "topics": ["...", "...", "...", "..."]
}}"""

    success = False
    attempt = 0
    content = ""
    
    while not success and attempt < MAX_RETRIES:
        attempt += 1
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response['message']['content'].strip()

            # Extract JSON using regex
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if not json_match:
                raise ValueError(f"Attempt {attempt}/{MAX_RETRIES}: No JSON object found in model response.")

            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            
            # Validate required fields exist
            if not all(key in parsed for key in ["summary", "entities", "topics"]):
                missing = [k for k in ["summary", "entities", "topics"] if k not in parsed]
                raise ValueError(f"Attempt {attempt}/{MAX_RETRIES}: Missing required fields: {', '.join(missing)}")

            augmented.append({
                "id": doc_id,
                "source": title,
                "date": date,
                "summary": parsed.get("summary"),
                "entities": parsed.get("entities", []),
                "topics": parsed.get("topics", [])
            })
            
            success = True
            if attempt > 1:
                print(f"\n✓ Successfully processed doc {doc_id} on attempt {attempt}")

        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"\n⚠️ Error on attempt {attempt}/{MAX_RETRIES} for doc {doc_id} ({title}): {e}")
                print(f"Waiting {RETRY_DELAY}s before retrying...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"\n❌ Failed all {MAX_RETRIES} attempts for doc {doc_id} ({title}): {e}")
                print("Final model response:")
                print(repr(content))
                failed_docs.append({
                    "id": doc_id,
                    "source": title,
                    "error": str(e),
                    "final_response": content
                })

# Save to augmentedMavOutput.json
timestamp = datetime.now().strftime('%m-%d_%H-%M-%S')
output_path = os.path.join(os.path.dirname(__file__), f"augmentedMavOutput_{timestamp}.json")
with open(output_path, "w") as f:
    json.dump(augmented, f, indent=2)

# Save failed documents for analysis
if failed_docs:
    failed_path = os.path.join(os.path.dirname(__file__), f"failed_docs_{timestamp}.json")
    with open(failed_path, "w") as f:
        json.dump(failed_docs, f, indent=2)
    print(f"\n⚠️ {len(failed_docs)} documents failed processing. Details saved to failed_docs_{timestamp}.json")

print(f"\n✅ Done! Saved {len(augmented)} augmented entries to augmentedMavOutput_{timestamp}.json")
print(f"Success rate: {len(augmented)}/{len(data)} ({len(augmented)/len(data)*100:.1f}%)")