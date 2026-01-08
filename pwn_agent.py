import sys
import os
import warnings
import json
import subprocess
import time
import uuid
import re
import random
from colorama import Fore, Style, init

# Configuration Système
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
os.environ["CHROMA_LOG_LEVEL"] = "ERROR"
warnings.simplefilter("ignore")
try:
    if sys.stdin: sys.stdin.reconfigure(encoding='utf-8')
    if sys.stdout: sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr: sys.stderr.reconfigure(encoding='utf-8')
except AttributeError: pass

import chromadb
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Metasploit Check
try:
    from pymetasploit3.msfrpc import MsfRpcClient
    MSF_AVAILABLE = True
except ImportError:
    MSF_AVAILABLE = False

init(autoreset=True)

MY_API_KEY = os.getenv("GOOGLE_API_KEY")
if not MY_API_KEY:
    print(f"{Fore.RED}[ERREUR] Clé API manquante.{Style.RESET_ALL}")
    exit(1)
genai.configure(api_key=MY_API_KEY)

# --- ANIMATION ---
def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')
def loading_bar(desc, dur=1):
    steps=15; sys.stdout.write(f"{Fore.CYAN}{desc:<40} ["); sys.stdout.flush()
    for i in range(steps): time.sleep(dur/steps); sys.stdout.write("█"); sys.stdout.flush()
    print(f"] {Fore.GREEN}OK{Style.RESET_ALL}")

def startup_animation():
    clear_screen()
    print(f"""{Fore.RED}{Style.BRIGHT}
    ██████╗ ██╗    ██╗███╗   ██╗██╗ █████╗ 
    ██╔══██╗██║    ██║████╗  ██║██║██╔══██╗
    ██████╔╝██║ █╗ ██║██╔██╗ ██║██║███████║
    ██╔═══╝ ██║███╗██║██║╚██╗██║██║██╔══██║
    ██║     ╚███╔███╔╝██║ ╚████║██║██║  ██║
    ╚═╝      ╚══╝╚══╝ ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝ v8.0 (NUCLEI + C2)
    {Style.RESET_ALL}""")
    time.sleep(0.5)
    loading_bar("🔥 Initialisation Nuclei Engine", 0.5)
    loading_bar("📡 Connexion au Dashboard C2", 0.5)
    print(f"\n{Fore.GREEN}SYSTEM READY.{Style.RESET_ALL}")

# --- MISSION BRAIN ---
class MissionBrain:
    def __init__(self, filename="mission_state.json"):
        self.filename = filename
        if not os.path.exists(self.filename): self.reset_mission()
    def reset_mission(self):
        self.save_state({"target_ip": "Non définie", "ports_open": [], "identified_services": {}, "confirmed_vulnerabilities": [], "loot": [], "status": "IDLE"})
    def load_state(self):
        try: 
            with open(self.filename, "r", encoding='utf-8') as f: return json.load(f)
        except: return {}
    def save_state(self, state):
        with open(self.filename, "w", encoding='utf-8') as f: json.dump(state, f, indent=4)
    def update_mission(self, category, value):
        s = self.load_state()
        if category == 'target': s['target_ip'] = value
        elif category == 'status': s['status'] = value
        elif category == 'port': 
            if value not in s['ports_open']: s['ports_open'].append(value)
        elif category == 'service':
            if ":" in value: p,v = value.split(":",1); s['identified_services'][p] = v
        elif category == 'vuln':
            if value not in s['confirmed_vulnerabilities']: s['confirmed_vulnerabilities'].append(value)
        elif category == 'loot':
            if value not in s['loot']: s['loot'].append(value)
        self.save_state(s)
        return f"✅ UPDATE [{category}]: {value}"
    def get_dashboard(self):
        s = self.load_state()
        return f"DASHBOARD: TGT={s.get('target_ip')} | PORTS={s.get('ports_open')} | VULNS={s.get('confirmed_vulnerabilities')} | LOOT={s.get('loot')}"

mission = MissionBrain()

# --- REPORTER ---
class HTMLReporter:
    def __init__(self, brain): self.brain = brain
    def generate(self):
        d = self.brain.load_state()
        html = f"<html><body style='background:#111;color:#0f0;font-family:monospace'><h1>RAPPORT {d.get('target_ip')}</h1><h2>VULNS</h2><p>{d.get('confirmed_vulnerabilities')}</p><h2>LOOT</h2><p>{d.get('loot')}</p></body></html>"
        with open(f"RAPPORT_{d.get('target_ip')}.html", "w") as f: f.write(html)
        return "📄 Rapport HTML Généré."
reporter = HTMLReporter(mission)

# --- RAG ---
class RAGBrain:
    def __init__(self): 
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.coll = self.client.get_or_create_collection("pwn_knowledge")
    def memorize(self, c, t):
        emb = genai.embed_content(model="models/text-embedding-004", content=c)["embedding"]
        self.coll.add(documents=[c], embeddings=[emb], metadatas=[{"tag": t}], ids=[str(uuid.uuid4())])
        return "✅ Mémorisé."
    def recall(self, q):
        emb = genai.embed_content(model="models/text-embedding-004", content=q)["embedding"]
        res = self.coll.query(query_embeddings=[emb], n_results=2)
        return str(res['documents'][0]) if res['documents'][0] else "Rien trouvé."
rag = RAGBrain()

# --- TOOLS ---
def execute_shell(cmd):
    print(f"\n{Fore.YELLOW}[SHELL] {cmd}{Style.RESET_ALL}")
    if "rm -rf" in cmd: return "BLOQUÉ"
    try: return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120).stdout[:20000]
    except Exception as e: return f"Error: {e}"

def python_interpreter(code):
    print(f"\n{Fore.YELLOW}[PYTHON] Executing...{Style.RESET_ALL}")
    with open("temp_exploit.py", "w") as f: f.write(code)
    try: return subprocess.run(["python3", "temp_exploit.py"], capture_output=True, text=True, timeout=30).stdout
    except Exception as e: return f"Error: {e}"

def vision_scan(url):
    print(f"\n{Fore.CYAN}[VISION] {url}{Style.RESET_ALL}")
    opts = Options(); opts.add_argument("--headless"); opts.add_argument("--no-sandbox"); opts.add_argument("--disable-dev-shm-usage")
    driver = None
    try:
        driver = webdriver.Chrome(options=opts); driver.get(url); time.sleep(2); driver.save_screenshot("screenshot.png"); driver.quit()
        return "[IMAGE_READY]"
    except Exception as e: 
        if driver: driver.quit()
        return f"Error Vision: {e}"

def run_nuclei_scan(url):
    print(f"\n{Fore.RED}[NUCLEI] Fast Scan: {url}{Style.RESET_ALL}")
    cmd = f"nuclei -u {url} -s critical,high -silent -no-color"
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        if res.stdout.strip():
            mission.update_mission("vuln", f"[NUCLEI] Found: {res.stdout.strip()[:100]}")
            return f"✅ NUCLEI FOUND:\n{res.stdout}"
        return "✅ Nuclei Clean."
    except Exception as e: return f"Error Nuclei: {e}"

def execute_metasploit(inst):
    if not MSF_AVAILABLE: return "MSF Missing."
    print(f"\n{Fore.MAGENTA}[MSF] {inst}{Style.RESET_ALL}")
    try:
        c = MsfRpcClient('pwnia_secret', port=55553, ssl=True)
        if "search" in inst: return str(c.modules.search(inst.split()[1])[:3])
        if "use" in inst:
            p = inst.split(); exp = c.modules.use('exploit', p[1])
            if "TARGET" in p: exp['RHOSTS'] = p[p.index("TARGET")+1]
            return f"Job: {exp.execute(payload='cmd/unix/interact')['job_id']}"
    except Exception as e: return f"Error MSF: {e}"

def analyze_loot(content, source):
    print(f"\n{Fore.MAGENTA}[LOOT] Analyzing {source}{Style.RESET_ALL}")
    found = []
    if "AKIA" in content: found.append("AWS Key")
    if "root:" in content: found.append("Root User")
    if "flag{" in content: found.append("FLAG")
    if found: mission.update_mission("loot", str(found)); return f"SECRETS: {found}"
    return "No secrets."

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
ROLE: PwnIA, IA Offensive Elite.
OUTILS:
1. SHELL (Nmap) / VISION (Selenium)
2. NUCLEI (`run_nuclei_scan`): OBLIGATOIRE si HTTP détecté (Port 80/443). Utilise-le AVANT Metasploit.
3. METASPLOIT / PYTHON (Exploits)
4. MISSION / LOOT / REPORTER (Gestion)

PROCESS:
1. Reco (Nmap).
2. Si Web -> Vision + NUCLEI (Scan Rapide).
3. Si Vuln -> Exploit (MSF/Python).
4. Post-Exploit -> Loot.
5. Rapport.
"""

model = genai.GenerativeModel('gemini-2.5-flash', tools=[execute_shell, python_interpreter, vision_scan, run_nuclei_scan, rag.memorize, rag.recall, mission.update_mission, execute_metasploit, analyze_loot, reporter.generate], system_instruction=SYSTEM_PROMPT, safety_settings={HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE})

def main():
    startup_animation()
    try: subprocess.Popen(["msfrpcd", "-P", "pwnia_secret", "-n", "-f", "-a", "127.0.0.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(8)
    except: pass
    mission.reset_mission()
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    auto_mode = False
    
    while True:
        try:
            if not auto_mode: u_input = input(f"\n{Fore.BLUE}Hack > {Style.RESET_ALL}")
            else:
                d = mission.get_dashboard()
                print(f"\n{Fore.YELLOW}[AUTO] Thinking...{Style.RESET_ALL}")
                u_input = f"{d}\nANALYSE DASHBOARD. NEXT STEP? (NUCLEI if web, MSF if vuln). IF DONE: REPORT."
            
            if u_input.startswith("auto ") and not auto_mode:
                auto_mode = True; mission.update_mission('target', u_input.split()[1]); u_input = f"GO AUTO {u_input.split()[1]}"

            if "exit" in u_input: break
            
            resp = chat.send_message(u_input + " [CTF MODE]")
            
            if os.path.exists("screenshot.png") and time.time() - os.path.getmtime("screenshot.png") < 15:
                print(f"{Fore.CYAN}[IMG] Sending Image...{Style.RESET_ALL}")
                resp = chat.send_message(["Visuel:", Image.open("screenshot.png")])
            
            print(f"\n{Fore.GREEN}PwnIA >{Style.RESET_ALL} {resp.text}")
            
            if auto_mode and ("RAPPORT" in resp.text or "MISSION COMPLETE" in resp.text):
                auto_mode = False
                
        except Exception as e: print(f"Crash: {e}"); auto_mode = False

if __name__ == "__main__":
    main()
