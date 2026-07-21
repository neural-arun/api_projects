# Environment and Config

## Why .env Files?

Hard-coding configuration is a security risk and makes deployment painful.

| Approach | Problem |
|---|---|
| `DATABASE_URL = "postgresql://..."` in code | Commits secrets to git |
| Different values for dev/staging/prod | Need to edit code each time |
| API keys in source | Anyone with repo access sees them |

Solution: Environment variables loaded from a `.env` file.

```
# .env — NEVER commit this file
DATABASE_URL=postgresql://user:pass@localhost:5432/appointments
SECRET_KEY=your-secret-key-here
DEBUG=true
```

## pydantic-settings

Instead of `os.getenv()`, use `pydantic-settings` for type-safe, validated config.

```bash
pip install pydantic-settings
```

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"


settings = Settings()  # Loads and validates on import
```

**What this gives you:**
- Type coercion (`DEBUG=true` → `bool(True)`)
- Validation (missing required fields raise error on startup)
- IDE autocomplete for `settings.database_url`
- Default values (`debug` defaults to `False`)

## Environment-Specific Configs

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"


class DevelopmentSettings(Settings):
    debug: bool = True
    database_url: str = "postgresql://localhost/dev"


class ProductionSettings(Settings):
    debug: bool = False


def get_settings() -> Settings:
    env = os.getenv("ENV", "development")
    if env == "production":
        return ProductionSettings()
    return DevelopmentSettings()
```

## Using Settings in the App

```python
# app/database.py
from app.config import settings

engine = create_engine(settings.database_url)
```

```python
# app/main.py
from app.config import settings

app = FastAPI(title="Healthcare API", debug=settings.debug)
```

## Injecting Settings via Depends()

```python
from fastapi import Depends
from app.config import Settings

def get_settings() -> Settings:
    return Settings()


@app.get("/info")
def get_info(settings: Settings = Depends(get_settings)):
    return {"environment": "production" if not settings.debug else "development"}
```

## DON'T commit .env

Add it to `.gitignore`:
```
.env
```

Create a `.env.example` instead:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
SECRET_KEY=change-me
DEBUG=true
```

## References

- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/)
- [pydantic-settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
