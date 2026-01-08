import warnings
warnings.filterwarnings("ignore", module="google.generativeai")

import os
import glob
import chromadb
import uuid
import google.generativeai as genai
from colorama import Fore, Style, init

init(autoreset=True)

MY_API_KEY = os.getenv("GOOGLE_API_KEY")
if not MY_API_KEY: exit(1)
genai.configure(api_key=MY_API_KEY)

# Dossiers à scanner
KNOWLEDGE_MAP = {
    "/app/knowledge_input/technical": {"tag": "TOOL", "prefix": "[DOC TECHNIQUE]"},
    "/app/knowledge_input/writeups":  {"tag": "STRAT", "prefix": "[WRITE-UP]"}
}
DB_PATH = "/app/chroma_db"

def ingest():
    print(f"{Fore.CYAN}=== INGESTION INTELLIGENTE (Support Repos Git) ==={Style.RESET_ALL}")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name="pwn_knowledge")
    
    total_files = 0

    for folder_root, meta in KNOWLEDGE_MAP.items():
        print(f"\n{Fore.YELLOW}--> Scan de : {folder_root}{Style.RESET_ALL}")
        
        # On utilise os.walk pour parcourir tous les sous-dossiers récursivement
        for current_dir, dirs, files in os.walk(folder_root):
            
            # FILTRE 1 : Ignorer le dossier .git (Crucial !)
            if ".git" in dirs:
                dirs.remove(".git")
            
            for filename in files:
                # FILTRE 2 : Seulement les fichiers texte utiles
                if not filename.endswith((".md", ".txt", ".py", ".sh")):
                    continue
                
                file_path = os.path.join(current_dir, filename)
                
                try:
                    # Lecture
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f: 
                        raw = f.read()
                    
                    if not raw.strip(): continue

                    # ASTUCE : On calcule le chemin relatif pour donner le contexte (ex: SQL/README.md)
                    relative_path = os.path.relpath(file_path, folder_root)
                    
                    # Découpage (Chunks)
                    chunks = [raw[i:i+8000] for i in range(0, len(raw), 8000)]
                    
                    for chunk in chunks:
                        # On injecte le chemin complet dans le texte
                        enhanced_content = f"{meta['prefix']}\nCONTEXTE/CHEMIN: {relative_path}\nCONTENU:\n{chunk}"
                        
                        emb = genai.embed_content(model="models/text-embedding-004", content=enhanced_content)["embedding"]
                        
                        collection.add(
                            documents=[enhanced_content],
                            embeddings=[emb],
                            metadatas=[{"type": meta["tag"], "path": relative_path}],
                            ids=[str(uuid.uuid4())]
                        )
                        print(".", end="", flush=True)
                    
                    total_files += 1

                except Exception as e:
                    # On ignore silencieusement les fichiers binaires ou illisibles
                    pass

    print(f"\n\n{Fore.GREEN}=== SUCCÈS : {total_files} fichiers ingérés dans le cerveau. ==={Style.RESET_ALL}")

if __name__ == "__main__":
    ingest()
