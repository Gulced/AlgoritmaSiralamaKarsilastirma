"""500000 elemanda yalnızca dört verimli algoritmanın bağımsız süre deneyi.

Her kayıt grubu bir dağılımın dört algoritmasını içerir. Mevcut deney yöneticisi
aynı seed verisini paylaşır, her ölçümde kopya/sayaç oluşturur ve algoritma
sırasını tekrarlarla döndürür. Bir warm-up (316), beş ölçüm (317..321) vardır.
Süre yalnızca algoritma çağrısı ve sayaç maliyetidir; bellek ölçümü yapılmaz.
Her dağılım sonunda atomik kontrol noktası ve buradan üretilen CSV'ler yazılır.
Dağılım grupları arasında 1 saniye beklenir. Bir dağılım yarıda kesilirse
yalnızca o dağılım yeniden ölçülür. İki CSV birlikte atomik değildir; kontrol
noktaları sonraki başlatmada CSV'leri onarır. Eşzamanlı çalıştırma desteklenmez.
Otomatik timeout yoktur. İçe aktarma deney başlatmaz; daha büyük boyut yoktur.
"""

import argparse
import json
from pathlib import Path
import time

from deneyler.deney_yoneticisi import deneyCalistir
from deneyler.kayit import HAM_ALANLAR, OZET_ALANLAR
from deneyler.tam_deney import _atomik_yaz, _csv_metni, _grup_gecerli


BOYUT = 500000
ALGORITMALAR = ("shell", "quick", "merge", "heap")
VERI_TIPLERI = ("rastgele", "sirali", "ters_sirali", "kismen_sirali")
OLCUM_AYARLARI = {"shell_gap_yontemi": "klasik", "quick_pivot_yontemi": "orta",
                  "ana_seed": 317, "tekrar_sayisi": 5, "isinma_seed": 316}
VARSAYILAN_KLASOR = Path(__file__).resolve().parents[1] / "sonuclar/bonuslar"


def _sonuc_basarili(sonuc, veri_tipi):
    if len(sonuc["ham_sonuclar"]) != 20 or len(sonuc["ozet_sonuclar"]) != 4:
        return False
    for ad in ALGORITMALAR:
        alt_sonuc = {
            "ham_sonuclar": [s for s in sonuc["ham_sonuclar"] if s["algoritma"] == ad],
            "ozet_sonuclar": [s for s in sonuc["ozet_sonuclar"] if s["algoritma"] == ad],
            "isinma_sonuclari": sonuc["isinma_sonuclari"],
        }
        if not _grup_gecerli(alt_sonuc, BOYUT, veri_tipi, ad):
            return False
    return True


def _kontrol_noktalarini_oku(klasor):
    kayitlar = {}
    for tip in VERI_TIPLERI:
        yol = klasor / "buyuk_veri_kontrol_noktalari" / f"{BOYUT}_{tip}.json"
        if yol.exists():
            kayit = json.loads(yol.read_text(encoding="utf-8"))
            if kayit["surum"] != 1 or kayit["boyut"] != BOYUT or kayit["olcum_ayarlari"] != OLCUM_AYARLARI:
                raise ValueError(f"Uyumsuz büyük veri kontrol noktası: {yol}")
            kayitlar[tip] = kayit["sonuc"]
    return kayitlar


def _csvleri_yaz(klasor, kayitlar):
    for ad, alanlar, anahtar in [
        ("buyuk_veri_ham.csv", HAM_ALANLAR, "ham_sonuclar"),
        ("buyuk_veri_ozet.csv", OZET_ALANLAR, "ozet_sonuclar"),
    ]:
        satirlar = [s for tip in VERI_TIPLERI if tip in kayitlar for s in kayitlar[tip][anahtar]]
        _atomik_yaz(klasor / ad, _csv_metni(alanlar, satirlar))


def buyukVeriDeneyi(veri_tipleri=VERI_TIPLERI, klasor=VARSAYILAN_KLASOR):
    tipler = tuple(veri_tipleri)
    if not tipler or any(t not in VERI_TIPLERI for t in tipler) or len(set(tipler)) != len(tipler):
        raise ValueError("Dağılımlar geçerli, tekrarsız ve boş olmayan bir liste olmalıdır.")
    klasor = Path(klasor)
    kayitlar = _kontrol_noktalarini_oku(klasor)
    if kayitlar:
        _csvleri_yaz(klasor, kayitlar)
    elif any((klasor / ad).exists() for ad in ("buyuk_veri_ham.csv", "buyuk_veri_ozet.csv")):
        raise FileExistsError("Kontrol noktası olmayan büyük veri CSV'si mevcut; dosyalar korunuyor.")
    for sira, tip in enumerate(tipler):
        if tip in kayitlar and _sonuc_basarili(kayitlar[tip], tip):
            print(f"ATLANDI: {tip}, n={BOYUT}; dört algoritma daha önce başarılı", flush=True)
            continue
        print(f"BÜYÜK VERİ BAŞLADI: {tip}, n={BOYUT}; shell/klasik, quick/orta, merge, heap; "
              "bir warm-up + beş tekrar; timeout yok", flush=True)
        baslangic = time.perf_counter_ns()
        sonuc = deneyCalistir(BOYUT, tip, tekrar_sayisi=5, ana_seed=317,
                              algoritmalar=list(ALGORITMALAR))
        gecen_ns = time.perf_counter_ns() - baslangic
        kayit = dict(surum=1, boyut=BOYUT, olcum_ayarlari=OLCUM_AYARLARI,
                     grup_duvar_suresi_ns=gecen_ns, sonuc=sonuc)
        yol = klasor / "buyuk_veri_kontrol_noktalari" / f"{BOYUT}_{tip}.json"
        _atomik_yaz(yol, json.dumps(kayit, ensure_ascii=False))
        kayitlar[tip] = sonuc
        _csvleri_yaz(klasor, kayitlar)
        basarili = sum(s["basarili_mi"] for s in sonuc["ham_sonuclar"])
        print(f"BÜYÜK VERİ BİTTİ: {tip}; başarılı ölçüm {basarili}/20; "
              f"grup başarılı={_sonuc_basarili(sonuc, tip)}; {gecen_ns / 1e9:.3f} sn", flush=True)
        if sira < len(tipler) - 1:
            time.sleep(1)
    return kayitlar


if __name__ == "__main__":
    ayristirici = argparse.ArgumentParser(description="Yalnızca 500000 eleman ve dört verimli algoritma.")
    ayristirici.add_argument("--veri-tipleri", nargs="+", choices=VERI_TIPLERI, required=True)
    ayarlar = ayristirici.parse_args()
    try:
        buyukVeriDeneyi(ayarlar.veri_tipleri)
    except KeyboardInterrupt:
        print("Kesildi. Tamamlanmış dağılımlar korundu; aynı komutla devam edebilirsiniz.", flush=True)
        raise SystemExit(130)
