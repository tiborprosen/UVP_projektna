import os
import re
import pandas as pd
from bs4 import BeautifulSoup, Comment

MAPA_HTML = os.path.join("podatki", "html")
MAPA_CSV = "podatki"

def ocisti_besedilo(tekst):
    if not tekst:
        return ""
    return re.sub(r'[*+]', '', tekst).strip()

def izlusci_kategorijo(pot_do_html, kategorija):
    with open(pot_do_html, "r", encoding="utf-8") as f:
        html_vsebina = f.read()

    soup = BeautifulSoup(html_vsebina, "html.parser")

    # Razširimo tabele iz HTML komentarjev, če obstajajo
    komentarji = soup.find_all(string=lambda text: isinstance(text, Comment))
    for kom in komentarji:
        if "data-stat" in kom:
            kom_soup = BeautifulSoup(kom, "html.parser")
            tabela = kom_soup.find("table")
            if tabela:
                soup.append(tabela)

    podatki = []
    tabela = soup.find("table")
    if not tabela:
        return podatki

    vrstice = tabela.find_all("tr")

    for vrstica in vrstice:
        if vrstica.find("th", {"data-stat": "ranker"}) and vrstica.find("th", {"data-stat": "ranker"}).text.strip() == "Rk":
            continue

        # Strogo filtriramo playoff vrstice (kot je tista z dodatnimi jardami za Josha Allena)
        id_vrstice = vrstica.get("id", "")
        if "playoff" in id_vrstice.lower():
            continue

        celica_opombe = vrstica.find(["td", "th"], {"data-stat": "notes"})
        celotno_besedilo_vrstice = vrstica.get_text().lower()
        if "playoff" in celotno_besedilo_vrstice or (celica_opombe and "playoff" in celica_opombe.text.lower()):
            continue

        ime_celica = vrstica.find(["td", "th"], {"data-stat": "name_display"})
        if not ime_celica:
            ime_celica = vrstica.find(["td", "th"], {"data-stat": "player"})
        if not ime_celica:
            continue
        
        ime = ocisti_besedilo(ime_celica.text)
        if not ime or ime == "Player" or not vrstica.find(["td", "th"]):
            continue

        def pridobi_val(stat_names, privzeta="0"):
            if isinstance(stat_names, str):
                stat_names = [stat_names]
            for stat in stat_names:
                celica = vrstica.find(["td", "th"], {"data-stat": stat})
                if celica and celica.text.strip():
                    return celica.text.strip()
            return privzeta

        ekipa_val = "N/A"
        for stat_name in ["team", "team_name_abbr", "team_name", "franchise_name"]:
            c = vrstica.find(["td", "th"], {"data-stat": stat_name})
            if c and c.text.strip():
                ekipa_val = c.text.strip()
                break
        
        if ekipa_val == "N/A":
            ekipa_link = vrstica.find("a", href=re.compile(r"/teams/"))
            if ekipa_link:
                ekipa_val = ekipa_link.text.strip()

        poz_val = ocisti_besedilo(pridobi_val("pos", privzeta="N/A"))
        tekme_val = pridobi_val(["games", "g"], privzeta="0")
        starost_val = pridobi_val("age", privzeta="0")

        vnos = {
            "igralec": ime,
            "ekipa": ocisti_besedilo(ekipa_val),
            "pozicija": poz_val if poz_val else "N/A",
            "starost": starost_val,
            "tekme": tekme_val,
        }

        # Dinamično dodamo samo tiste statistike, ki pripadajo trenutni kategoriji
        if kategorija == "passing":
            vnos.update({
                "passing_yards": pridobi_val("pass_yds"),
                "passing_td": pridobi_val("pass_td"),
                "passing_att": pridobi_val("pass_att"),
                "passing_cmp": pridobi_val("pass_cmp"),
                "passing_int": pridobi_val("pass_int"),
                "sacks": pridobi_val("pass_sacked"),
            })
        elif kategorija == "rushing":
            vnos.update({
                "rushing_yards": pridobi_val("rush_yds"),
                "rushing_td": pridobi_val("rush_td"),
                "rushing_att": pridobi_val("rush_att"),
                "fumbles": pridobi_val("fumbles"),
            })
        elif kategorija == "receiving":
            vnos.update({
                "receiving_yards": pridobi_val("rec_yds"),
                "receiving_td": pridobi_val("rec_td"),
                "receptions": pridobi_val("rec"),
                "targets": pridobi_val("targets"),
            })
        elif kategorija == "defense":
            vnos.update({
                "def_interceptions": pridobi_val("def_int"),
                "def_sacks": pridobi_val("def_sacks"),
            })

        podatki.append(vnos)

    return podatki

def obdelaj_vse():
    kategorije = ["passing", "rushing", "receiving", "defense"]
    dfs = []

    for kat in kategorije:
        pot = os.path.join(MAPA_HTML, f"{kat}_2025.html")
        if os.path.exists(pot):
            print(f"Luščim podatke iz {kat}_2025.html ...")
            zabrane_vrstice = izlusci_kategorijo(pot, kat)
            df_kat = pd.DataFrame(zabrane_vrstice)
            
            if not df_kat.empty:
                for col in df_kat.columns:
                    if col not in ["igralec", "ekipa", "pozicija"]:
                        df_kat[col] = pd.to_numeric(df_kat[col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
                
                if "ekipa" in df_kat.columns:
                    multi_team_mask = df_kat["ekipa"].str.contains(r"\dTM", na=False)
                    if multi_team_mask.any():
                        players_with_multi = df_kat.loc[multi_team_mask, "igralec"].unique()
                        df_kat = df_kat[~(df_kat["igralec"].isin(players_with_multi) & (~df_kat["ekipa"].str.contains(r"\dTM", na=False)))]

                dfs.append(df_kat)

    if dfs:
        df_končni = dfs[0]
        for d in dfs[1:]:
            ključi = [k for k in ["igralec", "ekipa"] if k in df_končni.columns and k in d.columns]
            df_končni = pd.merge(df_končni, d, on=ključi, how="outer", suffixes=("_x", "_y"))
            
            for col in ["pozicija", "starost", "tekme"]:
                col_x = f"{col}_x"
                col_y = f"{col}_y"
                if col_x in df_končni.columns and col_y in df_končni.columns:
                    df_končni[col] = df_končni[col_x].combine_first(df_končni[col_y])
                    df_končni.drop(columns=[col_x, col_y], inplace=True)

        zacetni_stolpci = ["igralec", "ekipa", "pozicija", "starost", "tekme"]
        for col in df_končni.columns:
            if col not in zacetni_stolpci:
                df_končni[col] = df_končni[col].fillna(0)

        os.makedirs(MAPA_CSV, exist_ok=True)
        pot_csv = os.path.join(MAPA_CSV, "nfl_2025_statistika.csv")
        df_končni.to_csv(pot_csv, index=False, encoding="utf-8")
        
        print(f"\nPodatki so pripravljeni! Skupno število podatkov (vrstic): {len(df_končni)}")
        print(f"CSV shranjen na: {pot_csv}")

if __name__ == "__main__":
    obdelaj_vse()