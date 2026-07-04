FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Non-root runtime user.
RUN useradd --create-home --shell /usr/sbin/nologin app

# Install deps first (better layer caching).
COPY pyproject.toml README.md ./
COPY server ./server
RUN pip install .

# Content and generated web artifacts (also bind-mounted in compose).
COPY content ./content
COPY web ./web
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh \
    && mkdir -p /app/data \
    && chown -R app:app /app

USER app
EXPOSE 8080
ENTRYPOINT ["entrypoint.sh"]
