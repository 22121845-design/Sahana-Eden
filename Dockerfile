# Repo link (WIF3005 requirement): https://github.com/22121845-design/Sahana-Eden

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    build-essential gcc \
    libxml2-dev libxslt1-dev zlib1g-dev \
    libjpeg62-turbo-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN git clone --depth 1 https://github.com/web2py/web2py.git

WORKDIR /opt/web2py/applications/eden
COPY . .

WORKDIR /opt/web2py
RUN pip install --no-cache-dir -r applications/eden/requirements.txt

EXPOSE 8000

CMD ["python", "web2py.py", "-a", "admin", "-i", "0.0.0.0", "-p", "8000"]
