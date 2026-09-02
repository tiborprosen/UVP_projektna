import argparse
from zajem import prenesi_strani
from naredi_csv import obdelaj_vse

def glavna_funkcija():
    parser = argparse.ArgumentParser(
        description="Celoten cevovod za zajem, obdelavo in shranjevanje podatkov o NFL igralcih."
    )
    parser.add_argument(
        "-s", "--skip-download", 
        action="store_true", 
        help="Preskoči prenos HTML datotek s spleta (uporabi že shranjene datoteke)."
    )
    parser.add_argument(
        "-p", "--pages", 
        type=int, 
        default=40, 
        help="Število strani za zajem (privzeto: 40 strani)."
    )

    args = parser.parse_args()

    print("=== ZAČETEK PROCESA ===")

    if args.skip_download:
        print("\n[1/2] Preskakujem prenos HTML datotek (--skip-download vklopljen).")
    else:
        print(f"\n[1/2] Začenjam prenos {args.pages} HTML strani...")
        prenesi_strani(st_strani=args.pages)

    print("\n[2/2] Začenjam izluščenje podatkov in shranjevanje v CSV...")
    obdelaj_vse()

    print("\n=== PROCES USPEŠNO ZAKLJUČEN ===")

if __name__ == "__main__":
    glavna_funkcija()