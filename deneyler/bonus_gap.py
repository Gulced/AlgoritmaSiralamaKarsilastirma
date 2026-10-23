"""Shell Sort'ta klasik ve Knuth aralıklarının adil karşılaştırması.

İki yöntem de gap listesini algoritma çağrısı içinde üretir; bu maliyet ve
sayaç artırımları süreye dahildir. Veri üretimi, kopyalama, sayaç oluşturma,
doğrulama ve CSV kaydı dışarıdadır. Seed=316 hazırlık, 317..321 gerçek tekrardır.
Yöntemlerin sırası tekrarlarla ve dağılımlarla dönüşümlü başlatılır. Beş tekrar
tek sayıdır: bir grupta 3/2, sonraki grupta 2/3 ilk çalışma sırası kullanılır.
Gap listeleri iki yöntemde de O(log n) ek alan kullanır; O(1) iddiası yapılmaz.
"""

from collections import Counter
import csv
from pathlib import Path
import time

from algoritmalar.shell import shellSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar
from cekirdek.veri_uretimi import veriUret


GAP_YONTEMLERI = ("klasik", "knuth")
VERI_TIPLERI = ("rastgele", "sirali", "ters_sirali", "kismen_sirali")
HAM_ALANLAR = ["gap_yontemi", "algoritma", "veri_tipi", "boyut", "seed", "tekrar",
               "sure_ns", "sure_ms", "karsilastirma_sayisi", "hareket_sayisi",
               "sirali_mi", "eleman_butunlugu", "basarili_mi"]
OZET_ALANLAR = ["gap_yontemi", "algoritma", "veri_tipi", "boyut", "tekrar_sayisi",
                "basarili_tekrar_sayisi", "ortalama_sure_ms",
                "ortalama_karsilastirma", "ortalama_hareket", "basarili_mi"]


def gapOlcum(gap_yontemi, baslangic_dizisi):
    if gap_yontemi not in GAP_YONTEMLERI:
        raise ValueError("Geçersiz gap yöntemi.")
    dizi = baslangic_dizisi.copy()
    sayaclar = Sayaclar()
    baslangic = time.perf_counter_ns()
    shellSort(dizi, sayaclar, gap_yontemi=gap_yontemi)
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


def gapDeneyi(boyutlar=(100, 1000, 5000, 10000)):
    boyutlar = tuple(boyutlar)
    if (not boyutlar or any(type(n) is not int or n not in (100, 1000, 5000, 10000) for n in boyutlar)
            or len(set(boyutlar)) != len(boyutlar)):
        raise ValueError("Boyutlar tekrarsız olarak 100, 1000, 5000 veya 10000 seçilmelidir.")
    ham_sonuclar = []
    ozet_sonuclar = []
    isinmalar = []
    for boyut in boyutlar:
        for dagilim_sirasi, tip in enumerate(VERI_TIPLERI):
            print(f"GAP BAŞLADI: n={boyut}, {tip}; iki yöntem, warm-up + 5 tekrar", flush=True)
            hazirlik = veriUret(boyut, tip, seed=316)
            hazirlik_sirasi = GAP_YONTEMLERI if dagilim_sirasi % 2 == 0 else GAP_YONTEMLERI[::-1]
            isinma = {y: gapOlcum(y, hazirlik) for y in hazirlik_sirasi}
            isinmalar.append(dict(boyut=boyut, veri_tipi=tip, sonuclar=isinma))
            grup = []
            for tekrar in range(5):
                seed = 317 + tekrar
                dizi = veriUret(boyut, tip, seed=seed)
                sira = GAP_YONTEMLERI if (tekrar + dagilim_sirasi) % 2 == 0 else GAP_YONTEMLERI[::-1]
                for yontem in sira:
                    sonuc = gapOlcum(yontem, dizi)
                    grup.append(dict(gap_yontemi=yontem, algoritma="shell", veri_tipi=tip,
                                     boyut=boyut, seed=seed, tekrar=tekrar + 1, **sonuc))
            ham_sonuclar.extend(grup)
            for yontem in GAP_YONTEMLERI:
                basarililar = [s for s in grup if s["gap_yontemi"] == yontem and s["basarili_mi"]]

                def ortalama(alan):
                    return sum(s[alan] for s in basarililar) / len(basarililar) if basarililar else None

                ozet_sonuclar.append(dict(
                    gap_yontemi=yontem, algoritma="shell", veri_tipi=tip, boyut=boyut,
                    tekrar_sayisi=5, basarili_tekrar_sayisi=len(basarililar),
                    ortalama_sure_ms=ortalama("sure_ms"),
                    ortalama_karsilastirma=ortalama("karsilastirma_sayisi"),
                    ortalama_hareket=ortalama("hareket_sayisi"),
                    basarili_mi=len(basarililar) == 5 and isinma[yontem]["basarili_mi"]))
            print(f"GAP BİTTİ: n={boyut}, {tip}; başarılı gerçek ölçüm "
                  f"{sum(s['basarili_mi'] for s in grup)}/10", flush=True)
    return dict(ham_sonuclar=ham_sonuclar, ozet_sonuclar=ozet_sonuclar, isinma_sonuclari=isinmalar)


def gapCsvKaydet(sonuclar, klasor="sonuclar/bonuslar"):
    """Satır eklemez; mevcut gap dosyaları varsa üzerine yazmayı reddeder."""
    klasor = Path(klasor)
    yollar = (klasor / "gap_ham.csv", klasor / "gap_ozet.csv")
    if any(yol.exists() for yol in yollar):
        raise FileExistsError("Gap sonuçları mevcut; farklı çıktı klasörü seçin.")
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
    klasor = Path(__file__).resolve().parents[1] / "sonuclar/bonuslar"
    if any((klasor / ad).exists() for ad in ("gap_ham.csv", "gap_ozet.csv")):
        raise FileExistsError("Gap sonuçları mevcut; mevcut kayıtlar korunuyor.")
    sonuc = gapDeneyi()
    for yol in gapCsvKaydet(sonuc, klasor):
        print(yol)
