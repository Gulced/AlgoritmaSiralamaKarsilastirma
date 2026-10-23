def _asagi_suz(dizi, yigin_boyutu, kok, sayaclar):
    """Kökteki elemanı yinelemeli olarak uygun seviyeye indirir."""
    while True:
        en_buyuk = kok
        sol_cocuk = 2 * kok + 1
        sag_cocuk = 2 * kok + 2

        if sol_cocuk < yigin_boyutu:
            sayaclar.karsilastirma_sayisi += 1
            if dizi[sol_cocuk] > dizi[en_buyuk]:
                en_buyuk = sol_cocuk
        if sag_cocuk < yigin_boyutu:
            sayaclar.karsilastirma_sayisi += 1
            if dizi[sag_cocuk] > dizi[en_buyuk]:
                en_buyuk = sag_cocuk

        if en_buyuk == kok:
            break

        gecici = dizi[kok]
        dizi[kok] = dizi[en_buyuk]
        dizi[en_buyuk] = gecici
        sayaclar.hareket_sayisi += 3
        kok = en_buyuk


def _max_yigin_olustur(dizi, sayaclar):
    # Son iç düğümden köke ilerleyerek alt yığınları düzelt.
    for kok in range(len(dizi) // 2 - 1, -1, -1):
        _asagi_suz(dizi, len(dizi), kok, sayaclar)


def heapSort(dizi, sayaclar):
    """Max Heap ile yerinde sıralar; yinelemeli süzme O(1) ek alan kullanır.

    Yığın kurma O(n), her çıkarma en fazla O(log n): toplam O(n log n).
    Her veri karşılaştırması 1, geçici dahil her gerçek swap 3 sayılır.
    """
    _max_yigin_olustur(dizi, sayaclar)
    for son_indeks in range(len(dizi) - 1, 0, -1):
        # En büyük elemanı sıralı son bölüme taşı; bu bölümü yığından çıkar.
        gecici = dizi[0]
        dizi[0] = dizi[son_indeks]
        dizi[son_indeks] = gecici
        sayaclar.hareket_sayisi += 3
        _asagi_suz(dizi, son_indeks, 0, sayaclar)
