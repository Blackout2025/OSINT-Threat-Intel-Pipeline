# OSINT Threat Intelligence & Automation Ingestion Pipeline

## 🎯 Architectural Overview
An automated offensive and defensive reconnaissance pipeline designed to ingest, parse, and normalize raw open-source threat intelligence (OSINT) data streams. This system processes indicators of compromise (IoCs) including malicious IP addresses, domain names, and file hashes to generate structured threat data feeds for security operation centers (SOC).



## Core Features
* **Automated Data Normalization:** Converts unformatted threat data into clean, structured JSON payloads.
* **Malignant Indicator Scoring:** Evaluates threat severity using customizable context and risk weighting vectors.
* **Compliance Reporting Layer:** Generates an automated HTML analytics dashboard tracking compromised actors globally.

## Installation & Execution
```bash
# Clone the repository
git clone [https://github.com/Blackout656/OSINT-Threat-Intel-Pipeline.git](https://github.com/Blackout656/OSINT-Threat-Intel-Pipeline.git)
cd OSINT-Threat-Intel-Pipeline

# Execute the pipeline
python3 intel_pipeline.py
