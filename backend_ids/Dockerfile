# backend_ids/Dockerfile (optional - for deployment)

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    iptables \
    sudo \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user for running app (iptables still needs sudo)
RUN useradd -m -u 1000 appuser && \
    echo "appuser ALL=(ALL) NOPASSWD: /usr/sbin/iptables" >> /etc/sudoers

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
