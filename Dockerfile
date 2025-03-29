FROM python:3.12.9-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/isislab-unisa/vm-lab.git .

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["/bin/sh", "-c", "cp /app/template_secrets.toml /app/.streamlit/secrets.toml && streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]
