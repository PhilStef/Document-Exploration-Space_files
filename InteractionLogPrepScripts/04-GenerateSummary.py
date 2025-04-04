import json
import os
import re
import time
from datetime import datetime
from ollama import Client

def process_document(entry, ollama=Client(host='http://localhost:11434'), model_name="llama3.2", max_retries=3, retry_delay=1):
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

    attempt = 0
    content = ""

    while attempt < max_retries:
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
                raise ValueError(f"Attempt {attempt}/{max_retries}: No JSON object found in model response.")

            json_str = json_match.group(0)
            parsed = json.loads(json_str)

            # Validate required fields exist
            if not all(key in parsed for key in ["summary", "entities", "topics"]):
                missing = [k for k in ["summary", "entities", "topics"] if k not in parsed]
                raise ValueError(f"Attempt {attempt}/{max_retries}: Missing required fields: {', '.join(missing)}")

            return {
                "id": doc_id,
                "source": title,
                "date": date,
                "summary": parsed.get("summary"),
                "entities": parsed.get("entities", []),
                "topics": parsed.get("topics", [])
            }

        except Exception as e:
            if attempt < max_retries:
                print(f"\n⚠️ Error on attempt {attempt}/{max_retries} for doc {doc_id} ({title}): {e}")
                print(f"Waiting {retry_delay}s before retrying...")
                time.sleep(retry_delay)
            else:
                print(f"\n❌ Failed all {max_retries} attempts for doc {doc_id} ({title}): {e}")
                print("Final model response:")
                print(repr(content))
                return {
                    "id": doc_id,
                    "source": title,
                    "error": str(e),
                    "final_response": content
                }


def requestNarrativeSummary(entry, ollama=Client(host='http://localhost:11434'), model_name="llama3.2", max_retries=3, retry_delay=1):

    prompt = f"""Consider the following statements. This is the work that someone else has completed while completing an analysis task. Please write a narrative summary of what this individual did. Write in the first person, as if you were the individual who completed this work. Use phrases like:
- To learn more about A, I did B
- I was able to do C because of D
- I researched Y because I was interested in Z
- I learned A and B which helped me conclude C

Prepare the narrative highlighting the most important events and actions taken so that someone new could quickly understand where to start.
Do not use bullet points. Do not use a list. Do not use a table. Do not use any other format. Just write a narrative summary in the first person. You may use headers, bold, italics, or other formatting to help the reader understand the content.
Here is the document:

{entry}

Respond using only valid Markdown format with no extra characters.
"""

    attempt = 0
    content = ""

    while attempt < max_retries:
        attempt += 1
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response['message']['content'].strip()

            # todo check if markdown is valid.
            return content

        except Exception as e:
            if attempt < max_retries:
                print(f"\n⚠️ Error on attempt {attempt}/{max_retries} for doc {doc_id} ({title}): {e}")
                print(f"Waiting {retry_delay}s before retrying...")
                time.sleep(retry_delay)
            else:
                print(f"\n❌ Failed all {max_retries} attempts for doc {doc_id} ({title}): {e}")
                print("Final model response:")
                print(repr(content))
                return {
                    "id": doc_id,
                    "source": title,
                    "error": str(e),
                    "final_response": content
                }



def process_documents(data, ollama, model_name, max_retries=3, retry_delay=1):
    augmented = []
    failed_docs = []

    for entry in tqdm(data, desc="Augmenting documents"):
        result = process_document(entry, ollama, model_name, max_retries, retry_delay)
        if "error" in result:
            failed_docs.append(result)
        else:
            augmented.append(result)

    return augmented, failed_docs


def save_results(augmented, failed_docs, output_dir):
    timestamp = datetime.now().strftime('%m-%d_%H-%M-%S')

    # Save augmented results
    output_path = os.path.join(output_dir, f"augmentedMavOutput_{timestamp}.json")
    with open(output_path, "w") as f:
        json.dump(augmented, f, indent=2)

    # Save failed documents
    if failed_docs:
        failed_path = os.path.join(output_dir, f"failed_docs_{timestamp}.json")
        with open(failed_path, "w") as f:
            json.dump(failed_docs, f, indent=2)
        print(f"\n⚠️ {len(failed_docs)} documents failed processing. Details saved to failed_docs_{timestamp}.json")

    print(f"\n✅ Done! Saved {len(augmented)} augmented entries to augmentedMavOutput_{timestamp}.json")
    print(f"Success rate: {len(augmented)}/{len(augmented) + len(failed_docs)} ({len(augmented)/(len(augmented) + len(failed_docs))*100:.1f}%)")


if __name__ == "__main__":
    # Load MavOutput.json
    input_path = os.path.join(os.path.dirname(__file__), "mavOutput.json")
    with open(input_path, "r") as f:
        data = json.load(f)

    # Process documents
    augmented, failed_docs = process_documents(data, ollama, model_name, MAX_RETRIES, RETRY_DELAY)

    # Save results
    save_results(augmented, failed_docs, os.path.dirname(__file__))