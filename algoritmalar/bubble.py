def bubbleSort(dizi, sayaclar):
    """Komşu elemanları karşılaştırarak diziyi yerinde sıralar."""
    for son_indeks in range(len(dizi) - 1, 0, -1):
        degisim_oldu = False
        # Her turda en büyük eleman sona yerleşir; sonraki tur kısalır.
        for indeks in range(son_indeks):
            sayaclar.karsilastirma_sayisi += 1
            if dizi[indeks] > dizi[indeks + 1]:
                gecici = dizi[indeks]
                dizi[indeks] = dizi[indeks + 1]
                dizi[indeks + 1] = gecici
                sayaclar.hareket_sayisi += 3
                degisim_oldu = True

        if not degisim_oldu:
            break
