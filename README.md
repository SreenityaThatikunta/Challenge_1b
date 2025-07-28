# Challenge 1b: Multi-Collection PDF Analysis Pipeline

## Overview

This project implements an advanced PDF analysis pipeline that processes multiple document collections and extracts relevant content based on specific personas and use cases. It leverages the Qwen 3 LLM (via Docker) to analyze PDF content and produce structured JSON outputs for downstream applications.

## Features

- Persona-based content analysis
- Importance ranking of extracted sections
- Multi-collection document processing
- Structured JSON output with metadata
- Modular, extensible Python code

## Project Structure

```
Challenge_1b/
├── Collection 1/                    # Travel Planning
│   ├── PDFs/                       # South of France guides
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── Collection 2/                    # Adobe Acrobat Learning
│   ├── PDFs/                       # Acrobat tutorials
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── Collection 3/                    # Recipe Collection
│   ├── PDFs/                       # Cooking guides
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── main.py                         # Pipeline code
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Containerization
└── README.md                       # Project documentation
```

## Input/Output Format

### Input JSON Structure

```
{
  "challenge_info": { ... },
  "documents": [{"filename": "doc.pdf", "title": "Title"}],
  "persona": {"role": "User Persona"},
  "job_to_be_done": {"task": "Use case description"}
}
```

### Output JSON Structure

```
{
  "metadata": { ... },
  "extracted_sections": [ ... ],
  "subsection_analysis": [ ... ]
}
```

## How It Works

1. For each collection, the pipeline reads the input JSON and extracts text from each PDF.
2. Each page of each PDF is sent to the Qwen 3 LLM (via Docker) with persona and task context.
3. The LLM returns structured JSON with relevant sections and refined text.
4. Results are aggregated and saved to the output JSON in the required schema.

## Usage

### Prerequisites

- Python 3.11+
- Docker (with access to the Qwen 3 model image: `ai/qwen3:0.6B-Q4_0`)

### Install Python dependencies

```
pip install -r requirements.txt
```

### Run the pipeline (locally)

```
python main.py
```

### Run with Docker

Build the container:

```
docker build -t challenge1b-pipeline .
```

Run the pipeline (mount Docker socket for LLM subprocess):

```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock challenge1b-pipeline
```

## Troubleshooting

- If you see Docker image errors (e.g., `mismatched image rootfs and manifest layers`), remove and re-pull the Qwen image:
  ```
  docker rmi ai/qwen3:0.6B-Q4_0
  docker pull ai/qwen3:0.6B-Q4_0
  ```
- Ensure your Docker and Python versions are compatible with your OS/architecture.
- If the LLM output is empty, check that your PDFs contain extractable text and the model is running correctly.

## Customization

- To use a different LLM or API, modify the `call_llm` function in `main.py`.
- To add more collections, simply add new folders with the required structure and input files.
