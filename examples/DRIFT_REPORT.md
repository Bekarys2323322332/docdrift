# DocDrift Report: time_forecasting

**Docs trust score: 77%**  (33 of 43 checkable claims are correct)

| Claims checked | OK | DRIFT | UNVERIFIED |
|---|---|---|---|
| 43 | 33 | 10 (4 high, 4 medium, 2 low) | 0 |

Files audited: `README.md`

---

## Drift findings

Sorted by severity, HIGH first.

---

### D1 [HIGH] [COMMAND] `uvicorn` entry-point references a non-existent module

- **Docs say** (`README.md:55`): `"uvicorn src.api.server:app --reload"`
- **Code says** (`src/api/main.py:11`): `app = FastAPI(...)` is defined in `src/api/main.py`, not `server.py`. There is no `src/api/server.py` file in the repository.
- **Why it matters:** A developer following the Quick Start guide will get `ModuleNotFoundError: No module named 'src.api.server'` and will not be able to start the API.
- **Suggested fix:** `uvicorn src.api.main:app --reload`

---

### D2 [HIGH] [COMMAND] `streamlit run` references a non-existent file

- **Docs say** (`README.md:56`): `"streamlit run dashboard/main.py"`
- **Code says** (`dashboard/app.py`): The dashboard entry point is `dashboard/app.py`. There is no `dashboard/main.py` in the repository.
- **Why it matters:** A developer following the Quick Start guide will get `Error: [Errno 2] No such file or directory: 'dashboard/main.py'` and will not be able to start the dashboard.
- **Suggested fix:** `streamlit run dashboard/app.py`

---

### D3 [HIGH] [ENV] Wrong environment variable name for the database connection

- **Docs say** (`README.md:52`): `"set DB_CONNECTION_STRING in .env"`
- **Code says** (`src/config.py:17`): The `Settings` class defines `database_url: str`, which pydantic-settings maps to the env var `DATABASE_URL`. The `.env.example` file also uses `DATABASE_URL`.
- **Why it matters:** A user who sets `DB_CONNECTION_STRING` to point to PostgreSQL will see the app silently ignore it and fall back to its default SQLite/Postgres default URL.
- **Suggested fix:** Replace `DB_CONNECTION_STRING` with `DATABASE_URL` everywhere in the docs.

---

### D4 [HIGH] [API] `GET /models` endpoint does not exist; the real endpoint is `GET /tickers`

- **Docs say** (`README.md:81`): `"GET | /models | Which tickers have a trained model ready"`
- **Code says** (`src/api/routes.py:69`): `@router.get("/tickers", response_model=TickerListResponse)`. There is no `/models` route in `routes.py`.
- **Why it matters:** A developer who calls `GET /models` will receive a 404, and will not discover that `GET /tickers` is the correct endpoint.
- **Suggested fix:** Change the table row to: `GET | /tickers | Which tickers have a trained model ready`

---

### D5 [MEDIUM] [PATH] `src/api/endpoints.py` does not exist; the real file is `src/api/routes.py`

- **Docs say** (`README.md:104`): `"src/api/  endpoints.py    Endpoints"`
- **Code says** (`src/api/routes.py`): The file is named `routes.py`, confirmed by directory listing of `src\api\`.
- **Why it matters:** A developer navigating to `src/api/endpoints.py` to find or read endpoint code will not find it.
- **Suggested fix:** Change the project-structure listing to: `routes.py           Endpoints`

---

### D6 [MEDIUM] [PATH] `src/training/lstm_model.py` does not exist; the real file is `src/training/lstm_trainer.py`

- **Docs say** (`README.md:108`): `"src/training/  lstm_model.py     PyTorch LSTM"`
- **Code says** (`src/training/lstm_trainer.py`): The file is named `lstm_trainer.py`, confirmed by directory listing of `src\training\`.
- **Why it matters:** A developer looking for the LSTM implementation will not find `lstm_model.py`.
- **Suggested fix:** Change the project-structure listing to: `lstm_trainer.py      PyTorch LSTM`

---

### D7 [MEDIUM] [API] `POST /predict` endpoint does not exist; the real endpoint is `POST /forecast`

- **Docs say** (`README.md:85`): `"POST | /predict | Get predictions (lstm, prophet, arima, or ensemble)"`
- **Code says** (`src/api/routes.py:198`): `@router.post("/forecast", response_model=ForecastResponse)`. There is no `/predict` route.
- **Why it matters:** A developer who calls `POST /predict` will receive a 404.
- **Suggested fix:** Change the table row to: `POST | /forecast | Get predictions (lstm, prophet, arima, or ensemble)`

---

### D8 [MEDIUM] [API] `POST /health` should be `GET /health`

- **Docs say** (`README.md:80`): `"POST | /health | API status, database connectivity, trained tickers"`
- **Code says** (`src/api/routes.py:59`): `@router.get("/health", response_model=HealthResponse)`. The method is GET, not POST.
- **Why it matters:** A developer who sends `POST /health` will receive a 405 Method Not Allowed.
- **Suggested fix:** Change the table row to: `GET | /health | API status, database connectivity, trained tickers`

---

### D9 [LOW] [VERSION] Python version listed as 3.9 but Docker images use Python 3.12

- **Docs say** (`README.md:204`): `"Python 3.9, FastAPI, PyTorch, ..."`
- **Code says** (`Dockerfile.api:3`): `FROM python:3.12-slim`. (Also `Dockerfile.dashboard:8`: `FROM python:3.12-slim`.)
- **Why it matters:** A developer who creates a local venv with Python 3.9 may hit compatibility issues with the dependencies (e.g. `torch==2.13.0` requires Python ≥ 3.9 but was built/tested on 3.12).
- **Suggested fix:** Change `Python 3.9` to `Python 3.12` in the Stack section.

---

### D10 [LOW] [DEPENDENCY] Redis is listed in the stack but is not used anywhere in the project

- **Docs say** (`README.md:204`): `"..., Redis, Docker, pytest"`
- **Code says**: Redis does not appear in `requirements.txt`, in any file under `src/`, or in `docker-compose.yml`. Zero grep matches for `redis` across the entire codebase.
- **Why it matters:** A developer who believes Redis is needed may spend time installing or configuring it unnecessarily.
- **Suggested fix:** Remove `Redis` from the Stack list in the README.

---

## Undocumented settings

Environment variables and config keys the code reads but the docs never mention
(names only, never values):

| Name | Read at | Default in code |
|---|---|---|
| `API_PORT` | `src/config.py:20` | `8000` |
| `API_BASE_URL` | `dashboard/app.py:34` | `http://localhost:8000` |

---

## Unverified claims

None. All 43 claims produced a clear verdict.

---

## Verified claims (OK)

| ID | Category | Claim | Evidence |
|---|---|---|---|
| C1 | COMMAND | `docker compose up --build` | `docker-compose.yml` exists with `api`, `dashboard`, `db` services |
| C2 | COMMAND | `pip install -r requirements.txt` | `requirements.txt` exists at repo root |
| C3 | COMMAND | `copy .env.example .env` | `.env.example` exists at repo root |
| C6 | COMMAND | `pytest -m "not slow"` | `@pytest.mark.slow` found at `tests/test_api.py:167`, `tests/test_predictor.py:56`, `tests/test_training.py:65` (and many more) |
| C7 | PATH | `src/config.py` | Confirmed: `src\config.py` |
| C8 | PATH | `src/database.py` | Confirmed: `src\database.py` |
| C9 | PATH | `src/models.py` | Confirmed: `src\models.py` |
| C10 | PATH | `src/api/main.py` | Confirmed: `src\api\main.py` |
| C12 | PATH | `src/api/schemas.py` | Confirmed: `src\api\schemas.py` |
| C13 | PATH | `src/training/data_loader.py` | Confirmed: `src\training\data_loader.py` |
| C15 | PATH | `src/training/prophet_trainer.py` | Confirmed: `src\training\prophet_trainer.py` |
| C16 | PATH | `src/training/arima_trainer.py` | Confirmed: `src\training\arima_trainer.py` |
| C17 | PATH | `src/training/evaluation.py` | Confirmed: `src\training\evaluation.py` |
| C18 | PATH | `src/training/pipeline.py` | Confirmed: `src\training\pipeline.py` |
| C19 | PATH | `src/inference/predictor.py` | Confirmed: `src\inference\predictor.py` |
| C20 | PATH | `dashboard/app.py` | Confirmed: `dashboard\app.py` |
| C21 | PATH | `tests/` folder | Confirmed: `tests\` directory exists |
| C22 | PATH | `exploration.ipynb` | Confirmed: `exploration.ipynb` at repo root |
| C23 | ENV | `.env.example` exists | Confirmed: `.env.example` at repo root |
| C27 | API | `GET /historical?ticker=AAPL&days=365` | `src/api/routes.py:227` |
| C28 | API | `POST /retrain` | `src/api/routes.py:138` |
| C29 | API | `GET /retrain-status/{job_id}` | `src/api/routes.py:177` |
| C31 | API | `GET /model-comparison?ticker=AAPL` | `src/api/routes.py:280` |
| C32 | API | `POST /retrain` returns `job_id` | `src/api/schemas.py` `RetrainResponse` schema includes `job_id` field |
| C34 | DEPENDENCY | FastAPI | `requirements.txt:22` (`fastapi==0.141.1`) |
| C35 | DEPENDENCY | PyTorch | `requirements.txt:15` (`torch==2.13.0`) |
| C36 | DEPENDENCY | Prophet | `requirements.txt:16` (`prophet==1.4.0`) |
| C37 | DEPENDENCY | statsmodels | `requirements.txt:17` (`statsmodels==0.14.6`) |
| C38 | DEPENDENCY | SQLAlchemy | `requirements.txt:28` (`sqlalchemy==2.0.52`) |
| C39 | DEPENDENCY | PostgreSQL | `requirements.txt:29` (`psycopg2-binary`); `docker-compose.yml:13` (`db` service) |
| C40 | DEPENDENCY | Streamlit | `requirements.txt:32` (`streamlit==1.60.0`) |
| C42 | DEPENDENCY | pytest | `requirements.txt:37` (`pytest==9.1.1`) |
| C43 | COUNT | "68 tests" | 68 test functions confirmed: 14 in `test_api.py`, 18 in `test_predictor.py` (including parametrize expansions), 16 in `test_training.py`, 20 in `test_data_loader.py` |
