"""Açık boyut seçimiyle, grup bazında devam edilebilir deneyler.

Her grup (boyut, dağılım, algoritma) bir warm-up ve beş ölçüm içerir.
Atomik JSON kontrol noktaları asıl kayıttır; CSV'ler bunlardan yeniden kurulur.
İki CSV birlikte atomik değildir: arada kesinti olursa sonraki başlatma onarır.
Aynı sonuç klasöründe eşzamanlı çalıştırma desteklenmez. Gerçek timeout yoktur.
"""

import argparse
import csv
import io
import json
import os
from pathlib import Path
import tempfile
import time

from deneyler.deney_yoneticisi import deneyCalistir
from deneyler.kayit import HAM_ALANLAR, OZET_ALANLAR
from deneyler.olcum import ALGORITMALAR


BOYUTLAR = (100, 1000, 5000, 10000, 50000, 100000)
VERI_TIPLERI = ("rastgele", "sirali", "ters_sirali", "kismen_sirali")
VARSAYILAN_KLASOR = Path(__file__).resolve().parents[1] / "sonuclar/deneyler"


def _atomik_yaz(yol, metin):
    yol.parent.mkdir(parents=True, exist_ok=True)
    gecici_yol = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                         dir=yol.parent, delete=False, suffix=".tmp") as dosya:
            gecici_yol = Path(dosya.name)
            dosya.write(metin)
            dosya.flush()
            os.fsync(dosya.fileno())
        os.replace(gecici_yol, yol)
    finally:
        if gecici_yol is not None:
            gecici_yol.unlink(missing_ok=True)


def _csv_metni(alanlar, satirlar):
    metin = io.StringIO(newline="")
    yazici = csv.DictWriter(metin, fieldnames=alanlar)
    yazici.writeheader()
    for satir in satirlar:
        yazici.writerow({alan: format(deger, ".9f") if isinstance(deger, float)
                         else deger for alan, deger in satir.items()})
    return metin.getvalue()


def _grup_gecerli(sonuc, boyut, tip, ad):
    ham = sonuc["ham_sonuclar"]
    ozet = sonuc["ozet_sonuclar"]
    return (len(ham) == 5 and len(ozet) == 1
            and {(s["tekrar"], s["seed"]) for s in ham}
            == {(i, 316 + i) for i in range(1, 6)}
            and all(s["algoritma"] == ad and s["boyut"] == boyut
                    and s["veri_tipi"] == tip and s["basarili_mi"] is True
                    and s["sirali_mi"] is True and s["eleman_butunlugu"] is True for s in ham)
            and ozet[0]["algoritma"] == ad and ozet[0]["boyut"] == boyut
            and ozet[0]["veri_tipi"] == tip and ozet[0]["tekrar_sayisi"] == 5
            and ozet[0]["basarili_mi"] is True
            and sonuc["isinma_sonuclari"][ad]["basarili"] is True)


def _kayitlari_oku(klasor, boyut):
    kayitlar = {}
    for tip in VERI_TIPLERI:
        for ad in ALGORITMALAR:
            yol = klasor / "kontrol_noktalari" / f"{boyut}_{tip}_{ad}.json"
            if yol.exists():
                # Bozuk JSON/dosya hataları gizlenmez; sağlam kayıtlar korunur.
                kayit = json.loads(yol.read_text(encoding="utf-8"))
                if kayit["surum"] != 1:
                    raise ValueError(f"Desteklenmeyen kontrol noktası: {yol}")
                kayitlar[tip, ad] = kayit["sonuc"]
    return kayitlar


def _csvleri_kaydet(klasor, boyut, kayitlar):
    ham = [s for sonuc in kayitlar.values() for s in sonuc["ham_sonuclar"]]
    ozet = [s for sonuc in kayitlar.values() for s in sonuc["ozet_sonuclar"]]
    _atomik_yaz(klasor / f"ham_{boyut}.csv", _csv_metni(HAM_ALANLAR, ham))
    _atomik_yaz(klasor / f"ozet_{boyut}.csv", _csv_metni(OZET_ALANLAR, ozet))


def asamaliDeney(boyutlar, algoritmalar=None, klasor=VARSAYILAN_KLASOR,
                 bekleme=0.1, yeniden=False):
    boyutlar = list(boyutlar)
    adlar = list(ALGORITMALAR) if algoritmalar is None else list(algoritmalar)
    if not boyutlar or any(type(n) is not int or n not in BOYUTLAR for n in boyutlar):
        raise ValueError("Geçersiz veya boş boyut seçimi.")
    if len(set(boyutlar)) != len(boyutlar):
        raise ValueError("Boyutlar tekrarlanmamalıdır.")
    if not adlar or any(ad not in ALGORITMALAR for ad in adlar) or len(set(adlar)) != len(adlar):
        raise ValueError("Geçersiz veya tekrarlı algoritma seçimi.")
    if not isinstance(bekleme, (int, float)) or not 0 <= bekleme < float("inf"):
        raise ValueError("Bekleme sonlu ve negatif olmayan saniye olmalıdır.")
    klasor = Path(klasor)
    for boyut in boyutlar:
        kayitlar = _kayitlari_oku(klasor, boyut)
        if kayitlar:
            _csvleri_kaydet(klasor, boyut, kayitlar)
        for tip in VERI_TIPLERI:
            for ad in adlar:
                onceki = kayitlar.get((tip, ad))
                if not yeniden and onceki is not None and _grup_gecerli(onceki, boyut, tip, ad):
                    print(f"ATLANDI (tamamlanmış): {ad}, {tip}, n={boyut}", flush=True)
                    continue
                print(f"BAŞLADI: {ad}, {tip}, n={boyut}; 1 warm-up + 5 ölçüm; timeout yok", flush=True)
                baslangic = time.perf_counter()
                sonuc = deneyCalistir(boyut, tip, tekrar_sayisi=5, ana_seed=317, algoritmalar=[ad])
                yol = klasor / "kontrol_noktalari" / f"{boyut}_{tip}_{ad}.json"
                _atomik_yaz(yol, json.dumps({"surum": 1, "sonuc": sonuc}, ensure_ascii=False))
                kayitlar[tip, ad] = sonuc
                _csvleri_kaydet(klasor, boyut, kayitlar)
                basarili = sum(s["basarili_mi"] for s in sonuc["ham_sonuclar"])
                durum = "BAŞARILI" if _grup_gecerli(sonuc, boyut, tip, ad) else "BAŞARISIZ/EKSİK"
                print(f"BİTTİ: {ad}, {tip}, n={boyut}; {time.perf_counter() - baslangic:.3f} sn; "
                      f"başarılı tekrar {basarili}/5; {durum}", flush=True)
                time.sleep(bekleme)


def komutSatiri(argv=None):
    ayristirici = argparse.ArgumentParser(description="Yalnızca açıkça seçilen boyutları çalıştırır; timeout yok.")
    ayristirici.add_argument("--boyutlar", nargs="+", type=int, choices=BOYUTLAR, required=True)
    ayristirici.add_argument("--algoritmalar", nargs="+", choices=list(ALGORITMALAR))
    ayristirici.add_argument("--bekleme", type=float, default=0.1, help="Gruplar arası saniye")
    ayristirici.add_argument("--yeniden", action="store_true", help="Seçilen grupları yeniden ölç ve değiştir")
    ayarlar = ayristirici.parse_args(argv)
    print("Büyük boyutlar özellikle karesel algoritmalarda uzun sürebilir. Ctrl+C ile durdurulabilir.", flush=True)
    try:
        asamaliDeney(ayarlar.boyutlar, ayarlar.algoritmalar,
                     bekleme=ayarlar.bekleme, yeniden=ayarlar.yeniden)
    except KeyboardInterrupt:
        print("Kesildi. Tamamlanan gruplar korundu; aynı komutla devam edebilirsiniz.", flush=True)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(komutSatiri())
