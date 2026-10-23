import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deneyler.deney_yoneticisi import deneyCalistir
from deneyler.kayit import HAM_ALANLAR, OZET_ALANLAR, csvKaydet


class KayitTestleri(unittest.TestCase):
    def setUp(self):
        self.gecici = tempfile.TemporaryDirectory()
        self.addCleanup(self.gecici.cleanup)
        self.klasor = Path(self.gecici.name) / "sonuclar"
        self.sonuclar = deneyCalistir(100, "rastgele", algoritmalar=["quick"])

    def test_basliklar_satirlar_ve_ondaliklar(self):
        yollar = csvKaydet(self.sonuclar, self.klasor)
        for yol, alanlar, sayi in [(yollar[0], HAM_ALANLAR, 5),
                                   (yollar[1], OZET_ALANLAR, 1)]:
            with yol.open(encoding="utf-8", newline="") as dosya:
                okuyucu = csv.DictReader(dosya)
                self.assertEqual(okuyucu.fieldnames, alanlar)
                satirlar = list(okuyucu)
            self.assertEqual(len(satirlar), sayi)
            self.assertTrue(all(s["basarili_mi"] == "True" for s in satirlar))
        with yollar[0].open(encoding="utf-8", newline="") as dosya:
            for satir in csv.DictReader(dosya):
                self.assertEqual(len(satir["sure_ms"].split(".")[1]), 9)
                self.assertAlmostEqual(float(satir["sure_ms"]), int(satir["sure_ns"]) / 1e6)

    def test_yeniden_kayit_reddedilir_ve_acik_uzerine_yazma(self):
        yollar = csvKaydet(self.sonuclar, self.klasor)
        onceki = [yol.read_bytes() for yol in yollar]
        with self.assertRaises(FileExistsError):
            csvKaydet(self.sonuclar, self.klasor)
        self.assertEqual([yol.read_bytes() for yol in yollar], onceki)
        csvKaydet(self.sonuclar, self.klasor, uzerine_yaz=True)
        self.assertEqual([yol.read_bytes() for yol in yollar], onceki)

    def test_tek_mevcut_dosya_da_korunur(self):
        self.klasor.mkdir()
        ozet = self.klasor / "ozet_sonuclar.csv"
        ozet.write_text("korunacak", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            csvKaydet(self.sonuclar, self.klasor)
        self.assertEqual(ozet.read_text(encoding="utf-8"), "korunacak")
        self.assertFalse((self.klasor / "ham_sonuclar.csv").exists())

    def test_yazim_hatasi_iletilir(self):
        with patch.object(Path, "open", side_effect=OSError("Yazma başarısız")):
            with self.assertRaisesRegex(OSError, "Yazma başarısız"):
                csvKaydet(self.sonuclar, self.klasor)
