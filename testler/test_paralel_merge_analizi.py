import csv
from decimal import Decimal
import hashlib
from pathlib import Path
import tempfile
import unittest

from analizler import paralel_merge_analizi as analiz


class ParalelMergeAnaliziTestleri(unittest.TestCase):
    def test_tek_calisan(self):
        for f in (0, 0.5, 0.75, 0.9, 0.95, 1):
            self.assertEqual(analiz.amdahlHizlanma(f, 1), 1)

    def test_paralel_oran_sifir_ve_bir(self):
        for p in (1, 2, 4, 8):
            self.assertEqual(analiz.amdahlHizlanma(0, p), 1)
            self.assertEqual(analiz.amdahlHizlanma(1, p), p)

    def test_gecersiz_oran(self):
        for f in (-0.1, 1.1, float("nan"), float("inf"), True, "0.9", None):
            with self.subTest(f=f):
                with self.assertRaises(ValueError):
                    analiz.amdahlHizlanma(f, 2)

    def test_gecersiz_calisan(self):
        for p in (0, -1, 2.0, True, "4", None):
            with self.subTest(p=p):
                with self.assertRaises(ValueError):
                    analiz.amdahlHizlanma(0.9, p)

    def test_hizlanma_ve_teorik_sure(self):
        self.assertEqual(analiz.amdahlHizlanma(0.75, 4), Decimal(16) / 7)
        self.assertEqual(analiz.teorikSure(100, 0.9, 2), Decimal("55"))
        self.assertEqual(analiz.teorikSure(100, 0.9, 4), Decimal("32.5"))
        self.assertEqual(analiz.teorikSure(100, 0.9, 8), Decimal("21.25"))
        for sure in (-1, float("inf"), float("nan"), True):
            with self.assertRaises(ValueError):
                analiz.teorikSure(sure, 0.9, 2)

    def test_kaynaklar_ve_etiketler_korunur(self):
        kok = Path(__file__).resolve().parents[1]
        onceki = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (kok / "sonuclar").rglob("*.csv")}
        gercekler = analiz.mergeSureleriniOku(kok)
        self.assertEqual([s["boyut"] for s in gercekler], [10000, 50000, 100000, 500000])
        for g in gercekler:
            with (kok / g["kaynak_csv"]).open(encoding="utf-8", newline="") as dosya:
                kaynak = next(s for s in csv.DictReader(dosya) if s["algoritma"] == "merge"
                              and s["veri_tipi"] == "rastgele" and int(s["boyut"]) == g["boyut"])
            self.assertEqual(g["ortalama_sure_ms"], kaynak["ortalama_sure_ms"])
        rows = analiz.tahminleriOlustur(gercekler)
        self.assertEqual(len(rows), 16)
        self.assertEqual(sum(s["kayit_turu"] == "teorik_tahmin" for s in rows), 12)
        for r in rows:
            if r["kayit_turu"] == "gercek_sirali_olcum":
                self.assertEqual(r["sure_ms"], r["referans_gercek_sure_ms"])
            else:
                self.assertIn("gercek paralel olcum DEGIL", r["aciklama"])
        with tempfile.TemporaryDirectory() as gecici:
            yol = Path(gecici) / "paralel_merge_teorik.csv"
            analiz.teorikCsvKaydet(rows, yol)
            with yol.open(encoding="utf-8", newline="") as dosya:
                okuyucu = csv.DictReader(dosya)
                self.assertEqual(okuyucu.fieldnames, analiz.CSV_ALANLAR)
                kayitlar = list(okuyucu)
            self.assertEqual(len(kayitlar), 16)
            for kayit in kayitlar:
                if kayit["kayit_turu"] == "gercek_sirali_olcum":
                    self.assertEqual(kayit["sure_ms"], kayit["referans_gercek_sure_ms"])
            with self.assertRaises(FileExistsError):
                analiz.teorikCsvKaydet(rows, yol)
        for yol, ozet in onceki.items():
            self.assertEqual(hashlib.sha256(yol.read_bytes()).hexdigest(), ozet)

    def test_eksik_kaynak_hatasi(self):
        with tempfile.TemporaryDirectory() as gecici:
            with self.assertRaises(FileNotFoundError):
                analiz.mergeSureleriniOku(gecici)


if __name__ == "__main__":
    unittest.main()
