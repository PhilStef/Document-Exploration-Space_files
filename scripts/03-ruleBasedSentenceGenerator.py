import json
import os

def generate_sentence_for_event(event):
    """
    Generate a sentence sentence for an event based on its type
    
    Args:
        event (dict): Event data
        
    Returns:
        str: Summary sentence
    """
    event_type = event.get("type", "unknown")
    print (event_type, event)
    if event_type == "drag-start":
        status = event.get("msg", "unknown")
        if status == "open":
            return f"Started dragging a document (ID#: {event.get('doc_id', 'unknown')}) about {event.get('essential_information', 'unknown')} to {event.get('pos',[0,0])}."
        else:
            return f"Started dragging document (ID#: {event.get('doc_id', 'unknown')}) to {event.get('pos',[0,0])}."

    elif event_type == "drag-end":
        status = event.get("msg", "unknown")
        if status == "open":
            return f"Finished dragging a document (ID#: {event.get('doc_id', 'unknown')}) about {event.get('essential_information', 'unknown')} to {event.get('pos',[0,0])}."
        else:
            return f"Finished dragging document (ID#: {event.get('doc_id', 'unknown')}) to {event.get('pos',[0,0])}."

    elif event_type == "mouseleave-doc":
        status = event.get("msg", "unknown")
        if status == "open":
            return f"The mouse left an open document about {event.get('essential_information', 'unknown')}"
        else:
            return f"The mouse left a closed document about {event.get('essential_information', 'unknown')}"

    elif event_type == "mouseenter-doc":
        status = event.get("msg", "unknown")
        if status == "open":
            return f"The mouse hovered on an open document (ID#: {event.get('doc_id', 'unknown')}) about {event.get('essential_information', 'unknown')}"
        else:
            return f"The mouse hovered on a closed document (ID#: {event.get('doc_id', 'unknown')}) about {event.get('essential_information', 'unknown')}"

    elif event_type == "open-doc":
        return f"Opened document (ID#: {event.get('doc_id', 'unknown')}) about {event.get('topics', 'unknown')}. It contains the following entities: {event.get('entities', 'unknown')}, and describes {event.get('essential_information', 'unknown')}"

    elif event_type == "close-doc":
        return f"Closed document (ID#: {event.get('doc_id', 'unknown')}) about {event.get('essential_information', 'unknown')}"

    elif event_type == "search":
        query = event.get("msg", "unknown terms")
        doc_ids = event.get("doc_id", [])
        if isinstance(doc_ids, list):
            num_results = len(doc_ids)
            return f"Searched for '{query}' and found {num_results} results."
        else:
            return f"Searched for '{query}' but no documents were returned."

    elif event_type == "highlight":
        text = event.get("msg", "")
        return f"Highlighted '{text}' in a document about {event.get('essential_information', 'unknown')}"

    elif event_type == "note":
        text = event.get("msg", "")
        return f"Created note: '{text}'."

    elif event_type == "end-notes":
        texts = event.get("msg")
        messages =""
        if isinstance(texts, list):
            num_results = len(texts)
            messages = "\n\n".join(texts)
            if(num_results == 1):
                return f"the user wrote down {num_results} note during the investigation and it contains the following message: ```{messages}```."
            else:
                return f"the user wrote down {num_results} note(s) during the investigation and they contain the following messages: ```{messages}```."
        else:
            return f"The user did not write anything into their notebook."

    # Add any additional event types you need to handle

    else:
        # Generic fallback
        return f"Performed {event_type} action with the following information {event}."

def convert_seconds_to_human_time(seconds):
    """
    Convert seconds (with decimal milliseconds) to a human-readable format (minutes and seconds).
    
    Args:
        seconds (float): Time in seconds (can include milliseconds as decimal).
        
    Returns:
        str: Time in "X minutes, Y seconds" format.
    """
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes} minutes, {round(remaining_seconds)} seconds"

def add_sentences_to_events(events):
    """
    Add sentence field to each event
    
    Args:
        events (list): List of event dictionaries
        
    Returns:
        list: Events with summaries added
    """
    events_with_summaries = []
    
    for event in events:
        # Create a copy of the event to avoid modifying the original
        new_event = event.copy()
        
        # Add the sentence
        new_event["sentence"] = generate_sentence_for_event(event)

        print(new_event)
        
        events_with_summaries.append(new_event)
        
    return events_with_summaries

def calculate_session_metrics(events):
    """
    Calculate useful metrics about the session
    
    Args:
        events (list): List of event dictionaries
        
    Returns:
        dict: Session metrics
    """
    metrics = {
        "total_events": len(events),
        "event_types": {},
        "documents_visited": set(),
        "searches_performed": 0,
        "session_duration": 0
    }
    
    for event in events:
        # Count event types
        event_type = event.get("type", "unknown")
        if event_type in metrics["event_types"]:
            metrics["event_types"][event_type] += 1
        else:
            metrics["event_types"][event_type] = 1
        
        # Track visited documents
        if "doc_id" in event and isinstance(event["doc_id"], str):
            metrics["documents_visited"].add(event["doc_id"])
        
        # Count searches
        if event_type == "search":
            metrics["searches_performed"] += 1
    
    # Calculate session duration
    if len(events) > 1:
        start_time = events[0].get("timestamp", 0)
        end_time = events[-1].get("timestamp", 0)
        metrics["session_duration"] = end_time - start_time
    
    # Convert set to list for JSON serialization
    metrics["documents_visited"] = list(metrics["documents_visited"])
    metrics["unique_documents"] = len(metrics["documents_visited"])
    
    return metrics

def generate_session_narrative(events):
    """
    Generate a narrative summary of the session
    
    Args:
        events (list): List of event dictionaries
        
    Returns:
        str: Session narrative
    """
    # Calculate metrics for the narrative
    metrics = calculate_session_metrics(events)
    
    # Generate a session summary
    narrative = [
        f"Session Metrics: This session contained {metrics['total_events']} events spanning {convert_seconds_to_human_time(metrics['session_duration'])}.",
        f"The user interacted with {metrics['unique_documents']} unique documents and performed {metrics['searches_performed']} searches."
    ]
    
    # Add information about the most common activities
    if metrics["event_types"]:
        most_common_event = max(metrics["event_types"].items(), key=lambda x: x[1])
        narrative.append(f"The most common activity was '{most_common_event[0]}' which occurred {most_common_event[1]} times.")
    
    # Generate a chronological narrative of key events
    narrative.append("\nKey Activities (chronological order):")
    
    # Filter to key events to avoid overwhelming narrative
    key_event_types = {"search", "open-doc", "highlight", "note"}
    filtered_events = [e for e in events if e.get("type") in key_event_types]
    
    # Take a sample of events if there are too many
    max_events_to_show = 50
    if len(filtered_events) > max_events_to_show:
        step = len(filtered_events) // max_events_to_show
        sampled_events = filtered_events[::step][:max_events_to_show]
    else:
        sampled_events = filtered_events
    
    # Add sentence of each key event to the narrative
    for event in sampled_events:
        sentence = generate_sentence_for_event(event)
        timestamp = convert_seconds_to_human_time(event.get("timestamp", 0))
        narrative.append(f"- At {timestamp}: {sentence}")
    
    # Ensure the final "end-note" event is included if it exists
    end_note_event = next((e for e in events if e.get("type") == "end-notes"), None)
    if end_note_event:
        sentence = generate_sentence_for_event(end_note_event)
        timestamp = convert_seconds_to_human_time(end_note_event.get("timestamp", 0))
        narrative.append(f"\nAt {timestamp}: the investigation ended and {sentence}")
    
    return "\n".join(narrative)

def get_sentences(input_file_path, output_file_path=None):
    """
    Convert JSON events to sentences and summaries
    
    Args:
        input_file_path (str): Path to the JSON file to convert
        output_file_path (str, optional): Path to save the output sentences
        
    Returns:
        dict: Generated summaries and metrics
        str: Path to the output file
    """
    file_name = os.path.basename(input_file_path)
    print(f"Converting file to sentences: {file_name}")
    
    # Load the data
    try:
        with open(input_file_path, 'r') as file:
            data = json.load(file)
            print(f"Input file opened successfully with {len(data)} events.")
    except IOError as e:
        print(f"Error opening input file: {e}")
        return {}, ""
    
    # Add summaries to each event
    events_with_summaries = add_sentences_to_events(data)
    print(events_with_summaries)
    
    # Generate a session narrative
    session_narrative = generate_session_narrative(events_with_summaries)
    
    # Calculate session metrics
    metrics = calculate_session_metrics(events_with_summaries)
    
    # Combine individual event summaries into a single text
    individual_summaries = [event["sentence"] for event in events_with_summaries]
    all_summaries = " ".join(individual_summaries)
    
    # Prepare the output
    results = {
        "session_narrative": session_narrative,
        "all_sentences": all_summaries,
        "metrics": metrics,
        "events_with_sentences": events_with_summaries,
    }
    
    # Create output path if not specified
    if not output_file_path:
        current_dir = os.getcwd()
        folder_path = os.path.join(current_dir, "outputLogs", "03-sentences")
        os.makedirs(folder_path, exist_ok=True)
        
        # Generate a base filename
        base_name = file_name.replace(".json", "")
        
        # Create output files for different outputs
        json_output_path = os.path.join(folder_path, f'sentences_{base_name}.json')
        text_output_path = os.path.join(folder_path, f'narrative_{base_name}.txt')
    else:
        # Use the specified output path for JSON
        json_output_path = output_file_path
        text_output_path = output_file_path.replace(".json", ".txt")
    
    # Write the summary JSON to file
    with open(json_output_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    
    # Write the narrative text to file
    with open(text_output_path, 'w') as text_file:
        text_file.write(session_narrative)
    
    print(f"Summaries saved to: {json_output_path}")
    print(f"Narrative saved to: {text_output_path}")
    
    return results, json_output_path\

def main():
    """Main function if you want to run the script directly"""
    logToParse = 'augmented_parsed_4_ac11c30b_interactions.json.json'
    print(os.getcwd())
    main_file_path = os.path.join("outputLogs", "02-augmented", logToParse) 
    results, output_path = get_sentences(main_file_path)
    print(f"Results saved to: {output_path}")

if __name__ == "__main__":
    main()
