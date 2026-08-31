import os
import time
import requests

MAPA_PODATKI = "podatki"
MAPA_HTML = os.path.join(MAPA_PODATKI, "html")

# Podrobnejše glave brskalnika za obhod 403 blokade
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/",
}

URLI = {
    "passing": "https://www.pro-football-reference.com/years/2025/passing.htm",
    "rushing": "https://www.pro-football-reference.com/years/2025/rushing.htm",
    "receiving": "https://www.pro-football-reference.com/years/2025/receiving.htm"
}

def prenesi_nfl_strani(preskoci_obstojece=True):
    os.makedirs(MAPA_HTML, exist_ok=True)
    
    for kategorija, url in URLI.items():
        pot_datoteke = os.path.join(MAPA_HTML, f"{kategorija}_2025.html")
        
        if preskoci_obstojece and os.path.exists(pot_datoteke):
            print(f"Datoteka {kategorija}_2025.html že obstaja, preskakujem.")
            continue
            
        print(f"Prenašam {kategorija} z naslova: {url} ...")
        
        try:
            odziv = requests.get(url, headers=HEADERS, timeout=10)
            if odziv.status_code == 200:
                with open(pot_datoteke, "w", encoding="utf-8") as f:
                    f.write(odziv.text)
                print(f"Uspešno shranjeno: {pot_datoteke}")
            else:
                print(f"Napaka pri prenosu {kategorija}: Status {odziv.status_code}")
        except Exception as e:
            print(f"Prišlo je do napake: {e}")
            
        time.sleep(3)

if __name__ == "__main__":
    prenesi_nfl_strani()