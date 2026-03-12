# AI Interview Platform

A web application that allows users to register, log in, and conduct mock interviews using browser-based Speech-to-Text conversion and Python/NLP backend analysis.

## Features
- User Auth (Register, Login, Dashboard)
- Interactive Speech-to-text recording UI (Premium Glassmorphism Dark Mode)
- Real time Backend NLP analysis (keyword matching, sentence length checking, confidence text fillers evaluating).

## Prerequisites
- Python 3.10+
- Modern Web Browser that supports Web Speech API (e.g., Google Chrome or Edge). **Note: Firefox and Safari do not currently fully support Web Speech API**.

## How to Deploy & Run Locally

1. **Activate your Python environment** (Optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```

2. **Install Dependencies**:
   Open a terminal in the directory where `requirements.txt` is located and run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   Run the `app.py` server. This will automatically set up the SQLite DB (`database.db`) inside the folder to prevent initial problems.
   ```bash
   python app.py
   ```

4. **Access the Website**:
   Open your browser and navigate to:
   ```text
   http://localhost:5000
   ```

### Important deployment notes for Production:
- This uses Flask's built in development server. For actual production, use `waitress` or `gunicorn`!
Example using waitress to run on all networks on port `8080`:
```bash
waitress-serve --port=8080 app:app
```
- Since the application relies on the browser's `webkitSpeechRecognition`, your domain must have **HTTPS** enabled (or run locally on `localhost`). Browsers block microphone access on insecure network domains.
