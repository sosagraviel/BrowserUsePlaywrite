# AI Test Automation with browser-use & LangChain

## Overview
This project demonstrates browser automation and UI validation using the `browser-use` agent and Gemini (Google Generative AI) via LangChain. It is designed for UI automation testers to validate web tasks using LLMs.

## Requirements
- Python 3.9+
- macOS (tested on Apple Silicon)

## Setup

1. **Clone the repository** (if not already):
   ```sh
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers:**
   ```sh
   playwright install
   ```

## Environment Variables
Set your Gemini API key as an environment variable in your script or shell:
```python
os.environ["GEMINI_API_KEY"] = "<your-gemini-api-key>"
```
Or export it in your shell:
```sh
export GEMINI_API_KEY=<your-gemini-api-key>
```

## Usage
Run the main script:
```sh
python main.py
```

## File Structure
- `main.py` — Main entry point for running the browser-use agent with Gemini via LangChain.
- `requirements.txt` — All required Python dependencies with pinned versions.

## Troubleshooting
- If you see errors about missing Playwright browsers, run `playwright install` again.
- If you see LLM or API key errors, ensure your `GEMINI_API_KEY` is set and valid.
- For dependency issues, delete your `venv` and reinstall using the provided `requirements.txt`.

## References
- [browser-use documentation](https://docs.browser-use.com/)
- [LangChain documentation](https://python.langchain.com/)
- [Playwright Python](https://playwright.dev/python/) 