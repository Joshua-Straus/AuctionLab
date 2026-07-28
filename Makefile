.PHONY: api frontend migrate seed test

api:
	uvicorn backend.app.main:app --reload --port 8000

frontend:
	streamlit run streamlit_app.py --server.port 8501

migrate:
	alembic upgrade head

seed:
	python3 -m scripts.seed_experiments

test:
	python3 -m pytest
