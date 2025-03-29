FROM python:3.12.9-slim
WORKDIR /app

# curl: for healthcheck
# libpq-dev, gcc, build-essential: for psycopg2
# software-properties-common: for add-apt-repository
# openssl: for generating keys
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \ 
    software-properties-common \
    libpq-dev \
    gcc \
    openssl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN cp template_secrets.toml .streamlit/secrets.toml

# Generate random keys for secrets.toml
RUN export COOKIE_KEY=$(openssl rand -base64 32) && sed -i "s|some cookie key|$COOKIE_KEY|g" .streamlit/secrets.toml
RUN export FERNET_KEY=$(openssl rand -base64 32) && sed -i "s|some Fernet compliant key|$FERNET_KEY|g" .streamlit/secrets.toml

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
