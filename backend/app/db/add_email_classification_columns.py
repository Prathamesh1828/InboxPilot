from sqlalchemy import inspect, text

from app.db.database import engine


def main():
    inspector = inspect(engine)

    columns = {
        column["name"]
        for column in inspector.get_columns("emails")
    }

    statements = []

    if "category" not in columns:
        statements.append(
            "ALTER TABLE emails ADD COLUMN category VARCHAR(50)"
        )

    if "classification_confidence" not in columns:
        statements.append(
            "ALTER TABLE emails "
            "ADD COLUMN classification_confidence FLOAT"
        )

    if "classified_at" not in columns:
        statements.append(
            "ALTER TABLE emails "
            "ADD COLUMN classified_at TIMESTAMP WITH TIME ZONE"
        )

    if not statements:
        print("✅ Email classification columns already exist.")
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

    print("✅ Email classification columns added successfully.")


if __name__ == "__main__":
    main()