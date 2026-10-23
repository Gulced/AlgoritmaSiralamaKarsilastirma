def _birlestir(dizi, yardimci_dizi, baslangic, orta, bitis, sayaclar):
    sol = baslangic
    sag = orta
    yazma_indeksi = baslangic

    while sol < orta and sag < bitis:
        sayaclar.karsilastirma_sayisi += 1
        # Eşitlikte soldan seçmek, eşit anahtarların sırasını korur.
        if dizi[sol] <= dizi[sag]:
            yardimci_dizi[yazma_indeksi] = dizi[sol]
            sol += 1
        else:
            yardimci_dizi[yazma_indeksi] = dizi[sag]
            sag += 1
        sayaclar.hareket_sayisi += 1
        yazma_indeksi += 1

    while sol < orta:
        yardimci_dizi[yazma_indeksi] = dizi[sol]
        sayaclar.hareket_sayisi += 1
        sol += 1
        yazma_indeksi += 1

    while sag < bitis:
        yardimci_dizi[yazma_indeksi] = dizi[sag]
        sayaclar.hareket_sayisi += 1
        sag += 1
        yazma_indeksi += 1

    for indeks in range(baslangic, bitis):
        dizi[indeks] = yardimci_dizi[indeks]
        sayaclar.hareket_sayisi += 1


def _araligi_sirala(dizi, yardimci_dizi, baslangic, bitis, sayaclar):
    if bitis - baslangic <= 1:
        return
    orta = (baslangic + bitis) // 2
    _araligi_sirala(dizi, yardimci_dizi, baslangic, orta, sayaclar)
    _araligi_sirala(dizi, yardimci_dizi, orta, bitis, sayaclar)
    _birlestir(dizi, yardimci_dizi, baslangic, orta, bitis, sayaclar)


def mergeSort(dizi, sayaclar):
    """Diziyi kararlı sıralar; her yardımcı/ana dizi yazımı 1 harekettir.

    İndeks atamaları ve None ile bellek ayırma veri hareketi sayılmaz.
    Alt diziler dilimlenmez; bitiş indeksi işlenen aralığa dahil değildir.
    """
    # Tüm çağrılar aynı n elemanlı tamponu paylaşır: O(n) ek bellek.
    yardimci_dizi = [None] * len(dizi)
    _araligi_sirala(dizi, yardimci_dizi, 0, len(dizi), sayaclar)
