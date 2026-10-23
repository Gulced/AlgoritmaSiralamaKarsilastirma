"""Kontrollü ön ölçüm ve matematiksel süre projeksiyonu.

Tahminler garanti değildir. Tek ölçüm, Python/sayaç maliyeti ve zamanlama
gürültüsünü içerir; warm-up ve tekrar yapılmaz. Büyük boyutlar çalıştırılmaz.
CLI ölçümleri ayrı süreçte yapar. Gerçek timeout veya tahmine göre atlama
uygulanmaz; Ctrl+C çalışan süreci sonlandırır. 5000 için açık seçenek gerekir.

Selection/Bubble için karesel projeksiyon kullanılır; erken duran sıralı
Bubble'da bu özellikle muhafazakâr olabilir. Insertion sıralıda doğrusal,
kısmen sıralıda ölçülen büyüme ile modellenir; %10 değişim az kaydırma
garantilemez. Quick'in n log n modeli en kötü durum garantisi değildir.
Shell ve kısmi Insertion'ın iki noktalı üssü gürültüye çok duyarlıdır;
ilk ölçümde yeterli veri yoksa bu tahminler boş bırakılır. Büyük boyutlara
uzun ekstrapolasyon ve tek seed sonuçları deney planlama ipucudur.
"""

import argparse
import csv
import math
import multiprocessing
from pathlib import Path

from cekirdek.veri_uretimi import veriUret
from deneyler.olcum import ALGORITMALAR, tekOlcum


VERI_TIPLERI = ("rastgele", "sirali", "ters_sirali", "kismen_sirali")
CSV_ALANLAR = ["algoritma", "veri_tipi", "olculen_boyut", "olculen_sure_ns",
              "olculen_sure_ms", "tahmin_10000_ms", "tahmin_50000_ms",
              "tahmin_100000_ms", "tahmin_yontemi", "deger_turu", "basarili_mi"]


def tahminUret(algoritma, veri_tipi, boyut, sure_ns, onceki_olcum=None):
    """Son ölçümü referans alır; Shell/kısmi insertion için iki nokta kullanır."""
    if algoritma not in ALGORITMALAR:
        raise ValueError("Geçersiz algoritma adı.")
    if veri_tipi not in VERI_TIPLERI:
        raise ValueError("Geçersiz veri tipi.")
    if type(boyut) is not int or boyut not in (100, 1000, 5000):
        raise ValueError("Ölçülen boyut 100, 1000 veya 5000 olmalıdır.")
    if not math.isfinite(sure_ns) or sure_ns < 0:
        raise ValueError("Süre sonlu ve negatif olmayan bir sayı olmalıdır.")

    if algoritma in ("quick", "merge", "heap"):
        yontem = "n log2(n) projeksiyonu"

        def oran(hedef):
            return hedef * math.log2(hedef) / (boyut * math.log2(boyut))
    else:
        us = 2
        yontem = "n² projeksiyonu"
        if algoritma == "insertion" and veri_tipi == "sirali":
            us = 1
            yontem = "sıralı insertion: doğrusal projeksiyon"
        elif algoritma == "shell" or (algoritma == "insertion" and veri_tipi == "kismen_sirali"):
            # Küçük ölçüm gürültüsünü karmaşıklık garantisine dönüştürme.
            if onceki_olcum is None or sure_ns == 0 or onceki_olcum[1] <= 0:
                us = None
                yontem = "ölçülen büyüme için iki pozitif süre gerekli"
            else:
                onceki_boyut, onceki_sure = onceki_olcum
                if not 0 < onceki_boyut < boyut or not math.isfinite(onceki_sure):
                    raise ValueError("Önceki ölçüm daha küçük boyut ve sonlu pozitif süre içermelidir.")
                us = math.log(sure_ns / onceki_sure) / math.log(boyut / onceki_boyut)
                yontem = f"ölçülen büyüme üssü p={us:.4f}; karmaşıklık garantisi değil"

        def oran(hedef):
            return (hedef / boyut) ** us if us is not None else None

    sonuc = {"algoritma": algoritma, "veri_tipi": veri_tipi,
             "olculen_boyut": boyut, "olculen_sure_ns": sure_ns,
             "olculen_sure_ms": sure_ns / 1_000_000,
             "tahmin_yontemi": yontem,
             "deger_turu": "ölçülen referans ve matematiksel tahminler"}
    for hedef in (10000, 50000, 100000):
        carpan = oran(hedef)
        sonuc[f"tahmin_{hedef}_ms"] = sure_ns / 1_000_000 * carpan if carpan is not None else None
    return sonuc


def _kombinasyon_olc(gorev):
    boyut, veri_tipi, seed = gorev
    dizi = veriUret(boyut, veri_tipi, seed)
    sonuclar = []
    for ad in ALGORITMALAR:
        print(f"BAŞLADI: {ad}, {veri_tipi}, n={boyut}", flush=True)
        sonuc = tekOlcum(ad, dizi)
        sonuclar.append((ad, veri_tipi, boyut, sonuc))
        print(f"BİTTİ: {ad}, {sonuc['sure_ns'] / 1e6:.3f} ms, başarılı={sonuc['basarili']}", flush=True)
    return sonuclar


def _sureclerde_olc(boyutlar, seed):
    # Ayrı süreç: ana süreç sıralama yapmaz; Ctrl+C'de çocuk sonlandırılır.
    baglam = multiprocessing.get_context("spawn")
    havuz = baglam.Pool(processes=1)
    try:
        gorevler = [(boyut, veri_tipi, seed) for boyut in boyutlar for veri_tipi in VERI_TIPLERI]
        gruplar = havuz.map_async(_kombinasyon_olc, gorevler)
        while True:
            try:
                sonuc = gruplar.get(timeout=0.5)
                break
            except multiprocessing.TimeoutError:
                # Bu yalnızca durum bekleme aralığıdır; ölçümü durduran timeout değildir.
                continue
        havuz.close()
    except BaseException:
        havuz.terminate()
        raise
    finally:
        havuz.join()
    return [satir for grup in sonuc for satir in grup]


def onAnaliz(boyutlar=(100, 1000), seed=317):
    """API'de açık boyut listesi; CLI'de 5000 yalnızca --5000-dahil ile."""
    boyutlar = tuple(boyutlar)
    if not boyutlar or any(type(n) is not int or n not in (100, 1000, 5000) for n in boyutlar):
        raise ValueError("Ön ölçüm boyutları yalnızca 100, 1000 ve 5000 olabilir.")
    if list(boyutlar) != sorted(set(boyutlar)):
        raise ValueError("Boyutlar artan ve tekrarsız olmalıdır.")
    oncekiler = {}
    tablo = []
    for ad, veri_tipi, boyut, sonuc in _sureclerde_olc(boyutlar, seed):
        anahtar = ad, veri_tipi
        satir = tahminUret(ad, veri_tipi, boyut, sonuc["sure_ns"], oncekiler.get(anahtar))
        satir["basarili_mi"] = sonuc["basarili"]
        if sonuc["basarili"]:
            oncekiler[anahtar] = boyut, sonuc["sure_ns"]
        else:
            for hedef in (10000, 50000, 100000):
                satir[f"tahmin_{hedef}_ms"] = None
            satir["tahmin_yontemi"] = "başarısız ölçüm: tahmin üretilmedi"
        tablo.append(satir)
    return tablo


def onAnalizKaydet(tablo, yol="sonuclar/on_analiz.csv"):
    yol = Path(yol)
    if yol.name in ("ham_sonuclar.csv", "ozet_sonuclar.csv"):
        raise ValueError("Mevcut deney CSV dosyaları ön analiz için kullanılamaz.")
    yol.parent.mkdir(parents=True, exist_ok=True)
    with yol.open("x", encoding="utf-8", newline="") as dosya:
        yazici = csv.DictWriter(dosya, fieldnames=CSV_ALANLAR)
        yazici.writeheader()
        yazici.writerows(tablo)


if __name__ == "__main__":
    ayristirici = argparse.ArgumentParser(description="Kaba projeksiyon; gerçek timeout yok. Ctrl+C ile durdurulabilir.")
    ayristirici.add_argument("--5000-dahil", dest="bes_bin_dahil", action="store_true", help="Uzun sürebilen n=5000 ölçümlerini açıkça etkinleştir.")
    ayarlar = ayristirici.parse_args()
    yol = Path(__file__).resolve().parents[1] / "sonuclar/on_analiz.csv"
    if yol.exists():
        raise FileExistsError("Ön analiz CSV'si mevcut; önce arşivleyin.")
    print("Her kombinasyon bir kez ölçülecek. Süre garantisi/otomatik timeout yok; büyük boyutlar yalnızca tahmin.", flush=True)
    if ayarlar.bes_bin_dahil:
        print("UYARI: n=5000 karesel algoritmalar uzun sürebilir.", flush=True)
    boyutlar = (100, 1000, 5000) if ayarlar.bes_bin_dahil else (100, 1000)
    onAnalizKaydet(onAnaliz(boyutlar), yol)
    print(f"Kaydedildi: {yol}")
