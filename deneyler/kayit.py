"""Ham ve özet sonuçları UTF-8 CSV dosyalarına kaydeder."""

import csv
from pathlib import Path


HAM_ALANLAR = ["algoritma", "veri_tipi", "boyut", "seed", "tekrar", "sure_ns",
               "sure_ms", "karsilastirma_sayisi", "hareket_sayisi", "sirali_mi",
               "eleman_butunlugu", "basarili_mi"]
OZET_ALANLAR = ["algoritma", "veri_tipi", "boyut", "tekrar_sayisi",
                "ortalama_sure_ms", "ortalama_karsilastirma", "ortalama_hareket",
                "basarili_mi"]


def csvKaydet(sonuclar, klasor="sonuclar", uzerine_yaz=False):
    """Varsayılan olarak mevcut dosyaları reddeder; satır ekleme yapmaz.

    Açıkça uzerine_yaz=True verilirse iki dosya yeniden yazılır.
    Ondalıklar nokta ayracıyla 9 basamak yazılır; tanımsız ortalama boş kalır.
    Dosya sistemi hataları çağırana iletilir.
    """
    klasor = Path(klasor)
    klasor.mkdir(parents=True, exist_ok=True)
    ham_yolu = klasor / "ham_sonuclar.csv"
    ozet_yolu = klasor / "ozet_sonuclar.csv"
    if not uzerine_yaz and (ham_yolu.exists() or ozet_yolu.exists()):
        raise FileExistsError("Sonuç dosyası mevcut; başka klasör seçin veya uzerine_yaz=True kullanın.")
    for yol, alanlar, satirlar in [
        (ham_yolu, HAM_ALANLAR, sonuclar["ham_sonuclar"]),
        (ozet_yolu, OZET_ALANLAR, sonuclar["ozet_sonuclar"]),
    ]:
        with yol.open("w" if uzerine_yaz else "x", encoding="utf-8", newline="") as dosya:
            yazici = csv.DictWriter(dosya, fieldnames=alanlar)
            yazici.writeheader()
            for satir in satirlar:
                yazici.writerow({alan: format(deger, ".9f") if isinstance(deger, float)
                                 else deger for alan, deger in satir.items()})
    return ham_yolu, ozet_yolu
