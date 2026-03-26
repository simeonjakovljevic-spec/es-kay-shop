cena = input("Unesite cenu proizvoda: ")    
popust = input("Unesite postotak popusta: ")        

def račun_popusta(cena, popust_postotak):
    if cena < 0 or popust_postotak < 0 or popust_postotak > 100:
        raise ValueError("Cena mora biti nenegativna, a popust između 0 i 100.")
    else:
        popust_iznos = (popust_postotak / 100) * cena
        konačna_cena = cena - popust_iznos
        return konačna_cena
try:
    rezultat = račun_popusta(float(cena), float(popust))
    print(f"konačna cena nakon popusta je: {rezultat}")
except ValueError as e:
    print(f"Greška: {e}")
finally:
    print("Hvala što koristite naš program za izračun popusta.")            