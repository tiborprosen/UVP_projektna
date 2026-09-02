# Analiza igralcev lige NFL (sezona 2025/26)

Projektna naloga pri predmetu Uvod v programiranje. Program zajame podatke o igralcih lige NFL v rednem delu sezone 2025/26 s spletne strani [Pro Football Reference](https://www.pro-football-reference.com/) (podaje, teki in sprejete podaje) ter izvede statistično analizo in vizualizacijo podatkov.

## Struktura projekta

- `zajem.py` – Prenaša HTML strani (passing, rushing, receiving) s spleta in jih lokalno shranjuje v `podatki/html/`.
- `izluscenje.py` – Parsira podatke (igralec, ekipa, pozicija, starost, št. tekem in statistike po kategorijah) iz lokalnih HTML datotek.
- `naredi_csv.py` – Združi izluščene podatke vseh kategorij in jih zapiše v `podatki/nfl_2025_statistika.csv`.
- `main.py` – Glavna skripta, ki povezuje celoten cevovod (pipeline).
- `analiza.ipynb` – Jupyter zvezek z analizo in vizualizacijo podatkov (podajalci, tekači, sprejemalci).
- `podatki/` – Mapa s shranjenimi HTML datotekami (`html/`) in končno CSV datoteko (`nfl_2025_statistika.csv`).
- `uporaba-ui.md` – Datoteka, ki vsebuje pogovor s Claudeom.

## Namestitev

1. **Ustvarite in aktivirajte virtualno okolje:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   (na macOS/Linux: `source venv/bin/activate`)

2. **Namestite potrebne knjižnice:**
   ```bash
   pip install requests beautifulsoup4 pandas matplotlib jupyter
   ```

## Zagon

Celoten cevovod (zajem HTML-ja → izluščenje podatkov → shranjevanje v CSV) poženete z:

```bash
python main.py
```

Neobvezni argumenti:

- `-s` / `--skip-download` – preskoči prenos HTML-ja in uporabi že shranjene datoteke v `podatki/html/` (uporabno, če želite samo ponovno izluščiti/shraniti podatke brez novega poizvedovanja po spletu).

Primer:
```bash
python main.py --skip-download
```

Ko je `podatki/nfl_2025_statistika.csv` ustvarjen, odprite `analiza.ipynb` (npr. v VS Code ali Jupyterju) in poženite celice od zgoraj navzdol za analizo in grafe.

