# Auction Strategy Research Simulator

A full-stack research application for studying bidding behavior in first-price
and second-price sealed-bid auctions. It supports truthful, shaded, random, and
epsilon-greedy strategies; Monte Carlo experiments; competition and strategy
sweeps; economic metrics; and persisted reproducible experiments.

The simulation engine remains framework-independent. FastAPI is the application
boundary, PostgreSQL stores experiment definitions and run outputs, and
Streamlit is an HTTP-only frontend.

## Research capabilities

- First-price and second-price sealed-bid mechanisms
- Truthful, random, fixed-shading, adaptive bandit, and equilibrium bidders
- Configurable bidder counts and private-value distributions
- Seller revenue, bidder profit, regret, win rate, and allocative efficiency
- Competition and head-to-head strategy sweeps
- Fixed-strategy versus adaptive-agent learning comparisons
- Dedicated Vickrey weak-dominance experiment comparing expected profit
- Dedicated first-price experiment comparing every available bidder type
- Paired revenue-equality test with trial-level seller revenue
- Reproducible stored experiments with parameter overrides

## Architecture

```text
auction_sim/          Framework-independent auction engine and analytics
dashboard_logic.py    Auction experiment orchestration

backend/app/
  main.py             FastAPI application and CORS configuration
  routes.py           Simulation and stored-experiment endpoints
  schemas.py          Validated API contracts
  services.py         Engine adapter and run persistence
  models.py           SQLAlchemy experiment/run models
  database.py         PostgreSQL session management
  seed.py             Idempotent research experiment definitions

frontend/
  api_client.py       Streamlit-to-FastAPI boundary
streamlit_app.py      Presentation-only Streamlit application

migrations/           Alembic schema migrations
tests/                Auction engine and application tests
```

The frontend never imports the simulation engine. Every custom or pre-made run
travels through FastAPI and is persisted as an `experiment_runs` record.

## Run the full stack

```bash
docker compose up --build
```

Open:

- Streamlit: <http://localhost:8501>
- API documentation: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/api/v1/health>

PostgreSQL data lives in the named `postgres_data` Docker volume.

## Run services locally

```bash
python3 -m pip install -r requirements.txt
docker compose up -d db
cp .env.example .env
```

Export the values from `.env`, prepare the database, then run the services in
separate terminals:

```bash
alembic upgrade head
python3 -m scripts.seed_experiments
make api
make frontend
```

Configuration:

- `DATABASE_URL`: SQLAlchemy PostgreSQL URL
- `API_BASE_URL`: FastAPI base URL used by Streamlit
- `CORS_ORIGINS`: comma-separated browser origins accepted by FastAPI

## API

```text
POST /api/v1/simulations/auctions
POST /api/v1/simulations/learning
POST /api/v1/simulations/vickrey
POST /api/v1/simulations/first-price-strategies
POST /api/v1/simulations/revenue-equality

GET  /api/v1/experiments
GET  /api/v1/experiments/{slug}
POST /api/v1/experiments/{slug}/run
GET  /api/v1/runs/{run_id}
```

The stored-experiment run endpoint accepts an optional `overrides` object and
merges validated changes over the saved parameters.

## Test

```bash
python3 -m pytest
```
