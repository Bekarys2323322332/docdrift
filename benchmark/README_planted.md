# Time Series Forecasting: LSTM vs Prophet vs ARIMA

Trains and compares three forecasting models on any stock ticker, serves predictions through a
REST API, and presents everything in an interactive dashboard.

Pick a ticker and a date range, train all three models on it, then compare how they actually
performed on data none of them saw during training.

---

## What it does

- **Fetches live data** from Yahoo Finance for any ticker, over any date range up to 5 years
- **Trains three models** on the same data: a PyTorch LSTM, Facebook Prophet, and ARIMA
- **Backtests them** against a held-out test period and records the results
- **Serves forecasts** through a FastAPI REST API, including an ensemble that averages all three
- **Versions every training run**, so retraining on 2 years vs 5 years of data produces two
  separately comparable models rather than one overwriting the other

---

## Quick start

### Option A: Docker (recommended)

Runs the API, dashboard, and a PostgreSQL database together, with no local Python setup at all.

```bash
docker compose up --build
```

Then open:
- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs

The first build takes several minutes - PyTorch and Prophet are large. Later starts are fast.

### Option B: Running locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt

copy .env.example .env       # Windows
# cp .env.example .env       # macOS / Linux
```

The default `.env` uses SQLite, so no database server is needed. To use PostgreSQL instead, set
`DB_CONNECTION_STRING` in `.env`. Then, in two terminals:

```bash
uvicorn src.api.server:app --reload    # terminal 1
streamlit run dashboard/main.py         # terminal 2
```

---

## Using it

1. Open the dashboard and enter a ticker (e.g. `AAPL`)
2. Click **Train** in the sidebar - this trains all three models and takes a minute or two
3. Once training finishes, the **Forecasts** and **Comparison** tabs become available

The Forecasts tab plots the prediction against what actually happened. This works because
forecasts begin at the model's training cutoff rather than today, so real prices usually already
exist for part of the forecast window - making it a real accuracy check, not just a projection.

Nothing is pre-trained: a ticker must be trained before it can be forecast. `GET /tickers` lists
which ones are ready.

---

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/health` | API status, database connectivity, trained tickers |
| GET | `/models` | Which tickers have a trained model ready |
| GET | `/historical?ticker=AAPL&days=365` | Real price history |
| POST | `/retrain` | Start training a ticker (returns immediately with a job id) |
| GET | `/retrain-status/{job_id}` | Check on a training job |
| POST | `/predict` | Get predictions (`lstm`, `prophet`, `arima`, or `ensemble`) |
| GET | `/model-comparison?ticker=AAPL` | Each model's accuracy from its last training run |

Interactive docs at http://localhost:8000/docs once the API is running.

**Training is asynchronous.** `POST /retrain` returns a `job_id` right away rather than blocking
for the minutes training takes; poll `/retrain-status/{job_id}` until it reports `completed` or
`failed`.

---

## Project structure

```
src/
  config.py              All settings and limits in one place
  database.py            SQLAlchemy engine and session setup
  models.py              Database tables (training jobs, metrics, cached prices)
  api/
    main.py              FastAPI app and startup
    endpoints.py         Endpoints
    schemas.py           Request/response validation
  training/
    data_loader.py       Fetch from yfinance, clean, split
    lstm_model.py        PyTorch LSTM
    prophet_trainer.py   Facebook Prophet
    arima_trainer.py     ARIMA
    evaluation.py        Shared metrics, so all models are scored identically
    pipeline.py          Runs all three as one atomic training job
  inference/
    predictor.py         Loads trained models and produces forecasts
dashboard/app.py         Streamlit UI
tests/                   68 tests
exploration.ipynb        Data exploration and model comparison, with charts
```

---

## Tests

```bash
pytest                    # everything (~30 seconds)
pytest -m "not slow"      # skip the model-training tests (~7 seconds)
```

Tests mock the Yahoo Finance API, so they never hit the network - fast, and they don't break
tomorrow when prices change.

---

## Understanding the metrics

The Comparison tab and `/model-comparison` report four numbers per model, measured on the held-out
test period - data none of the models saw during training.

| Metric | Units | Meaning |
|---|---|---|
| **MAE** | dollars | Average size of the error. MAE of 4.20 means predictions were off by about $4.20 on a typical day. |
| **RMSE** | dollars | Same idea, but squares errors first, so large misses count for much more. |
| **MAPE** | percent | Error as a share of the actual price. Comparable across tickers. |
| **R-squared** | ratio | How much of the price movement the model explains. |

**MAE vs RMSE.** MAE treats a $10 miss as exactly twice as bad as a $5 miss. RMSE squares errors
before averaging, so one big miss hurts far more than several small ones. Comparing them is
informative: RMSE much higher than MAE means the model is usually close but occasionally badly
wrong; RMSE close to MAE means errors are evenly sized.

**Why MAPE too.** Being $5 off matters much more on a $20 stock than a $500 one. MAPE normalizes
for that, which is what makes comparing AAPL against a cheaper ticker meaningful.

**R-squared, including negatives.** 1.0 is perfect. 0 means the model does no better than simply
predicting the average price. **Negative values mean it does worse than that** - which happens
regularly in stock forecasting, and is worth reporting honestly rather than hiding.

Lower is better for the first three; higher is better for R-squared.

The Forecasts tab shows a second, different set of numbers: where real prices already exist for the
forecast window, it scores the forecast currently on screen against them. That is a live check on
this specific prediction, separate from the training-time metrics above.

---

## Design decisions worth knowing

**Per-ticker, versioned model storage.** Each training run saves to its own timestamped folder
(`models/AAPL/2026-08-24_14-30-12/`), with a `latest.txt` pointer marking which run is live. The
pointer only moves after all three models finish successfully - so a retrain that fails partway
through leaves the previously working model serving predictions instead of corrupting it.

**Two views of the same data.** The LSTM trains on normalized 0-1 sequences; Prophet and ARIMA
train on real dates and real prices. Prophet's seasonality detection specifically depends on real
calendar dates, so normalizing everything up front would quietly undermine it. All metrics are
reported in real price units so the three are directly comparable.

**Training data capped at 5 years.** Longer windows mix market conditions that are too different
to be useful (a stock's behavior 15 years ago says little about tomorrow), and training time
scales with data size.

**Forecast horizon capped at 60 days.** LSTM forecasts are autoregressive - each day's prediction
feeds the next - so error compounds and accuracy degrades the further out you look.

**Forecasts start from the training cutoff, not today.** Every model is trained on data up to a
specific date, and predictions continue from there. Retrain to move that anchor forward.

---

## Known limitations

- ARIMA uses a fixed `(1,1,1)` order rather than searching for the best fit, so its long-horizon
  forecasts tend to flatten out. `pmdarima.auto_arima` would improve this.
- LSTM training isn't seeded, so retraining the same ticker twice can produce noticeably different
  results.
- Old training runs accumulate on disk - there's no cleanup of superseded runs.
- `/historical` re-fetches from Yahoo Finance on every call rather than reading its own cache.

---

## Stack

Python 3.9, FastAPI, PyTorch, Prophet, statsmodels, SQLAlchemy, PostgreSQL, Streamlit, Plotly,
Redis, Docker, pytest.