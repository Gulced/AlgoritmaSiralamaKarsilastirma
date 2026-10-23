import random


def veriUret(boyut, veri_tipi, seed=317):
    """0..boyut-1 değerlerinden bağımsız, tekrar üretilebilir bir liste üretir.

    Kısmi karıştırmada konum sayısı max(2, boyut // 10) olarak belirlenir.
    Bu kural yalnızca boyut >= 2 iken uygulanır.
    """
    if boyut < 0:
        raise ValueError("Boyut negatif olamaz.")
    if veri_tipi not in ("rastgele", "sirali", "ters_sirali", "kismen_sirali"):
        raise ValueError(f"Bilinmeyen veri tipi: {veri_tipi}")

    if veri_tipi == "ters_sirali":
        return list(range(boyut - 1, -1, -1))

    dizi = list(range(boyut))
    uretec = random.Random(seed)

    if veri_tipi == "rastgele":
        # Fisher–Yates: her elemanı kalan bölümden seçilen bir konumla değiştir.
        for indeks in range(boyut - 1, 0, -1):
            secilen = uretec.randrange(indeks + 1)
            dizi[indeks], dizi[secilen] = dizi[secilen], dizi[indeks]
    elif veri_tipi == "kismen_sirali" and boyut >= 2:
        konum_sayisi = max(2, boyut // 10)
        konumlar = uretec.sample(range(boyut), konum_sayisi)
        # Seçilen benzersiz konumlarda döngüsel kaydırma her değeri değiştirir;
        # diğer konumlara dokunulmaz. Küçük dizilerde en az iki konum seçilir.
        gecici = dizi[konumlar[-1]]
        for sira in range(konum_sayisi - 1, 0, -1):
            dizi[konumlar[sira]] = dizi[konumlar[sira - 1]]
        dizi[konumlar[0]] = gecici

    return dizi
