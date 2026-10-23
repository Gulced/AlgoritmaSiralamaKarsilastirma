def insertionSort(dizi, sayaclar):
    """Elemanları sağa kaydırarak diziyi yerinde sıralar."""
    for indeks in range(1, len(dizi)):
        gecici = dizi[indeks]
        sayaclar.hareket_sayisi += 1
        sol_indeks = indeks - 1

        while sol_indeks >= 0:
            # Başarısız son veri karşılaştırması da sayılır.
            sayaclar.karsilastirma_sayisi += 1
            if dizi[sol_indeks] <= gecici:
                break
            dizi[sol_indeks + 1] = dizi[sol_indeks]
            sayaclar.hareket_sayisi += 1
            sol_indeks -= 1

        # Geçici elemanın son yerleştirmesi de bir veri atamasıdır.
        dizi[sol_indeks + 1] = gecici
        sayaclar.hareket_sayisi += 1
