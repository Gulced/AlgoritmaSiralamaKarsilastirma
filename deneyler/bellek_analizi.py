"""Süre deneylerinden bağımsız, tracemalloc ile ek Python tahsisi ölçümü.

Girdi üretimi, çalışma kopyası ve sayaç oluşturma izleme başlamadan yapılır.
Yalnızca algoritma çağrısının tepe tahsisi alınır; doğrulama izleme dışındadır.
Sonuç toplam RAM/RSS değildir; yardımcı alanın kesin matematiksel karşılığı
da değildir. Liste referansları, Python tamsayıları, sayaç güncellemeleri ve
çağrı maliyetleri ölçümü etkiler. None tampon başlatması da bellek tüketir.
Mevcut tracemalloc oturumuna dokunulmaz; etkinse RuntimeError üretilir.
Bu modül eşzamanlı bellek ölçümleri için tasarlanmamıştır.
"""

import csv
from collections import Counter
from pathlib import Path
import tracemalloc

from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar
from cekirdek.veri_uretimi import veriUret
from deneyler.olcum import ALGORITMALAR


VERI_TIPLERI = ("rastgele", "sirali", "ters_sirali", "kismen_sirali")
TEORIK_EK_ALAN = {
    "selection": "O(1)",
    "insertion": "O(1)",
    "bubble": "O(1)",
    # Mevcut klasik_gapler tüm gap'leri listeler; O(1) iddiası bu kodda geçersiz.
    "shell": "O(log n) gap listesi",
    "quick": "O(log n) cagri yigini ust siniri",
    "merge": "O(n) tampon + O(log n) cagri yigini",
    "heap": "O(1), yinelemeli",
}
CSV_ALANLAR = ["algoritma", "veri_tipi", "boyut", "olculen_tepe_bellek_bayt",
              "olculen_tepe_bellek_kib", "teorik_ek_alan", "basarili_mi", "olcum_yontemi"]
OLCUM_YONTEMI = "tracemalloc; algoritma ek Python tahsisi; tek calisma; seed=317; RSS degil"


def bellekOlc(algoritma_adi, baslangic_dizisi, veri_tipi):
    """Bağımsız kopyada tek bellek ölçümü; mevcut süre ölçümlerini çağırmaz."""
    if algoritma_adi not in ALGORITMALAR:
        raise ValueError("Geçersiz algoritma adı.")
    if veri_tipi not in VERI_TIPLERI:
        raise ValueError("Geçersiz veri tipi.")
    if tracemalloc.is_tracing():
        raise RuntimeError("tracemalloc zaten etkin; mevcut ölçüm korunarak işlem reddedildi.")
    dizi = baslangic_dizisi.copy()
    sayaclar = Sayaclar()
    algoritma = ALGORITMALAR[algoritma_adi]

    tracemalloc.start(1)
    try:
        algoritma(dizi, sayaclar)
        _, tepe = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    sirali = isSorted(dizi)
    farklar = Counter(baslangic_dizisi)
    farklar.subtract(dizi)
    eleman_butunlugu = all(fark == 0 for fark in farklar.values())
    return {
        "algoritma": algoritma_adi, "veri_tipi": veri_tipi,
        "boyut": len(baslangic_dizisi), "olculen_tepe_bellek_bayt": tepe,
        "olculen_tepe_bellek_kib": tepe / 1024,
        "teorik_ek_alan": TEORIK_EK_ALAN[algoritma_adi],
        "basarili_mi": sirali and eleman_butunlugu,
        "olcum_yontemi": OLCUM_YONTEMI,
        "sirali_mi": sirali, "eleman_butunlugu": eleman_butunlugu,
    }


def kontrolluBellekDeneyi():
    """1000'de tümü, 10000'de yalnızca dört algoritma; kombinasyon başına 1 ölçüm."""
    sonuclar = []
    for boyut in (1000, 10000):
        adlar = list(ALGORITMALAR) if boyut == 1000 else ["shell", "quick", "merge", "heap"]
        for veri_tipi in VERI_TIPLERI:
            dizi = veriUret(boyut, veri_tipi, seed=317)
            for ad in adlar:
                print(f"BELLEK BAŞLADI: {ad}, {veri_tipi}, n={boyut}", flush=True)
                sonuc = bellekOlc(ad, dizi, veri_tipi)
                sonuclar.append(sonuc)
                print(f"BELLEK BİTTİ: {sonuc['olculen_tepe_bellek_bayt']} bayt; "
                      f"başarılı={sonuc['basarili_mi']}", flush=True)
    return sonuclar


def bellekCsvKaydet(sonuclar, yol="sonuclar/bellek_sonuclari.csv"):
    yol = Path(yol)
    if yol.name != "bellek_sonuclari.csv":
        raise ValueError("Bellek çıktısının adı bellek_sonuclari.csv olmalıdır.")
    yol.parent.mkdir(parents=True, exist_ok=True)
    # Mevcut çıktı dahil hiçbir dosyanın üzerine yazılmaz.
    with yol.open("x", encoding="utf-8", newline="") as dosya:
        yazici = csv.DictWriter(dosya, fieldnames=CSV_ALANLAR)
        yazici.writeheader()
        for sonuc in sonuclar:
            satir = {alan: sonuc[alan] for alan in CSV_ALANLAR}
            satir["olculen_tepe_bellek_kib"] = format(satir["olculen_tepe_bellek_kib"], ".6f")
            yazici.writerow(satir)


if __name__ == "__main__":
    yol = Path(__file__).resolve().parents[1] / "sonuclar/bellek_sonuclari.csv"
    if yol.exists():
        raise FileExistsError("Bellek sonuçları mevcut; önce arşivleyin.")
    print("tracemalloc yavaşlatır; karesel algoritmalar yalnızca n=1000'de çalışacak.", flush=True)
    sonuclar = kontrolluBellekDeneyi()
    bellekCsvKaydet(sonuclar, yol)
    print(f"Kaydedildi: {yol}; ölçüm sayısı: {len(sonuclar)}")
