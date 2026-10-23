"""Farklı seed'leri koordine eder; çağrılmadıkça deney başlatmaz."""

from cekirdek.veri_uretimi import veriUret
from deneyler.olcum import ALGORITMALAR, tekOlcum


def deneyCalistir(boyut, veri_tipi, tekrar_sayisi=5, ana_seed=317, algoritmalar=None):
    if type(boyut) is not int or boyut not in (100, 1000, 5000, 10000, 50000, 100000, 500000):
        raise ValueError("Desteklenmeyen boyut; 100, 1000, 5000, 10000, 50000, 100000 veya 500000 seçin.")
    if veri_tipi not in ("rastgele", "sirali", "ters_sirali", "kismen_sirali"):
        raise ValueError("Geçersiz veri tipi.")
    if type(tekrar_sayisi) is not int or tekrar_sayisi <= 0:
        raise ValueError("Tekrar sayısı pozitif bir tam sayı olmalıdır.")
    if type(ana_seed) is not int:
        raise ValueError("Ana seed bir tam sayı olmalıdır.")
    if algoritmalar is not None and not isinstance(algoritmalar, (list, tuple)):
        raise ValueError("Algoritmalar bir liste veya demet olmalıdır.")
    adlar = list(ALGORITMALAR) if algoritmalar is None else list(algoritmalar)
    if not adlar or any(not isinstance(ad, str) or ad not in ALGORITMALAR for ad in adlar):
        raise ValueError("Geçersiz algoritma adı veya boş algoritma listesi.")
    if len(set(adlar)) != len(adlar):
        raise ValueError("Algoritma adları tekrarlanmamalıdır.")
    if boyut == 500000 and any(ad not in ("shell", "quick", "merge", "heap") for ad in adlar):
        raise ValueError("500000 boyutunda yalnızca shell, quick, merge ve heap desteklenir.")

    # Hazırlık girdisinin seed'i gerçek tekrarların dışındadır.
    isinma_verisi = veriUret(boyut, veri_tipi, ana_seed - 1)
    isinmalar = {ad: tekOlcum(ad, isinma_verisi) for ad in adlar}
    ham_sonuclar = []
    for tekrar in range(tekrar_sayisi):
        seed = ana_seed + tekrar
        baslangic_dizisi = veriUret(boyut, veri_tipi, seed)
        # İlk çalışan algoritma deterministik döner; zamanlama yanlılığı azaltılır.
        kayma = tekrar % len(adlar)
        sira = adlar[kayma:] + adlar[:kayma]
        for ad in sira:
            sonuc = tekOlcum(ad, baslangic_dizisi)
            ham_sonuclar.append({
                "algoritma": ad, "veri_tipi": veri_tipi, "boyut": boyut,
                "seed": seed, "tekrar": tekrar + 1,
                "sure_ns": sonuc["sure_ns"], "sure_ms": sonuc["sure_ns"] / 1_000_000,
                "karsilastirma_sayisi": sonuc["karsilastirma_sayisi"],
                "hareket_sayisi": sonuc["hareket_sayisi"],
                "sirali_mi": sonuc["sirali"],
                "eleman_butunlugu": sonuc["eleman_butunlugu"],
                "basarili_mi": sonuc["basarili"],
            })

    ozet_sonuclar = []
    for ad in adlar:
        kayitlar = [satir for satir in ham_sonuclar if satir["algoritma"] == ad]
        basarililar = [satir for satir in kayitlar if satir["basarili_mi"]]

        def ortalama(alan):
            return (sum(satir[alan] for satir in basarililar) / len(basarililar)
                    if basarililar else None)

        ozet_sonuclar.append({
            "algoritma": ad, "veri_tipi": veri_tipi, "boyut": boyut,
            "tekrar_sayisi": tekrar_sayisi,
            "ortalama_sure_ms": ortalama("sure_ms"),
            "ortalama_karsilastirma": ortalama("karsilastirma_sayisi"),
            "ortalama_hareket": ortalama("hareket_sayisi"),
            "basarili_mi": isinmalar[ad]["basarili"] and len(basarililar) == tekrar_sayisi,
        })
    return {"ham_sonuclar": ham_sonuclar, "ozet_sonuclar": ozet_sonuclar,
            "isinma_sonuclari": isinmalar}
