"""Aynı Quick Sort'ta yalnızca pivot yöntemini değiştirerek karşılaştırma.

Bir hazırlık (seed=316) ve beş gerçek tekrar (317..321) uygulanır.
Her seed için tek veri üretilir; iki yöntem ayrı kopya/sayaç alır.
Önce çalışan yöntem tekrarlar arasında döner. Süre yalnızca algoritma çağrısı
ve mevcut sayaç maliyetidir; kopyalama, üretim, doğrulama ve kayıt dışarıdadır.
İlk pivot sıralı/ters sıralı veride O(n²) süreye yaklaşabilir; küçük parçaya
özyineleme yığın alanını sınırlar, karesel çalışma süresini ortadan kaldırmaz.
Varsayılan yalnızca 100/1000'dir. Gerçek timeout yoktur; büyük boyutlar açıktır.
"""

import argparse
from collections import Counter
import csv
from pathlib import Path
import time

from algoritmalar.quick import quickSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar
from cekirdek.veri_uretimi import veriUret


PIVOTLAR = ("orta", "ilk")
VERI_TIPLERI = ("rastgele", "sirali", "ters_sirali", "kismen_sirali")
HAM_ALANLAR = ["pivot_yontemi", "veri_tipi", "boyut", "seed", "tekrar",
               "sure_ns", "sure_ms", "karsilastirma_sayisi", "hareket_sayisi",
               "sirali_mi", "eleman_butunlugu", "basarili_mi"]
OZET_ALANLAR = ["pivot_yontemi", "veri_tipi", "boyut", "tekrar_sayisi",
                "basarili_tekrar_sayisi", "ortalama_sure_ms",
                "ortalama_karsilastirma", "ortalama_hareket", "basarili_mi"]


def pivotOlcum(pivot_yontemi, baslangic_dizisi):
    if pivot_yontemi not in PIVOTLAR:
        raise ValueError("Geçersiz pivot yöntemi.")
    dizi = baslangic_dizisi.copy()
    sayaclar = Sayaclar()
    baslangic = time.perf_counter_ns()
    quickSort(dizi, sayaclar, pivot_yontemi=pivot_yontemi)
    bitis = time.perf_counter_ns()
    sirali = isSorted(dizi)
    farklar = Counter(baslangic_dizisi)
    farklar.subtract(dizi)
    butunluk = all(fark == 0 for fark in farklar.values())
    return dict(sure_ns=bitis - baslangic, sure_ms=(bitis - baslangic) / 1e6,
                karsilastirma_sayisi=sayaclar.karsilastirma_sayisi,
                hareket_sayisi=sayaclar.hareket_sayisi,
                sirali_mi=sirali, eleman_butunlugu=butunluk,
                basarili_mi=sirali and butunluk)


def pivotDeneyi(boyutlar=(100, 1000)):
    boyutlar = tuple(boyutlar)
    if (not boyutlar or any(type(n) is not int or n not in (100, 1000, 5000, 10000) for n in boyutlar)
            or len(set(boyutlar)) != len(boyutlar)):
        raise ValueError("Boyutlar tekrarsız olarak 100, 1000, 5000 veya 10000 seçilmelidir.")
    ham_sonuclar = []
    ozet_sonuclar = []
    isinmalar = []
    for boyut in boyutlar:
        for tip in VERI_TIPLERI:
            print(f"PIVOT BAŞLADI: n={boyut}, {tip}; iki yöntem, warm-up + 5 tekrar", flush=True)
            hazirlik = veriUret(boyut, tip, seed=316)
            isinma = {p: pivotOlcum(p, hazirlik) for p in PIVOTLAR}
            isinmalar.append(dict(boyut=boyut, veri_tipi=tip, sonuclar=isinma))
            grup = []
            for tekrar in range(5):
                seed = 317 + tekrar
                dizi = veriUret(boyut, tip, seed=seed)
                sira = PIVOTLAR if tekrar % 2 == 0 else PIVOTLAR[::-1]
                for pivot in sira:
                    sonuc = pivotOlcum(pivot, dizi)
                    grup.append(dict(pivot_yontemi=pivot, veri_tipi=tip,
                                     boyut=boyut, seed=seed, tekrar=tekrar + 1, **sonuc))
            ham_sonuclar.extend(grup)
            for pivot in PIVOTLAR:
                basarililar = [s for s in grup if s["pivot_yontemi"] == pivot and s["basarili_mi"]]

                def ortalama(alan):
                    return sum(s[alan] for s in basarililar) / len(basarililar) if basarililar else None

                ozet_sonuclar.append(dict(
                    pivot_yontemi=pivot, veri_tipi=tip, boyut=boyut,
                    tekrar_sayisi=5, basarili_tekrar_sayisi=len(basarililar),
                    ortalama_sure_ms=ortalama("sure_ms"),
                    ortalama_karsilastirma=ortalama("karsilastirma_sayisi"),
                    ortalama_hareket=ortalama("hareket_sayisi"),
                    basarili_mi=len(basarililar) == 5 and isinma[pivot]["basarili_mi"]))
            print(f"PIVOT BİTTİ: n={boyut}, {tip}; başarılı gerçek ölçüm "
                  f"{sum(s['basarili_mi'] for s in grup)}/10", flush=True)
    return dict(ham_sonuclar=ham_sonuclar, ozet_sonuclar=ozet_sonuclar, isinma_sonuclari=isinmalar)


def pivotCsvKaydet(sonuclar, klasor="sonuclar/bonuslar"):
    """Satır eklemez; dosyalardan biri mevcutsa ikisini de koruyarak reddeder."""
    klasor = Path(klasor)
    yollar = (klasor / "pivot_ham.csv", klasor / "pivot_ozet.csv")
    if any(yol.exists() for yol in yollar):
        raise FileExistsError("Pivot sonuçları mevcut; farklı çıktı klasörü seçin.")
    klasor.mkdir(parents=True, exist_ok=True)
    for yol, alanlar, satirlar in [
        (yollar[0], HAM_ALANLAR, sonuclar["ham_sonuclar"]),
        (yollar[1], OZET_ALANLAR, sonuclar["ozet_sonuclar"]),
    ]:
        with yol.open("x", encoding="utf-8", newline="") as dosya:
            yazici = csv.DictWriter(dosya, fieldnames=alanlar)
            yazici.writeheader()
            for satir in satirlar:
                yazici.writerow({alan: format(deger, ".9f") if isinstance(deger, float)
                                 else deger for alan, deger in satir.items()})
    return yollar


if __name__ == "__main__":
    ayristirici = argparse.ArgumentParser(description="Quick Sort pivot karşılaştırması; otomatik timeout yok.")
    ayristirici.add_argument("--boyutlar", nargs="+", type=int, choices=(100, 1000, 5000, 10000), default=[100, 1000])
    ayristirici.add_argument("--cikti", type=Path,
                           default=Path(__file__).resolve().parents[1] / "sonuclar/bonuslar")
    ayarlar = ayristirici.parse_args()
    if any((ayarlar.cikti / ad).exists() for ad in ("pivot_ham.csv", "pivot_ozet.csv")):
        raise FileExistsError("Pivot çıktıları mevcut; ayrı klasör için --cikti kullanın.")
    print("İlk pivot sıralı/ters sıralı girdilerde uzun sürebilir. Süreler gerçek ölçümdür.", flush=True)
    sonuc = pivotDeneyi(ayarlar.boyutlar)
    for yol in pivotCsvKaydet(sonuc, ayarlar.cikti):
        print(yol)
