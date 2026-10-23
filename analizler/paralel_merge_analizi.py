"""Mevcut sıralı Merge Sort sürelerinden idealize teorik tahminler üretir.

Paralel algoritma, thread, süreç veya yeni sıralama deneyi çalıştırmaz.
Amdahl f değerleri ölçülmüş oranlar değildir; örnek varsayımlardır.
"""

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


KARMASIKLIK = {
    "sirali_is": "T1(n) = 2T1(n/2) + Theta(n) = Theta(n log n)",
    "sirali_ek_alan": "O(n) tampon + O(log n) cagri yigini = O(n)",
    "ideal_kritik_yol": "Tinf(n) = Tinf(n/2) + Theta(n) = Theta(n)",
    "ideal_paralellik": "T1(n)/Tinf(n) = Theta(log n)",
    "model": "Alt problemler paralel, her birlestirme sirali; iletisim ve gorev ek yuku yok",
}
CSV_ALANLAR = ["kayit_turu", "boyut", "veri_tipi", "paralel_oran_f", "calisan_sayisi",
              "teorik_hizlanma", "sure_ms", "referans_gercek_sure_ms", "kaynak_csv", "aciklama"]


def _sayi(deger, ad):
    if isinstance(deger, bool) or not isinstance(deger, (int, float, Decimal)):
        raise ValueError(f"{ad} sonlu bir sayı olmalıdır.")
    try:
        sonuc = Decimal(str(deger))
    except InvalidOperation as hata:
        raise ValueError(f"{ad} geçersiz.") from hata
    if not sonuc.is_finite():
        raise ValueError(f"{ad} sonlu bir sayı olmalıdır.")
    return sonuc


def _amdahl_paydasi(f, p):
    f = _sayi(f, "f")
    if not 0 <= f <= 1:
        raise ValueError("f, 0 ile 1 arasında olmalıdır.")
    if type(p) is not int or p <= 0:
        raise ValueError("p pozitif bir tam sayı olmalıdır.")
    return (1 - f) + f / p


def amdahlHizlanma(f, p):
    """S(p)=1/((1-f)+f/p); Decimal döndürür, gerçek ölçüm değildir."""
    return 1 / _amdahl_paydasi(f, p)


def teorikSure(sirali_sure_ms, f, p):
    """Ölçülen referans * ((1-f)+f/p); gerçek paralel yürütme süresi değildir."""
    sure = _sayi(sirali_sure_ms, "Süre")
    if sure < 0:
        raise ValueError("Süre negatif olamaz.")
    return sure * _amdahl_paydasi(f, p)


def mergeSureleriniOku(proje_koku):
    """Dört başarılı rastgele Merge özetini okur; kaynak ondalık metnini korur."""
    kok = Path(proje_koku)
    gercekler = []
    for boyut in (10000, 50000, 100000, 500000):
        kaynak = ("sonuclar/bonuslar/buyuk_veri_ozet.csv" if boyut == 500000
                  else f"sonuclar/deneyler/ozet_{boyut}.csv")
        with (kok / kaynak).open(encoding="utf-8", newline="") as dosya:
            rows = [s for s in csv.DictReader(dosya) if s["algoritma"] == "merge"
                    and s["veri_tipi"] == "rastgele" and int(s["boyut"]) == boyut]
        if len(rows) != 1:
            raise ValueError(f"{boyut} için tek bir Merge özeti bekleniyor.")
        row = rows[0]
        if row["basarili_mi"] != "True" or int(row["tekrar_sayisi"]) != 5:
            raise ValueError(f"{boyut} referansı beş başarılı tekrara dayanmalıdır.")
        try:
            sure = Decimal(row["ortalama_sure_ms"])
        except InvalidOperation as hata:
            raise ValueError("Kaynak süre geçersiz.") from hata
        if not sure.is_finite() or sure < 0:
            raise ValueError("Kaynak süre sonlu ve negatif olmayan sayı olmalıdır.")
        gercekler.append(dict(boyut=boyut, veri_tipi="rastgele", kaynak_csv=kaynak,
                             ortalama_sure_ms=row["ortalama_sure_ms"]))
    return gercekler


def tahminleriOlustur(gercekler, f=0.90, calisanlar=(2, 4, 8)):
    calisanlar = tuple(calisanlar)
    _amdahl_paydasi(f, 1)
    if not calisanlar or len(set(calisanlar)) != len(calisanlar):
        raise ValueError("Çalışan sayıları boş veya tekrarlı olamaz.")
    for p in calisanlar:
        _amdahl_paydasi(f, p)
    rows = []
    for gercek in gercekler:
        ham_sure = gercek["ortalama_sure_ms"]
        sure = Decimal(ham_sure)
        teorikSure(sure, f, 1)
        ortak = dict(boyut=gercek["boyut"], veri_tipi=gercek["veri_tipi"],
                     referans_gercek_sure_ms=ham_sure, kaynak_csv=gercek["kaynak_csv"])
        rows.append(dict(**ortak, kayit_turu="gercek_sirali_olcum", paralel_oran_f="",
                         calisan_sayisi=1, teorik_hizlanma="", sure_ms=ham_sure,
                         aciklama="CSV'den okunan gercek sirali ortalama; yeni olcum yapilmadi"))
        for p in calisanlar:
            rows.append(dict(**ortak, kayit_turu="teorik_tahmin", paralel_oran_f=str(f),
                             calisan_sayisi=p, teorik_hizlanma=amdahlHizlanma(f, p),
                             sure_ms=teorikSure(sure, f, p),
                             aciklama="Idealize Amdahl senaryosu; gercek paralel olcum DEGIL"))
    return rows


def teorikCsvKaydet(rows, yol):
    yol = Path(yol)
    if yol.name != "paralel_merge_teorik.csv":
        raise ValueError("Çıktı adı paralel_merge_teorik.csv olmalıdır.")
    yol.parent.mkdir(parents=True, exist_ok=True)
    with yol.open("x", encoding="utf-8", newline="") as dosya:
        yazici = csv.DictWriter(dosya, fieldnames=CSV_ALANLAR)
        yazici.writeheader()
        yazici.writerows(rows)


if __name__ == "__main__":
    kok = Path(__file__).resolve().parents[1]
    rows = tahminleriOlustur(mergeSureleriniOku(kok))
    yol = kok / "sonuclar/analizler/paralel_merge_teorik.csv"
    teorikCsvKaydet(rows, yol)
    print(f"{len(rows)} kayıt: 4 mevcut sıralı ölçüm + 12 teorik tahmin. Paralel deney yapılmadı.")
    print(yol)
