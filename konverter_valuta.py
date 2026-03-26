evri_dinari = lambda dinari : dinari * 117
dinari_evri = lambda evri: evri / 117
choice = float(input("izaberite da li zelite da konvertujete 1: dinare u evre ili 2: evre u dinare (1/2): "))
if choice == 1:
    dinari = float(input("Unesite iznos u dinarima: "))
    print(f"U evrima: {dinari_evri(dinari)}")
elif choice == 2:
    evri = float(input("Unesite iznos u evrima: "))
    print(f"U dinarima: {evri_dinari(evri)}")
else:
    print("Neispravan izbor. Molimo izaberite '1' ili '2'.")
