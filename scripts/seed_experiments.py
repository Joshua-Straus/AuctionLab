from backend.app.database import SessionLocal
from backend.app.seed import seed_experiments


def main() -> None:
    with SessionLocal() as session:
        seed_experiments(session)


if __name__ == "__main__":
    main()
