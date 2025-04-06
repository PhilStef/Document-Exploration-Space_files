import os
import json
import random
import argparse
from datetime import datetime
import time
import openai
from ollama import Client
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

def load_environment_variables():
    """
    Load environment variables for API access
    
    Returns:
        bool: True if environment variables are set up correctly
    """
    # Check for OpenAI API key
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("⚠️ Warning: OPENAI_API_KEY environment variable not set.")
        print("If you want to use ChatGPT, please set this variable.")
        return False
    else:
        openai.api_key = openai_api_key
        return True

def chunk_text(text, max_chunk_size=4000):
    """
    Split text into chunks that fit within the model's context window
    
    Args:
        text (str): Text to chunk
        max_chunk_size (int): Maximum size of each chunk
        
    Returns:
        list: List of text chunks
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Find a good breaking point (sentence end or paragraph)
        end = min(start + max_chunk_size, len(text))
        
        if end < len(text):
            # Try to find a sentence break
            for break_char in ['.', '!', '?', '\n']:
                last_break = text.rfind(break_char, start, end)
                if last_break != -1 and last_break > start + max_chunk_size // 2:
                    end = last_break + 1  # Include the break character
                    break
        
        chunks.append(text[start:end])
        start = end
    
    return chunks

# Define prompts as variables
NARRATIVE_PROMPT_TEMPLATE = """I'll provide you with a list of actions someone performed during an analysis task. 
Please write a cohesive first-person narrative that describes what they did.
Focus on creating a flowing story that explains their process and insights.

Here are the actions:

{text}

Write a natural, first-person narrative (250-500 words) as if you were this person describing their work.
Do not simply list the actions - transform them into a coherent story about the analysis process.
Use markdown formatting for headers, emphasis, and other text styling."""

LIST_PROMPT_TEMPLATE = """Consider the following statements. This is the steps that someone took while completing an analysis task.
Please prepare a summary of what this individual did. Write in the first person, as if you were the individual who completed this work.

{text}

Please format your response using markdown with:
- A structured overview with headers
- Key entities or documents I worked with in bold
- Important insights or findings in italic
- A concise conclusion

Make sure the summary is well-organized and easy to follow."""

def request_narrative_from_chatgpt(text, prompt_template=NARRATIVE_PROMPT_TEMPLATE, model="gpt-3.5-turbo"):
    """
    Request a narrative summary from ChatGPT API
    
    Args:
        text (str): Text to summarize
        prompt_template (str): Template for the prompt
        model (str): ChatGPT model to use
        
    Returns:
        str: Narrative summary text
    """
    print(f"Requesting narrative summary from ChatGPT ({model})...")
    
    prompt = prompt_template.format(text=text)
    
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes user activity logs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error calling ChatGPT API: {e}")
        return f"Error generating narrative summary: {str(e)}"

def request_list_from_chatgpt(text, prompt_template=LIST_PROMPT_TEMPLATE, model="gpt-3.5-turbo"):
    """
    Request a list summary from ChatGPT API
    
    Args:
        text (str): Text to summarize
        prompt_template (str): Template for the prompt
        model (str): ChatGPT model to use
        
    Returns:
        str: List summary text
    """
    print(f"Requesting list summary from ChatGPT ({model})...")
    
    prompt = prompt_template.format(text=text)
    
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes user activity logs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error calling ChatGPT API: {e}")
        return f"Error generating list summary: {str(e)}"

def request_narrative_from_ollama(text, prompt_template=NARRATIVE_PROMPT_TEMPLATE, model="llama3.2", max_retries=3, retry_delay=1):
    """
    Request a narrative summary from local Ollama instance
    
    Args:
        text (str): Text to summarize
        prompt_template (str): Template for the prompt
        model (str): Ollama model to use
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        str: Narrative summary text
    """
    print(f"Requesting narrative summary from Ollama ({model})...")
    
    prompt = prompt_template.format(text=text)
    
    ollama = Client(host='http://localhost:11434')
    attempt = 0
    
    while attempt < max_retries:
        attempt += 1
        try:
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
            
        except Exception as e:
            print(f"Error on attempt {attempt}: {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    return f"Error: Maximum retries exceeded when calling Ollama for narrative summary"

def request_list_from_ollama(text, prompt_template=LIST_PROMPT_TEMPLATE, model="llama3.2", max_retries=3, retry_delay=1):
    """
    Request a list summary from local Ollama instance
    
    Args:
        text (str): Text to summarize
        prompt_template (str): Template for the prompt
        model (str): Ollama model to use
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        str: List summary text
    """
    print(f"Requesting list summary from Ollama ({model})...")
    
    prompt = prompt_template.format(text=text)
    
    ollama = Client(host='http://localhost:11434')
    attempt = 0
    
    while attempt < max_retries:
        attempt += 1
        try:
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
            
        except Exception as e:
            print(f"Error on attempt {attempt}: {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    return f"Error: Maximum retries exceeded when calling Ollama for list summary"

def validate_markdown(text):
    """
    Check if the generated text contains markdown formatting
    
    Args:
        text (str): Text to validate
        
    Returns:
        bool: True if text contains markdown formatting
    """
    markdown_patterns = [
        '# ',         # Headers
        '## ',
        '### ',
        '**',         # Bold
        '*',          # Italic
        '- ',         # List items
        '1. ',        # Numbered list
        '[',          # Links
        '```'         # Code blocks
    ]
    
    for pattern in markdown_patterns:
        if pattern in text:
            return True
    return False

def load_input_file(input_file_path):
    """
    Load input file, supporting both JSON and text formats
    
    Args:
        input_file_path (str): Path to the input file
        
    Returns:
        str: Text content to summarize
    """
    file_ext = os.path.splitext(input_file_path)[1].lower()
    
    try:
        if file_ext == '.json':
            print("Loading JSON file...")
            with open(input_file_path, 'r') as file:
                data = json.load(file)
                print(f"JSON file loaded successfully.")
                
                # Check for session_narrative field
                if "session_narrative" in data:
                    return data["session_narrative"]
                elif "all_summaries" in data:
                    return data["all_summaries"]
                else:
                    # Try to find any field that might contain the narrative
                    for key, value in data.items():
                        if isinstance(value, str) and len(value) > 500:  # Assuming narratives are typically long
                            print(f"Using field '{key}' as narrative source")
                            return value
                    
                    print("No suitable narrative found in JSON. Using entire JSON as string.")
                    return json.dumps(data)
                    
        else:  # Treat as text file
            print("Loading text file...")
            with open(input_file_path, 'r') as file:
                text = file.read()
                print(f"Text file loaded successfully.")
                return text
                
    except Exception as e:
        print(f"Error loading file: {e}")
        return ""

def generate_summary(input_file_path, provider="chatgpt", summary_type=None, 
                     chatgpt_model="gpt-3.5-turbo", ollama_model="llama3.2", 
                     should_chunk=False, max_chunk_size=4000,
                     narrative_prompt=NARRATIVE_PROMPT_TEMPLATE, 
                     list_prompt=LIST_PROMPT_TEMPLATE):
    """
    Generate a summary for the provided input file
    
    Args:
        input_file_path (str): Path to the input file
        provider (str): Provider to use (chatgpt or ollama)
        summary_type (str): Type of summary to generate (narrative or list)
        chatgpt_model (str): ChatGPT model to use
        ollama_model (str): Ollama model to use
        should_chunk (bool): Whether to chunk the text for Ollama
        max_chunk_size (int): Maximum size of each chunk for Ollama
        narrative_prompt (str): Template for narrative prompt
        list_prompt (str): Template for list prompt
        
    Returns:
        tuple: (summary text, output file path)
    """
    file_name = os.path.basename(input_file_path)
    print(f"Generating summary for: {file_name}")
    
    # Load the text content from the file
    text = load_input_file(input_file_path)
    if not text:
        print("Error: Could not extract text from the input file.")
        return "", ""
    
    print(f"Extracted text length: {len(text)} characters")
    
    # Determine summary type if not specified
    if not summary_type:
        summary_type = random.choice(["narrative", "list"])
        print(f"Summary type not specified, randomly selected: {summary_type}")
    
    # Generate summary based on provider and summary type
    if provider == "chatgpt":
        if load_environment_variables():
            if summary_type == "narrative":
                summary = request_narrative_from_chatgpt(text, narrative_prompt, chatgpt_model)
            else:  # list
                summary = request_list_from_chatgpt(text, list_prompt, chatgpt_model)
        else:
            print("Falling back to Ollama since OpenAI API key is not set.")
            if summary_type == "narrative":
                summary = request_narrative_from_ollama(text, narrative_prompt, ollama_model)
            else:  # list
                summary = request_list_from_ollama(text, list_prompt, ollama_model)
    else:  # ollama
        if should_chunk and len(text) > max_chunk_size:
            print(f"Text is too large ({len(text)} chars), chunking...")
            chunks = chunk_text(text, max_chunk_size)
            print(f"Split text into {len(chunks)} chunks")
            
            summaries = []
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}...")
                if summary_type == "narrative":
                    chunk_summary = request_narrative_from_ollama(chunk, narrative_prompt, ollama_model)
                else:  # list
                    chunk_summary = request_list_from_ollama(chunk, list_prompt, ollama_model)
                summaries.append(chunk_summary)
            
            # Join summaries
            summary = "\n\n".join(summaries)
        else:
            if summary_type == "narrative":
                summary = request_narrative_from_ollama(text, narrative_prompt, ollama_model)
            else:  # list
                summary = request_list_from_ollama(text, list_prompt, ollama_model)
    
    # Validate markdown formatting
    has_markdown = validate_markdown(summary)
    if not has_markdown:
        print("Warning: Generated summary does not contain markdown formatting.")
    else:
        print("✓ Generated summary contains markdown formatting.")
    
    # Prepare output path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_dir, "..", "PreparedInteractionLogs", "04-summarized")
    
    # Create the directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    
    # Create output file path
    base_name = os.path.splitext(file_name)[0]
    timestamp = datetime.now().strftime('%m-%d_%H-%M-%S')
    output_file_path = os.path.join(folder_path, f"{summary_type}-summary_{base_name}_{timestamp}.txt")
    
    # Write summary to output file
    with open(output_file_path, 'w') as file:
        file.write(summary)
    
    print(f"Summary saved to: {output_file_path}")
    
    return summary, output_file_path

def main():
    """Main function if you want to run the script directly"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate summaries from interaction logs")
    parser.add_argument("--input", "-i", help="Input file path (JSON or text)")
    parser.add_argument("--provider", "-p", choices=["chatgpt", "ollama"], default="chatgpt", 
                      help="Provider to use (chatgpt or ollama)")
    parser.add_argument("--summary-type", "-t", choices=["narrative", "list"], 
                      help="Type of summary to generate (narrative or list)")
    parser.add_argument("--chatgpt-model", default="gpt-3.5-turbo", 
                      help="ChatGPT model to use (default: gpt-3.5-turbo)")
    parser.add_argument("--ollama-model", default="llama3.2", 
                      help="Ollama model to use (default: llama3.2)")
    parser.add_argument("--chunk", "-c", action="store_true", 
                      help="Enable text chunking for Ollama")
    parser.add_argument("--max-chunk-size", type=int, default=4000, 
                      help="Maximum chunk size for Ollama (default: 4000)")
    parser.add_argument("--narrative-prompt", help="Path to a file containing a custom narrative prompt template")
    parser.add_argument("--list-prompt", help="Path to a file containing a custom list prompt template")
    
    args = parser.parse_args()
    
    # If no input file specified, use default
    # This is useful for testing the script directly
    if not args.input:
        input_file = "sentence_events_augmented_parsed_4_ac11c30b_interactions.json"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        input_path = os.path.join(current_dir, "..", "PreparedInteractionLogs", "03-sentences", input_file)
    else:
        input_path = args.input
    
    # Load custom prompt templates if provided
    narrative_prompt = NARRATIVE_PROMPT_TEMPLATE
    list_prompt = LIST_PROMPT_TEMPLATE
    
    if args.narrative_prompt:
        try:
            with open(args.narrative_prompt, 'r') as f:
                narrative_prompt = f.read()
                print(f"Custom narrative prompt loaded from {args.narrative_prompt}")
        except Exception as e:
            print(f"Error loading narrative prompt: {e}")
    
    if args.list_prompt:
        try:
            with open(args.list_prompt, 'r') as f:
                list_prompt = f.read()
                print(f"Custom list prompt loaded from {args.list_prompt}")
        except Exception as e:
            print(f"Error loading list prompt: {e}")
    
    # Generate summary
    summary, output_path = generate_summary(
        input_path,
        provider=args.provider,
        summary_type=args.summary_type,
        chatgpt_model=args.chatgpt_model,
        ollama_model=args.ollama_model,
        should_chunk=args.chunk,
        max_chunk_size=args.max_chunk_size,
        narrative_prompt=narrative_prompt,
        list_prompt=list_prompt
    )
    
    print(f"Summary generation complete. Results saved to: {output_path}")

if __name__ == "__main__":
    main()