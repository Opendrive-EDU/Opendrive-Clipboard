FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir .

RUN python -m unittest discover -s tests

EXPOSE 8080

CMD ["sh", "-c", "python -m opendrive_clipboard.server --host 0.0.0.0 --port ${PORT}"]
