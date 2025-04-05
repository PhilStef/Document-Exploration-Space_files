import argparse
import os
import json

def process_file(input_file):
    """
    Complete file processing pipeline:
    1. Clean the file
    2. Augment with lookup data
    3. Convert to sentences
    
    Args:
        input_file (str): Path to the input JSON file
        
    Returns:
        dict: Results of each processing step
    """
    import importlib.util

    def dynamic_import(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    # Dynamically import the modules
    parse_json_file = dynamic_import("cleanInteractions", "./InteractionLogPrepScripts/01-cleanInteractions.py").parse_json_file
    augment_data = dynamic_import("augmenter", "./InteractionLogPrepScripts/02-augmenter.py").augment_data
    get_sentences = dynamic_import("ruleBasedSentenceGenerator", "./InteractionLogPrepScripts/03-ruleBasedSentenceGenerator.py").get_sentences
    generate_summaryA = dynamic_import("generateSummary", "./InteractionLogPrepScripts/04-GenerateSummary.py").requestNarrativeSummary
    generate_summaryB = dynamic_import("generateSummary", "./InteractionLogPrepScripts/04-GenerateSummary.py").requestListSummary

    results = {}
    
    print("=" * 50)
    print(f"Starting processing pipeline for: {input_file}")
    print("=" * 50)
    
    # Step 1: Clean the file
    print("\n--- Step 1: Cleaning data ---")
    cleaned_data, cleaned_file_path = parse_json_file(input_file)
    results["cleaned"] = cleaned_file_path
    print(f"Data cleaned successfully. Output saved to: {cleaned_file_path}")
    
    # Step 2: Augment with lookup data
    print("\n--- Step 2: Augmenting data ---")
    lookup_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "explorer", "data", "Maverick", "augmentedMavOutput.json")
    
    augmented_data, augmented_file_path = augment_data(cleaned_file_path, lookup_file_path)
    results["augmented"] = augmented_file_path
    print(f"Data augmented successfully. Output saved to: {augmented_file_path}")
    
    # Step 3: Convert to sentences
    print("\n--- Step 3: Converting to sentences ---")
    # Using the function directly instead of instantiating a class
    generated_results, sentences_file_path = get_sentences(augmented_file_path)
    results["sentences"] = sentences_file_path
    print(f"Sentences generated successfully. Output saved to: {sentences_file_path}")
    
    # Print a sample of the narrative
    if "session_narrative" in generated_results:
        narrative_preview = generated_results["session_narrative"].split('\n')[:5]
        print("\n**Narrative Preview:***")
        for line in narrative_preview:
            print(f"  {line}")
        print("  ...")
    
    print("\n" + "=" * 50)
    print("Processing pipeline completed successfully!")
    print("=" * 50)
    
    # Step 4: Generate narrative summary
    # print("\n--- Step 4: Generating narrative summary ---")
    # summary_results, summary_file_path = generate_summaryA(generated_results["session_narrative"])
    # results["summary"] = summary_results
    # print(f"Narrative summary generated successfully. Output saved to: {summary_file_path}")


    return results

def main():
    parser = argparse.ArgumentParser(description="Process JSON data through a pipeline of cleaning, augmentation, and sentence generation.")
    parser.add_argument("input_file", help="Path to the input JSON file to process")
    
    args = parser.parse_args()
    
    process_file(args.input_file)

if __name__ == "__main__":
    main()