# Auction and Market Strategy Simulator

A full-stack simulator for first-price and second-price auctions, double-auction
markets, and adaptive bidding strategies. The original simulation packages
remain framework-independent; FastAPI is the application boundary, PostgreSQL
stores experiment definitions and run outputs, and Streamlit is an HTTP-only
frontend.

## Architecture

```text
auction_sim/          Auction simulation engine (unchanged)
market_sim/           Double-auction engine (unchanged)
dashboard_logic.py    Engine orchestration shared by backend services

backend/app/
  main.py             FastAPI application and CORS configuration
  routes.py           Simulation and stored-experiment endpoints
  schemas.py          Validated API contracts
  services.py         Engine adapter and run persistence
  models.py           SQLAlchemy experiment/run models
  database.py         PostgreSQL session management
  seed.py             Idempotent pre-made experiment definitions

frontend/
  api_client.py       Typed boundary between Streamlit and FastAPI
streamlit_app.py      Presentation-only Streamlit application

migrations/           Alembic schema migrations
tests/                Engine and application tests
```

The frontend never imports the simulation engine. Every custom or pre-made run
travels through FastAPI and is persisted as an `experiment_runs` record.

## Run the full stack

The simplest path starts PostgreSQL, applies migrations, seeds experiments,
then starts both application processes:

```bash
docker compose up --build
```

Open:

- Streamlit: <http://localhost:8501>
- API documentation: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/api/v1/health>

PostgreSQL data lives in the named `postgres_data` Docker volume.

## Run services locally

Install dependencies and start PostgreSQL:

```bash
python3 -m pip install -r requirements.txt
docker compose up -d db
cp .env.example .env
```

Export the values from `.env` in your shell, then prepare the database:

```bash
alembic upgrade head
python3 -m scripts.seed_experiments
```

Run the backend and frontend in separate terminals:

```bash
make api
make frontend
```

Configuration is environment-based:

- `DATABASE_URL`: SQLAlchemy PostgreSQL URL
- `API_BASE_URL`: FastAPI base URL used by Streamlit
- `CORS_ORIGINS`: comma-separated browser origins accepted by FastAPI

## API

Custom simulations:

```text
POST /api/v1/simulations/auctions
POST /api/v1/simulations/markets
POST /api/v1/simulations/learning
```

Stored experiments:

```text
GET  /api/v1/experiments
GET  /api/v1/experiments/{slug}
POST /api/v1/experiments/{slug}/run
GET  /api/v1/runs/{run_id}
```

The run endpoint accepts an optional `overrides` object, merging validated
changes over the stored parameters.

## Test

```bash
python3 -m pytest
```

The existing engine tests continue to exercise the original application logic.
