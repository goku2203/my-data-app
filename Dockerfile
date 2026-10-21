FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# build tools (tgcrypto compile aaga vendhaa thevai) - install pannitu remove pannidrom, image chinnadhaa irukkum
COPY requirements.txt .
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc build-essential \
 && pip install -r requirements.txt \
 && apt-get purge -y --auto-remove gcc build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY . .

# Render automatic-aa PORT set pannum (default 10000)
EXPOSE 10000

CMD ["python3", "bot.py"]
