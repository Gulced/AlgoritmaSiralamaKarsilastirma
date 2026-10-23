"""Yalnızca n=100 rastgele veri pilotu: python -m deneyler.pilot."""

from pathlib import Path

from deneyler.deney_yoneticisi import deneyCalistir
from deneyler.kayit import csvKaydet


if __name__ == "__main__":
    klasor = Path(__file__).resolve().parents[1] / "sonuclar"
    if any((klasor / ad).exists() for ad in ("ham_sonuclar.csv", "ozet_sonuclar.csv")):
        raise FileExistsError("Pilot sonuçları mevcut; korumak için önce başka klasöre taşıyın.")
    sonuclar = deneyCalistir(100, "rastgele")
    for yol in csvKaydet(sonuclar, klasor):
        print(yol)
    print(f"Gerçek ölçüm: {len(sonuclar['ham_sonuclar'])}, özet: {len(sonuclar['ozet_sonuclar'])}")
    print(f"Tümü başarılı: {all(s['basarili_mi'] for s in sonuclar['ozet_sonuclar'])}")
