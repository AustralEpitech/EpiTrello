FROM docker.io/python:3.14-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

FROM base AS build
RUN python -m venv /opt/venv/
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base
COPY --from=build /opt/venv /opt/venv/
COPY epitrello/ epitrello/
COPY boards/ boards/
COPY manage.py .
CMD ["uvicorn", "--host", "0", "epitrello.asgi:application"]
