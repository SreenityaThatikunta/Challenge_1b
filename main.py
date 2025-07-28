import os
import json
import logging
from typing import List, Dict
from PyPDF2 import PdfReader
import subprocess
from datetime import datetime

# --- CONFIG ---
COLLECTIONS = [
    "Collection 1",
    "Collection 2",
    "Collection 3"
]
INPUT_FILENAME = "challenge1b_input.json"
OUTPUT_FILENAME = "challenge1b_output.json"
PDFS_DIR = "PDFs"
DOCKER_IMAGE = "ai/qwen3:0.6B-Q4_0"

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- PDF Utility ---
def extract_text_from_pdf(pdf_path: str) -> List[str]:
    reader = PdfReader(pdf_path)
    return [page.extract_text() or "" for page in reader.pages]

# --- LLM Utility ---
def call_llm(page_text: str, persona: str, task: str) -> Dict:
    prompt = f"""
You are an expert assistant. Given the following persona and task, analyze the PDF page content.

Persona: {persona}
Task: {task}

PDF Page Content:
{page_text}

Return strictly valid JSON with two fields:
1. "sections": list of dicts (with "section_title", "importance_rank", "page_number")
2. "subsections": list of dicts (with "refined_text", "page_number")

ONLY JSON, no explanations or markdown.
""".strip()

    full_command = [
        "docker", "run", "--rm", "-i",
        "--network", "none",
        DOCKER_IMAGE,
        "--prompt", prompt
    ]

    try:
        result = subprocess.run(
            full_command,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )
        print("result", result)
        print("\n\n\n\n\n")
        output = result.stdout.strip()
        json_start = output.find('{')
        json_end = output.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            return json.loads(output[json_start:json_end])
        else:
            logging.warning(f"Invalid JSON received from model. Raw output:\n{output}")
            return {"sections": [], "subsections": []}
    except Exception as e:
        logging.error(f"LLM call failed: {e}")
        return {"sections": [], "subsections": []}

# --- Main Processor ---
def process_collection(collection_path: str):
    input_path = os.path.join(collection_path, INPUT_FILENAME)
    output_path = os.path.join(collection_path, OUTPUT_FILENAME)
    pdfs_path = os.path.join(collection_path, PDFS_DIR)

    with open(input_path, "r") as f:
        input_data = json.load(f)

    persona = input_data["persona"]["role"]
    task = input_data["job_to_be_done"]["task"]
    documents = input_data["documents"]
    input_filenames = [doc["filename"] for doc in documents]

    metadata = {
        "input_documents": input_filenames,
        "persona": persona,
        "job_to_be_done": task,
        "processing_timestamp": datetime.utcnow().isoformat() + "Z"
    }

    extracted_sections = []
    subsection_analysis = []

    for doc in documents:
        pdf_path = os.path.join(pdfs_path, doc["filename"])
        logging.info(f"Processing document: {pdf_path}")

        try:
            pages = extract_text_from_pdf(pdf_path)
        except Exception as e:
            logging.error(f"Failed to read {pdf_path}: {e}")
            continue

        for i, text in enumerate(pages):
            if not text.strip():
                continue
            result = call_llm(text, persona, task)

            for sec in result.get("sections", []):
                extracted_sections.append({
                    "document": doc["filename"],
                    "section_title": sec.get("section_title", ""),
                    "importance_rank": sec.get("importance_rank", 0),
                    "page_number": sec.get("page_number", i + 1)
                })

            for sub in result.get("subsections", []):
                subsection_analysis.append({
                    "document": doc["filename"],
                    "refined_text": sub.get("refined_text", ""),
                    "page_number": sub.get("page_number", i + 1)
                })

    output_data = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
    logging.info(f"Saved output to: {output_path}")

# --- Runner ---
if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    for collection in COLLECTIONS:
        path = os.path.join(base_dir, collection)
        if os.path.isdir(path):
            logging.info(f"Processing Collection: {collection}")
            process_collection(path)
        else:
            logging.warning(f"Collection not found: {path}")
