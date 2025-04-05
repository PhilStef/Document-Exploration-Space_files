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
- I started my investigation by E
- I learned F and G which helped me conclude H
- I researched J because I was interested in K

Prepare the narrative highlighting the most important events, transitions, and actions taken so that someone new could quickly understand where to start.
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




def requestListSummary(entry, ollama=Client(host='http://localhost:11434'), model_name="llama3.2", max_retries=3, retry_delay=1):

    prompt = f"""Consider the following statements. This is the steps that someone took while completing an analysis task. Please prepare a summary of what this individual did. Write in the first person, as if you were the individual who completed this work. 

Prepare the summary so someone new can begin where this individual left off. Highlight the most important events, transitions, and actions taken so that someone new could quickly understand where to start.
Use bullet points lists or any other format to prepare your summary so that . You may use headers, bold, italics, or other formatting to help the reader understand the content.
Here is the document:

{entry}

Respond using only valid Markdown format with no extra statements or conversation.
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


def save_results(augmented, failed_docs, input_file_path):
    """
    Save processed results to output files
    
    Args:
        augmented (list): List of augmented documents with summaries
        failed_docs (list): List of documents that failed processing
        input_file_path (str): Path to the input file
        
    Returns:
        tuple: (augmented data, output file path)
    """
    # Create output directory path
    file_name = os.path.basename(input_file_path)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder_path = os.path.join(base_dir, "PreparedInteractionLogs", "04-summarized")
    
    # Create the directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    
    # Create output file paths
    timestamp = datetime.now().strftime('%m-%d_%H-%M-%S')
    output_file_path = os.path.join(folder_path, f'summarized_{file_name}')
    
    # Save augmented results
    with open(output_file_path, "w") as f:
        json.dump(augmented, f, indent=2)
    print(f"Summarized data saved to: {output_file_path}")
    
    # Save failed documents if any
    if failed_docs:
        failed_path = os.path.join(folder_path, f"failed_docs_{timestamp}.json")
        with open(failed_path, "w") as f:
            json.dump(failed_docs, f, indent=2)
        print(f"\n⚠️ {len(failed_docs)} documents failed processing. Details saved to {failed_path}")
    
    return augmented, output_file_path


if __name__ == "__main__":
    # Load MavOutput.json
    input_path = os.path.join(os.path.dirname(__file__), ".json")
    with open(input_path, "r") as f:
        data = json.load(f)

    # Process documents
    augmented, failed_docs = process_documents(data, ollama, model_name, MAX_RETRIES, RETRY_DELAY)

    # Save results
    save_results(augmented, failed_docs, os.path.dirname(__file__))