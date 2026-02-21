# LearnSphere

> Adaptive AI-powered learning app built with Streamlit and Groq.

## Overview

LearnSphere is a simple Streamlit application that generates learning content and quizzes using the Groq API and stores user accounts and performance in a SQLite database.

## Files

- `app.py` - Main Streamlit application.
- `database.py` - SQLite connection and table creation helpers.
- `learnsphere.db` - SQLite database file (created automatically at runtime).

## Prerequisites

- Python 3.10+ (3.11 recommended)
- pip

## Quick setup

1. (Optional) Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install streamlit python-dotenv groq
```

3. Add your Groq API key in a `.env` file at the project root:

```
GROQ_API_KEY=your_api_key_here
```

4. Run the app:

```powershell
streamlit run app.py
```

The app will create `learnsphere.db` automatically and ensure required tables exist.

## Usage

- Use the `Register` menu to create an account, then `Login` to access the content generator and dashboard.
- Enter a topic, level and language to generate learning content and a quiz.

## Known issues & recommended improvements

- Plaintext passwords: User passwords are stored unhashed in `users.password`. Replace with a secure hashing method (e.g., `bcrypt`) for production.
- DB connection inconsistency: `app.py` uses `sqlite3.connect(..., check_same_thread=False)` while `database.py` does not. Consolidate DB connection logic in `database.py`.
- Hardcoded `total_questions`: The app inserts `total_questions = 5` even when quiz length varies. Make it dynamic using the actual quiz length.
- Fragile JSON parsing: The quiz JSON is extracted by slicing from the first `[` to the last `]`. This can fail when the model returns extra text. Improve parsing and validation.
- Env validation: The app creates the Groq client without validating `GROQ_API_KEY`—add explicit checks and clear error messages.
- No migrations/versioning: For future schema changes, add a lightweight migration strategy.

## Next steps (suggested)

- Hash passwords and update login/registration flows.
- Move DB helper functions into `database.py` and use them consistently.
- Make `total_questions` dynamic and validate quiz JSON robustly.
- Add a `requirements.txt` and CI checks for linting/tests.

---

If you want, I can implement one or more of the recommended improvements now (password hashing, DB consolidation, or JSON parsing hardening). Which would you like first?
                                         --- Thanking You ---
