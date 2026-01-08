FROM kalilinux/kali-rolling
LABEL maintainer="PwnIA-Gold"

# --- CORRECTIF ENCODAGE (CRUCIAL) ---
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8
# ------------------------------------

# 1. Installation Outils & Chrome
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    nmap curl wget netcat-traditional metasploit-framework \
    git gobuster hydra john sqlmap \
    wordlists iputils-ping procps \
    build-essential \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Installation de Nuclei (Scanner de vulnérabilités rapide)
RUN wget https://github.com/projectdiscovery/nuclei/releases/download/v3.1.0/nuclei_3.1.0_linux_amd64.zip \
    && unzip nuclei_3.1.0_linux_amd64.zip \
    && mv nuclei /usr/local/bin/ \
    && rm nuclei_3.1.0_linux_amd64.zip
# Mise à jour des templates Nuclei (base de données de failles)
RUN nuclei -update-templates

# 2. Rockyou Wordlist
RUN gzip -d /usr/share/wordlists/rockyou.txt.gz || true

# 3. Dépendances Python
COPY requirements.txt .
RUN pip3 install -r requirements.txt --break-system-packages

# 4. Dossiers
WORKDIR /app
RUN mkdir /app/chroma_db
RUN mkdir /app/screenshots
RUN mkdir /app/knowledge_input

# 5. Scripts
COPY pwn_agent.py .
COPY feed_brain.py .

CMD ["python3", "-u", "pwn_agent.py"]
