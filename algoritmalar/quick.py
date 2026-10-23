def pivot_indeksi_sec(baslangic, bitis, pivot_yontemi):
    """Desteklenen yönteme göre alt dizinin pivot indeksini seçer."""
    if pivot_yontemi == "orta":
        # Orta indeksteki değer seçilir; değerlerin medyanı hesaplanmaz.
        return (baslangic + bitis) // 2
    if pivot_yontemi == "ilk":
        return baslangic
    raise ValueError("Geçersiz pivot yöntemi: 'orta' veya 'ilk' seçin.")


def _bolumle(dizi, baslangic, bitis, sayaclar, pivot_yontemi):
    pivot = dizi[pivot_indeksi_sec(baslangic, bitis, pivot_yontemi)]
    # Pivot değerini geçiciye almak da 1 veri atamasıdır.
    sayaclar.hareket_sayisi += 1
    sol = baslangic
    sag = bitis

    while sol <= sag:
        while sol <= bitis:
            sayaclar.karsilastirma_sayisi += 1
            if not dizi[sol] < pivot:
                break
            sol += 1
        while sag >= baslangic:
            sayaclar.karsilastirma_sayisi += 1
            if not dizi[sag] > pivot:
                break
            sag -= 1

        if sol <= sag:
            if sol != sag:
                gecici = dizi[sol]
                dizi[sol] = dizi[sag]
                dizi[sag] = gecici
                sayaclar.hareket_sayisi += 3
            # Eşit değerlerde de ilerleyerek sonsuz döngüyü önle.
            sol += 1
            sag -= 1
    return sol, sag


def _araligi_sirala(dizi, baslangic, bitis, sayaclar, pivot_yontemi):
    while baslangic < bitis:
        sol, sag = _bolumle(dizi, baslangic, bitis, sayaclar, pivot_yontemi)
        # Küçük bölüme özyineleme, büyük bölüme döngü: çağrı derinliği sınırlanır.
        if sag - baslangic < bitis - sol:
            _araligi_sirala(dizi, baslangic, sag, sayaclar, pivot_yontemi)
            baslangic = sol
        else:
            _araligi_sirala(dizi, sol, bitis, sayaclar, pivot_yontemi)
            bitis = sag


def quickSort(dizi, sayaclar, pivot_yontemi="orta"):
    """İki yönlü bölümleme ile yerinde sıralar; sayaçları sıfırlamaz.

    Her bölümlemede pivot kopyası 1, gerçek swap 3 harekettir.
    Başarısız değer karşılaştırmaları sayılır; indeks kontrolleri sayılmaz.
    """
    # Boş ve tek elemanlı girdilerde de yöntem doğrulanır.
    pivot_indeksi_sec(0, len(dizi) - 1, pivot_yontemi)
    _araligi_sirala(dizi, 0, len(dizi) - 1, sayaclar, pivot_yontemi)
