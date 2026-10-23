import contextlib
import csv
import hashlib
import io
from pathlib import Path
import tempfile
import tracemalloc
import unittest
from unittest.mock import patch

from deneyler import bellek_analizi as bellek


class BellekAnaliziTestleri(unittest.TestCase):
    def test_yedi_algoritma_ve_giris_korunmasi(self):
        self.assertEqual(set(bellek.TEORIK_EK_ALAN),
                         {"selection", "insertion", "bubble", "shell", "quick", "merge", "heap"})
        for ad in bellek.ALGORITMALAR:
            with self.subTest(algoritma=ad):
                dizi = [8, 3, 5, 1, 3]
                sonuc = bellek.bellekOlc(ad, dizi, "rastgele")
                self.assertEqual(dizi, [8, 3, 5, 1, 3])
                self.assertTrue(sonuc["sirali_mi"])
                self.assertTrue(sonuc["eleman_butunlugu"])
                self.assertTrue(sonuc["basarili_mi"])
                self.assertGreaterEqual(sonuc["olculen_tepe_bellek_bayt"], 0)
                self.assertEqual(sonuc["olculen_tepe_bellek_kib"],
                                 sonuc["olculen_tepe_bellek_bayt"] / 1024)

    def test_gecersiz_adlar(self):
        for ad, tip in [("yanlis", "rastgele"), ("quick", "yanlis")]:
            with self.assertRaises(ValueError):
                bellek.bellekOlc(ad, [2, 1], tip)

    def test_mevcut_tracemalloc_korunur(self):
        self.assertFalse(tracemalloc.is_tracing())
        tracemalloc.start(3)
        try:
            veri = bytearray(4096)
            with self.assertRaisesRegex(RuntimeError, "zaten etkin"):
                bellek.bellekOlc("quick", [2, 1], "rastgele")
            self.assertTrue(tracemalloc.is_tracing())
            self.assertEqual(tracemalloc.get_traceback_limit(), 3)
            self.assertGreaterEqual(tracemalloc.get_traced_memory()[0], len(veri))
        finally:
            tracemalloc.stop()

    def test_algoritma_hatasinda_oturum_kapatilir(self):
        with patch.dict(bellek.ALGORITMALAR, quick=lambda d, s: 1 / 0):
            with self.assertRaises(ZeroDivisionError):
                bellek.bellekOlc("quick", [2, 1], "rastgele")
        self.assertFalse(tracemalloc.is_tracing())

    def test_izleme_sinirlari_ve_bagimsiz_sayaclar(self):
        diziler = []
        sayaclar = []

        def izlenen(dizi, sayac):
            self.assertTrue(tracemalloc.is_tracing())
            self.assertEqual(sayac.karsilastirma_sayisi, 0)
            diziler.append(dizi)
            sayaclar.append(sayac)
            bellek.ALGORITMALAR["selection"](dizi, sayac)

        gercek_dogrula = bellek.isSorted

        def dogrula(dizi):
            self.assertFalse(tracemalloc.is_tracing())
            return gercek_dogrula(dizi)

        giris = [2, 1]
        with patch.dict(bellek.ALGORITMALAR, quick=izlenen), \
                patch.object(bellek, "isSorted", side_effect=dogrula), \
                patch("deneyler.olcum.tekOlcum", side_effect=AssertionError("Süre ölçümü çağrılmamalı")):
            bellek.bellekOlc("quick", giris, "rastgele")
            bellek.bellekOlc("quick", giris, "rastgele")
        self.assertIsNot(diziler[0], diziler[1])
        self.assertIsNot(diziler[0], giris)
        self.assertIsNot(sayaclar[0], sayaclar[1])

    def test_basarisiz_siralama_ve_butunluk(self):
        def eleman_boz(dizi, sayac):
            dizi[0] = 1
        with patch.dict(bellek.ALGORITMALAR, quick=eleman_boz):
            sonuc = bellek.bellekOlc("quick", [2, 1], "rastgele")
        self.assertTrue(sonuc["sirali_mi"])
        self.assertFalse(sonuc["eleman_butunlugu"])
        self.assertFalse(sonuc["basarili_mi"])
        with patch.dict(bellek.ALGORITMALAR, quick=lambda d, s: None):
            sonuc = bellek.bellekOlc("quick", [2, 1], "rastgele")
        self.assertFalse(sonuc["sirali_mi"])
        self.assertTrue(sonuc["eleman_butunlugu"])
        self.assertFalse(sonuc["basarili_mi"])

    def test_kontrollu_matris_44_kombinasyon(self):
        def sahte(ad, dizi, tip):
            return {"olculen_tepe_bellek_bayt": 0, "basarili_mi": True}
        with patch.object(bellek, "bellekOlc", side_effect=sahte) as olc, \
                contextlib.redirect_stdout(io.StringIO()):
            sonuclar = bellek.kontrolluBellekDeneyi()
        self.assertEqual(len(sonuclar), 44)
        kombinasyonlar = {(c.args[0], len(c.args[1]), c.args[2]) for c in olc.call_args_list}
        self.assertEqual(len(kombinasyonlar), 44)
        for ad, boyut, tip in kombinasyonlar:
            self.assertIn(tip, bellek.VERI_TIPLERI)
            self.assertIn(boyut, (1000, 10000))
            if boyut == 10000:
                self.assertIn(ad, ("shell", "quick", "merge", "heap"))

    def test_csv_ve_performans_dosyalari_korunur(self):
        kok = Path(__file__).resolve().parents[1]
        onceki = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (kok / "sonuclar").rglob("*.csv")}
        sonuc = bellek.bellekOlc("merge", [3, 1, 2], "rastgele")
        with tempfile.TemporaryDirectory() as gecici:
            yol = Path(gecici) / "bellek_sonuclari.csv"
            bellek.bellekCsvKaydet([sonuc], yol)
            with yol.open(encoding="utf-8", newline="") as dosya:
                okuyucu = csv.DictReader(dosya)
                self.assertEqual(okuyucu.fieldnames, bellek.CSV_ALANLAR)
                self.assertEqual(len(list(okuyucu)), 1)
            with self.assertRaises(FileExistsError):
                bellek.bellekCsvKaydet([sonuc], yol)
            with self.assertRaises(ValueError):
                bellek.bellekCsvKaydet([sonuc], Path(gecici) / "ham_sonuclar.csv")
        for yol, ozet in onceki.items():
            self.assertEqual(hashlib.sha256(yol.read_bytes()).hexdigest(), ozet)


if __name__ == "__main__":
    unittest.main()
