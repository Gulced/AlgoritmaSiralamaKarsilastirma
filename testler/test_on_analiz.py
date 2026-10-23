import csv
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deneyler import on_analiz as analiz


class OnAnalizTestleri(unittest.TestCase):
    def test_parametre_dogrulamasi(self):
        for boyutlar in [(), (10000,), (100, 50000), (1000, 100), (100, 100), (100.0,)]:
            with self.subTest(boyutlar=boyutlar):
                with self.assertRaises(ValueError):
                    analiz.onAnaliz(boyutlar)
        for ad, tip, boyut in [("yanlis", "sirali", 100), ("quick", "yanlis", 100),
                               ("quick", "sirali", 10000)]:
            with self.assertRaises(ValueError):
                analiz.tahminUret(ad, tip, boyut, 1000)

    def test_her_algoritma_icin_tahmin(self):
        for ad in analiz.ALGORITMALAR:
            with self.subTest(ad=ad):
                sonuc = analiz.tahminUret(ad, "rastgele", 1000, 1000000, (100, 10000))
                self.assertGreater(sonuc["tahmin_10000_ms"], 0)
                self.assertIn("matematiksel tahmin", sonuc["deger_turu"])

    def test_karesel_olcekleme(self):
        for ad in ("selection", "bubble", "insertion"):
            sonuc = analiz.tahminUret(ad, "rastgele", 1000, 1000000)
            self.assertEqual(sonuc["tahmin_10000_ms"], 100)
            self.assertEqual(sonuc["tahmin_100000_ms"], 10000)

    def test_n_log_n_olcekleme(self):
        for ad in ("quick", "merge", "heap"):
            sonuc = analiz.tahminUret(ad, "rastgele", 1000, 1000000)
            self.assertAlmostEqual(sonuc["tahmin_10000_ms"],
                                   10000 * math.log2(10000) / (1000 * math.log2(1000)))

    def test_shell_olculen_buyume(self):
        sonuc = analiz.tahminUret("shell", "rastgele", 1000, 1000000, (100, 100000))
        self.assertAlmostEqual(sonuc["tahmin_10000_ms"], 10)
        self.assertIn("ölçülen büyüme", sonuc["tahmin_yontemi"])
        self.assertIsNone(analiz.tahminUret("shell", "rastgele", 100, 1000)["tahmin_10000_ms"])

    def test_insertion_dagilim_farki(self):
        sirali = analiz.tahminUret("insertion", "sirali", 1000, 1000000)
        kismi = analiz.tahminUret("insertion", "kismen_sirali", 1000, 1000000, (100, 10000))
        self.assertEqual(sirali["tahmin_10000_ms"], 10)
        self.assertAlmostEqual(kismi["tahmin_10000_ms"], 100)

    def test_varsayilan_boyutlar_ve_basarisiz_sonuc(self):
        with patch.object(analiz, "_sureclerde_olc", return_value=[
            ("quick", "rastgele", 100, {"sure_ns": 1000, "basarili": False}),
        ]) as olc:
            tablo = analiz.onAnaliz()
        olc.assert_called_once_with((100, 1000), 317)
        self.assertFalse(tablo[0]["basarili_mi"])
        self.assertIsNone(tablo[0]["tahmin_10000_ms"])

    def test_csv_basliklari_ve_koruma(self):
        satir = analiz.tahminUret("quick", "sirali", 100, 1000)
        satir["basarili_mi"] = True
        with tempfile.TemporaryDirectory() as gecici:
            yol = Path(gecici) / "on_analiz.csv"
            analiz.onAnalizKaydet([satir], yol)
            with yol.open(encoding="utf-8", newline="") as dosya:
                okuyucu = csv.DictReader(dosya)
                self.assertEqual(okuyucu.fieldnames, analiz.CSV_ALANLAR)
                self.assertEqual(len(list(okuyucu)), 1)
            with self.assertRaises(FileExistsError):
                analiz.onAnalizKaydet([satir], yol)
            for ad in ("ham_sonuclar.csv", "ozet_sonuclar.csv"):
                with self.assertRaises(ValueError):
                    analiz.onAnalizKaydet([satir], Path(gecici) / ad)
