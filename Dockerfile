FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY company_documents ./company_documents
COPY scripts ./scripts

EXPOSE 8000
CMD ["uvicorn", "support_bot.api:app", "--host", "0.0.0.0", "--port", "8000"]