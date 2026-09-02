import os
import pandas as pd
from izluscenje import izlusci_kategorijo, MAPA_HTML

MAPA_CSV = "podatki"

def obdelaj_vse():
    kategorije = ["passing", "rushing", "receiving"]
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