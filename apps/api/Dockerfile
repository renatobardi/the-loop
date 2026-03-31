FROM python:3.12-slim AS deps

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM deps AS build

COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

FROM python:3.12-slim AS runner

RUN groupadd -r api && useradd -r -g api -d /app -s /sbin/nologin api

WORKDIR /app

COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=deps /usr/local/bin/alembic /usr/local/bin/alembic
COPY --from=build /app/src src/
COPY --from=build /app/alembic alembic/
COPY --from=build /app/alembic.ini .

USER api

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
