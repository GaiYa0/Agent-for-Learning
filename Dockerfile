ARG BASE_IMAGE=docker.m.daocloud.io/library/python:3.11-slim
FROM ${BASE_IMAGE}

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY pyproject.toml ./
COPY .streamlit ./.streamlit
COPY src ./src

RUN pip install --upgrade pip \
    && pip install -e ".[frontend]"

EXPOSE 8000 8501

CMD ["learning-assistant-api"]
