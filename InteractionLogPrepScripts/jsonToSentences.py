import json
import os
import openai
import tiktoken
import math
import collections
from datasets import load_dataset
import evaluate

class SentenceGenerator:
    def __init__(self, api_key=None):
        """Initialize the SentenceGenerator with OpenAI API key"""
        self.openai_api_key = api_key
        if api_key:
            openai.api_key = api_key
        self.max_token = 3072

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0301"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        if model == "gpt-3.5-turbo-0301":
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"num_tokens_from_messages() not implemented for {model}.")

    def get_sentences(self, input_file_path, output_file_path=None):
        """
        Convert JSON data to sentences
        
        Args:
            input_file_path (str): Path to the JSON file to convert
            output_file_path (str, optional): Path to save the output sentences
            
        Returns:
            str: Generated sentences
            str: Path to the output file
        """
        file_name = os.path.basename(input_file_path)
        print(f"Converting file to sentences: {file_name}")
        
        # Load the data
        try:
            with open(input_file_path, 'r') as file:
                data = json.load(file)
                print("Input file opened successfully.")
        except IOError as e:
            print(f"Error opening input file: {e}")
            return "", ""

        # Process data to create a meaningful text summary
        sentences = []
        
        # Extract event sequences
        for event in data:
            event_type = event.get("type", "unknown")
            doc_id = event.get("doc_id", "unknown")
            
            # Create a basic description of the event
            if event_type == "mouseenter-doc":
                sentence = f"User opened document {doc_id}."
            elif event_type == "mouseleave-doc":
                sentence = f"User closed document {doc_id}."
            elif event_type == "drag-start":
                sentence = f"User started dragging in document {doc_id}."
            elif event_type == "drag-end":
                sentence = f"User finished dragging in document {doc_id}."
            else:
                sentence = f"User performed {event_type} on document {doc_id}."
            
            # Add additional context if available
            if "content" in event:
                sentence += f" Document content: {event['content'][:100]}..."
            
            if "topic" in event:
                sentence += f" Document topic: {event['topic']}."
                
            sentences.append(sentence)
        
        # Join all sentences into a coherent text
        full_text = " ".join(sentences)
        
        # Use OpenAI to summarize if API key is available and text is lengthy
        if self.openai_api_key and len(full_text) > 200:
            messages = [
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
                {"role": "user", "content": full_text}
            ]
            
            tokens = self.num_tokens_from_messages(messages)
            
            if tokens > self.max_token:
                # Split into chunks if too large
                chunks = []
                sentences_per_chunk = max(1, len(sentences) // (tokens // self.max_token + 1))
                for i in range(0, len(sentences), sentences_per_chunk):
                    chunks.append(" ".join(sentences[i:i+sentences_per_chunk]))
                
                summaries = []
                for chunk in chunks:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
                            {"role": "user", "content": chunk}
                        ]
                    )
                    summaries.append(response.choices[0].message.content)
                
                full_text = " ".join(summaries)
            else:
                # Summarize the whole text at once
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                full_text = response.choices[0].message.content
        
        # Save to output file if specified
        if not output_file_path:
            current_dir = os.getcwd()
            folder_path = os.path.join(current_dir, "Parsing Tests", "Specific Tests")
            os.makedirs(folder_path, exist_ok=True)
            output_file_path = os.path.join(folder_path, f'sentences_{file_name.replace(".json", ".txt")}')
        
        with open(output_file_path, 'w') as file:
            file.write(full_text)
        
        return full_text, output_file_path