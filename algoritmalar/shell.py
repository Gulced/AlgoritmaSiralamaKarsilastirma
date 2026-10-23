def klasik_gapler(dizi_uzunlugu):
    """Klasik yarıya bölme yöntemiyle azalan aralıkları üretir."""
    araliklar = []
    aralik = dizi_uzunlugu // 2
    while aralik > 0:
        araliklar.append(aralik)
        aralik //= 2
    return araliklar


def knuth_gapler(dizi_uzunlugu):
    """n'den küçük 1, 4, 13, ... aralıklarını büyükten küçüğe döndürür."""
    araliklar = []
    aralik = 1
    while aralik < dizi_uzunlugu:
        araliklar.append(aralik)
        aralik = 3 * aralik + 1
    araliklar.reverse()
    return araliklar


def shellSort(dizi, sayaclar, gap_yontemi="klasik"):
    """Her aralıkta kaydırmalı eklemeli sıralama yapar; diziyi yerinde değiştirir."""
    if gap_yontemi == "klasik":
        araliklar = klasik_gapler(len(dizi))
    elif gap_yontemi == "knuth":
        araliklar = knuth_gapler(len(dizi))
    else:
        raise ValueError("Geçersiz gap yöntemi: 'klasik' veya 'knuth' seçin.")
    for aralik in araliklar:
        for indeks in range(aralik, len(dizi)):
            gecici = dizi[indeks]
            sayaclar.hareket_sayisi += 1
            sol_indeks = indeks - aralik

            while sol_indeks >= 0:
                # Başarısız son değer karşılaştırması da sayılır.
                sayaclar.karsilastirma_sayisi += 1
                if dizi[sol_indeks] <= gecici:
                    break
                dizi[sol_indeks + aralik] = dizi[sol_indeks]
                sayaclar.hareket_sayisi += 1
                sol_indeks -= aralik

            # Geçiciye alma gibi son yerleştirme de bir harekettir.
            dizi[sol_indeks + aralik] = gecici
            sayaclar.hareket_sayisi += 1
