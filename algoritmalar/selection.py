def selectionSort(dizi, sayaclar):
    """Diziyi yerinde sıralar; işlem sayılarını verilen sayaçlara ekler."""
    for baslangic in range(len(dizi) - 1):
        en_kucuk_indeks = baslangic

        # Sıralanmamış bölümün en küçük elemanını bul.
        for indeks in range(baslangic + 1, len(dizi)):
            sayaclar.karsilastirma_sayisi += 1
            if dizi[indeks] < dizi[en_kucuk_indeks]:
                en_kucuk_indeks = indeks

        if en_kucuk_indeks != baslangic:
            # Geçici değişkene alma ve iki dizi yazımı toplam 3 harekettir.
            gecici = dizi[baslangic]
            dizi[baslangic] = dizi[en_kucuk_indeks]
            dizi[en_kucuk_indeks] = gecici
            sayaclar.hareket_sayisi += 3
