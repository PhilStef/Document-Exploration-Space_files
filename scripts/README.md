# scripts

This folder contains Python scripts designed to process and clean interaction logs from the Document explorer tool. These scripts are part of the preprocessing pipeline for preparing interaction data for passing to a LLM to summarize analysis steps.

## Scripts Overview

### 1. `00-postStudyProcessor.py`

This script calls on the other scripts to processes raw interaction logs collected after a study.

#### Usage

1. Ensure you have Python installed on your system.
2. Install the required packages

```sh 

pip install -r /path/to/requirements.txt
```

This script is designed to be run from the **root** of this project directory.

```sh

python3 scripts/00-postStudyProcessor.py inputLogs/ *<replace with raw log file>*.json
```

The output files are being placed in the `/outputLogs/` folder.

### Additional Scripts

- `01-cleanInteractions.py` - This script cleans the processed interaction logs by removing unnecessary data, handling missing values, and standardizing the format for downstream analysis.
- `02-augmenter.py` - This script augments the remaining interacitons from the cleaner and pulls in information from the augmented dataset. This augmented dataset includes summaries, entities and topics mentioned in each document. The idea is that these concepts will be shorter than sending the whole document's original text to a LLM, so we will save tokens by doing this. It
- `03-ruleBasedSentenceGenerator` - This script converts augmented data into a sentence to make it easy to communicate what happens in each event.
- `04-GenerateSummary` - This script works with either ollama (locally) or chatGPT (with an API token) to take the sentences and pair them with a prompt. Can be run independently with specified options (use the `-h` flag to learn more).

Other scripts in this folder may include specialized utilities for parsing, filtering, or transforming interaction logs. Each script is designed to handle a specific aspect of the preprocessing workflow.

## Notes

- Review each script's comments and documentation for detailed usage instructions.
- Ensure proper backups of raw data before running the scripts to avoid accidental data loss.
