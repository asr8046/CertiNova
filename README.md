# CertiNova

CertiNova is a Streamlit-based web app for verifying and extracting skills from resumes and certifications. It supports PDF uploads and certificate URL validation (Coursera, NPTEL, etc.), and uses NLP (spaCy) for smart skill extraction.

---

## Features
- Upload resume (PDF) and extract skills using NLP
- Upload certificate PDFs and/or provide certificate URLs
- Compare and verify skills between resume and certifications
- Modern, interactive Streamlit UI

---

## Setup Instructions

### 1. Clone the repository or download the code

### 2. Create and activate a virtual environment (Windows example)
```sh
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install all dependencies
```sh
pip install -r requirements.txt
```

### 4. Download the spaCy English model (required for skill extraction)
```sh
python -m spacy download en_core_web_sm
```

---

## Running the App

From the project root directory, run:
```sh
streamlit run skillcert-verifier/main.py
```

- The app will open in your browser (usually at http://localhost:8501/)
- Upload your resume and certifications, or paste certificate URLs, to see skill extraction and verification in action.

---

## Project Structure
```
CertiNova/
├── .venv/                  # Virtual environment (not included in repo)
├── requirements.txt        # All Python dependencies
├── README.md               # This file
└── skillcert-verifier/
    ├── main.py             # Streamlit app entry point
    └── utils/
        ├── pdf_parser.py   # PDF text extraction
        ├── url_handler.py  # Certificate URL scraping
        ├── skill_extractor.py # Skill matching logic
        └── __init__.py
```

---

## Notes
- Make sure to activate your virtual environment each time before running the app.
- If you add new dependencies, update `requirements.txt` and reinstall them with `pip install -r requirements.txt`.
- For best results, use clear, text-based PDF resumes and certificates.

---

## Troubleshooting
- **spaCy errors?** Make sure you've installed both `spacy` and run the model download command above.
- **No skills extracted?** Try uploading a different PDF, or expand the skill extraction logic in `main.py` or `utils/skill_extractor.py`.
- **ModuleNotFoundError?** Double-check that your virtual environment is activated and all requirements are installed.

---

## License
This project is for educational and demonstration purposes.