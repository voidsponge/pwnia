# 💀 PwnIA : Autonomous Offensive AI Agent (v8)

![Version](https://img.shields.io/badge/version-8.0-red?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python) ![Docker](https://img.shields.io/badge/Docker-Kali_Rolling-blue?style=for-the-badge&logo=docker) ![AI](https://img.shields.io/badge/Model-Gemini_2.5_Flash-orange?style=for-the-badge&logo=google)

> **⚠️ DISCLAIMER** > *Ce projet est une preuve de concept (PoC) développée à des fins éducatives et de recherche en cybersécurité. Il est conçu pour être utilisé uniquement sur des environnements autorisés (CTF, Cyber Ranges, Réseaux privés). L'auteur décline toute responsabilité en cas d'utilisation malveillante.*

---

## 🚀 Introduction

**PwnIA** n'est pas un simple script d'automatisation. C'est un **Agent Autonome** capable de conduire un audit de sécurité offensif (Red Teaming) de bout en bout.

Piloté par le modèle **Gemini 2.5 Flash**, il possède des "yeux" pour voir le Web, des "mains" pour exécuter des outils Kali Linux, et une "mémoire" pour ne jamais perdre le fil de sa mission.

Il scanne, analyse, exploite et rapporte ses découvertes sans intervention humaine.

---

## ⚡ Fonctionnalités Clés

| Module | Description |
| :--- | :--- |
| **🧠 Mission Brain** | Gestion d'état JSON persistante. L'agent sait toujours où il en est (Ports, Vulns, Loot). |
| **👁️ Computer Vision** | Utilisation de **Selenium** pour capturer et analyser visuellement les pages Web cibles. |
| **⚡ Nuclei Scanner** | Intégration du scanner le plus rapide du marché pour détecter les failles Web critiques en quelques secondes. |
| **☢️ Metasploit RPC** | Pilotage complet du framework Metasploit pour lancer des exploits complexes (RCE, EternalBlue...). |
| **🕵️ Advanced Looter** | Moteur de Regex intelligent pour exfiltrer automatiquement des secrets (AWS Keys, Shadow Hash, SSH Keys). |
| **🖥️ C2 Dashboard** | Interface de commandement **Streamlit** pour suivre l'attaque en temps réel (Logs & Visuels). |
| **📝 Auto-Reporting** | Génération automatique d'un rapport HTML professionnel en fin de mission. |

---

## 🏗️ Architecture Technique

L'agent repose sur une architecture modulaire dockerisée :

1.  **Perception (Input) :** Nmap (Réseau), Nuclei (Web), Vision (Screenshots).
2.  **Cognition (LLM) :** Gemini 2.5 analyse les résultats et consulte sa **Mémoire RAG** (ChromaDB) remplie de techniques de hacking.
3.  **Décision :** L'agent met à jour son plan d'attaque dans le `MissionBrain`.
4.  **Action (Output) :** Exécution de scripts Python générés à la volée ou de commandes Shell.

---

## 📸 Aperçu (Screenshots)

### 1. Le Terminal (Lancement & ASCII Art)
*L'agent démarre avec une séquence de boot stylisée.*

### 2. Le Dashboard C2 (Streamlit)
*Surveillance en temps réel des ports, vulnérabilités et du flux vidéo.*

### 3. Le Rapport Final (HTML)

---

## 🛠️ Installation & Utilisation

### Prérequis
* Docker & Docker Compose
* Une clé API Google Gemini (`GOOGLE_API_KEY`)

### 1. Installation
```bash
# Cloner le repo (si applicable)
git clone [https://github.com/voidsponge/pwnia.git](https://github.com/ton-user/pwnia.git)
cd pwnia

# Construire l'image Docker (inclut Kali, Nuclei, Metasploit)
docker build -t pwnia-gold .

```

### 2. Lancement du C2 Server (Dashboard + Agent)

```bash
# Lance le conteneur avec le port 8501 ouvert pour le Dashboard
docker run -it --rm --network host \
  -v $(pwd)/pwn_memory:/app/chroma_db \
  -v $(pwd):/app \
  -e GOOGLE_API_KEY="TA_CLE_ICI" \
  -p 8501:8501 \
  pwnia-gold bash

```

### 3. Démarrage

Dans le conteneur, lancez ces deux commandes (dans un multiplexer ou en background) :

```bash
# 1. Lancer le Dashboard
streamlit run dashboard.py &

# 2. Lancer l'Agent
python3 pwn_agent.py

```

Rendez-vous sur `http://localhost:8501` pour voir le QG.

---

## 🎯 Scénario d'Attaque (Demo)

Commande envoyée à l'agent :

> **Hack >** `auto scanme.nmap.org`

**Déroulement autonome :**

1. **[RECON]** Découverte des ports 80 (HTTP) et 22 (SSH).
2. **[VISION]** Capture d'écran de la page d'accueil (visible sur le Dashboard).
3. **[VULN]** Lancement de **Nuclei** sur le port 80 -> Aucune faille critique immédiate.
4. **[BRUTE]** Tentative de brute-force Hydra sur le SSH (simulé).
5. **[REPORT]** Génération du fichier `RAPPORT_scanme.html` avec le résumé de la surface d'attaque.

---

## 🛡️ Sécurité & Éthique

* **Pas de Persistance :** L'agent est configuré pour l'audit. Il ne crée pas de backdoors, ne modifie pas les crontabs et n'installe pas de rootkits.
* **Sandbox Docker :** L'agent tourne dans un conteneur isolé pour éviter toute fuite ou modification du système hôte.
* **Human-in-the-loop (Optionnel) :** Le mode manuel permet de valider chaque action avant exécution.

---

## 💻 Stack Technologique

* 🐍 **Python 3.11** (Core Logic)
* 🐳 **Docker** (Environment Kali Linux)
* 🧠 **Google Gemini** (Decision Making)
* 🕷️ **Selenium** (Computer Vision)
* ⚡ **Nuclei & Metasploit** (Offensive Tools)
* 📊 **Streamlit** (Frontend Dashboard)
