FROM docker.io/python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app/
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY epitrello/ epitrello/
COPY manage.py manage.py
CMD ["uvicorn", "--host", "0", "epitrello.asgi:application"]
