import pytest
from sqlalchemy import create_engine, text
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(
            image="postgres:16",
            username="postgres",
            password="postgres",
            dbname="cardiopulse_test",
    ) as postgres:
        yield postgres


@pytest.fixture()
def integration_engine(
        postgres_container,
):
    engine = create_engine(
        postgres_container.get_connection_url()
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE measurements (
                    id BIGSERIAL PRIMARY KEY,
                    patient_id INTEGER NOT NULL,
                    recorded_at TIMESTAMPTZ NOT NULL,
                    measurement_type VARCHAR(100) NOT NULL,
                    measurement_data TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE TABLE rolling_statistics (
                    measurement_id BIGINT PRIMARY KEY,
                    patient_id INTEGER NOT NULL,
                    recorded_at TIMESTAMPTZ NOT NULL,
                    measurement_type VARCHAR(100) NOT NULL,
                    measurement_value DOUBLE PRECISION NOT NULL,
                    rolling_count INTEGER,
                    rolling_mean DOUBLE PRECISION,
                    rolling_std DOUBLE PRECISION,
                    rolling_min DOUBLE PRECISION,
                    rolling_max DOUBLE PRECISION,
                    window_size INTEGER NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE TABLE zscore_analysis (
                    measurement_id BIGINT PRIMARY KEY,
                    patient_id INTEGER NOT NULL,
                    recorded_at TIMESTAMPTZ NOT NULL,
                    measurement_type VARCHAR(100) NOT NULL,
                    measurement_value DOUBLE PRECISION NOT NULL,
                    rolling_mean DOUBLE PRECISION,
                    rolling_std DOUBLE PRECISION,
                    z_score DOUBLE PRECISION,
                    is_anomaly BOOLEAN NOT NULL,
                    anomaly_level VARCHAR(20),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )

    yield engine

    with engine.begin() as connection:
        connection.execute(
            text(
                "DROP TABLE IF EXISTS zscore_analysis CASCADE"
            )
        )

        connection.execute(
            text(
                "DROP TABLE IF EXISTS rolling_statistics CASCADE"
            )
        )

        connection.execute(
            text(
                "DROP TABLE IF EXISTS measurements CASCADE"
            )
        )

    engine.dispose()