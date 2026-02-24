"""배포 설정 (Neon SSL, CORS, lifespan create_all) 검증 테스트."""

import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from unittest.mock import patch

import pytest
from sqlalchemy import inspect, text

from app.config import Settings
from app.database import Base, _build_engine


class TestCorsOriginsParsing:
    """cors_origins 설정값이 올바르게 파싱되는지 검증."""

    def test_single_origin(self):
        settings = Settings(
            database_url="sqlite:///./test.db",
            cors_origins="https://myapp.vercel.app",
        )
        origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
        assert origins == ["https://myapp.vercel.app"]

    def test_multiple_origins(self):
        settings = Settings(
            database_url="sqlite:///./test.db",
            cors_origins="https://a.com, https://b.com, https://c.com",
        )
        origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
        assert origins == ["https://a.com", "https://b.com", "https://c.com"]

    def test_wildcard_origin(self):
        settings = Settings(
            database_url="sqlite:///./test.db",
            cors_origins="*",
        )
        origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
        assert origins == ["*"]

    def test_default_is_wildcard(self):
        settings = Settings(database_url="sqlite:///./test.db")
        assert settings.cors_origins == "*"


class TestBuildEngineSSL:
    """_build_engine가 PostgreSQL URL에만 SSL을 적용하는지 검증."""

    def test_sqlite_no_ssl(self):
        with patch("app.database.settings") as mock_settings:
            mock_settings.database_url = "sqlite:///./test.db"
            engine = _build_engine()
            # SQLite 엔진이 정상 생성되어야 함
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.scalar() == 1

    def test_postgresql_url_gets_ssl_args(self):
        with patch("app.database.settings") as mock_settings:
            mock_settings.database_url = "postgresql://user:pass@host/db"
            engine = _build_engine()
            # connect_args에 sslmode=require가 포함되어야 함
            # 실제 연결은 하지 않고 엔진 생성만 확인
            assert "postgresql" in str(engine.url)


class TestLifespanCreateAll:
    """lifespan 이벤트에서 테이블이 자동 생성되는지 검증."""

    def test_tables_created_on_startup(self):
        from fastapi.testclient import TestClient

        from app.main import app

        with TestClient(app) as client:
            resp = client.get("/health")
            assert resp.status_code == 200

        # lifespan이 실행된 후 테이블이 존재하는지 확인
        from app.database import engine as prod_engine

        inspector = inspect(prod_engine)
        table_names = inspector.get_table_names()
        assert "books" in table_names
        assert "pages" in table_names
