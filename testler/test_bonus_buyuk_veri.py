import contextlib
import csv
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deneyler import bonus_buyuk_veri as bonus
from deneyler import deney_yoneticisi as yonetici
from deneyler.olcum import tekOlcum


class BonusBuyukVeriTestleri(unittest.TestCase):
    def setUp(self):
        self.gecici = tempfile.TemporaryDirectory()
        self.addCleanup(self.gecici.cleanup)
        self.klasor = Path(self.gecici.name)
        self.cikti = contextlib.redirect_stdout(io.StringIO())
        self.cikti.__enter__()
        self.addCleanup(self.cikti.__exit__, None, None, None)

    def sahte_kucuk_deney(self, boyut, veri_tipi, tekrar_sayisi, ana_seed, algoritmalar):
        self.assertEqual(boyut, 500000)
        self.assertEqual(algoritmalar, ["shell", "quick", "merge", "heap"])
        # Mevcut yöneticinin akışı gerçek; yalnızca üretilecek boyut küçültülür.
        with patch.object(yonetici, "veriUret", return_value=[8, 3, 5, 1]):
            return yonetici.deneyCalistir(boyut, veri_tipi, tekrar_sayisi, ana_seed, algoritmalar)

    def oku(self, tur):
        with (self.klasor / f"buyuk_veri_{tur}.csv").open(encoding="utf-8", newline="") as dosya:
            return list(csv.DictReader(dosya))

    def test_kucuk_veri_ile_matris_ve_varsayilanlar(self):
        with patch.object(bonus, "deneyCalistir", side_effect=self.sahte_kucuk_deney), \
                patch.object(bonus.time, "sleep") as bekle:
            sonuc = bonus.buyukVeriDeneyi(klasor=self.klasor)
        self.assertEqual(set(sonuc), set(bonus.VERI_TIPLERI))
        self.assertEqual(len(self.oku("ham")), 80)
        self.assertEqual(len(self.oku("ozet")), 16)
        self.assertTrue(all(bonus._sonuc_basarili(s, t) for t, s in sonuc.items()))
        self.assertEqual(bekle.call_count, 3)
        bekle.assert_called_with(1)
        for o in self.oku("ozet"):
            ham = [s for s in self.oku("ham") if s["algoritma"] == o["algoritma"] and s["veri_tipi"] == o["veri_tipi"]]
            self.assertEqual({(int(s["seed"]), int(s["tekrar"])) for s in ham}, {(317+i, i+1) for i in range(5)})
            self.assertAlmostEqual(float(o["ortalama_sure_ms"]), sum(int(s["sure_ns"]) for s in ham)/5e6)
        self.assertEqual(bonus.OLCUM_AYARLARI["shell_gap_yontemi"], "klasik")
        self.assertEqual(bonus.OLCUM_AYARLARI["quick_pivot_yontemi"], "orta")

    def test_ayni_girdi_yontem_sirasi_ve_warmup(self):
        gorulenler = []

        def izlenen(ad, dizi):
            gorulenler.append((ad, dizi))
            return tekOlcum(ad, dizi)

        with patch.object(yonetici, "veriUret", side_effect=lambda *a, **k: [2, 1]) as uret, \
                patch.object(yonetici, "tekOlcum", side_effect=izlenen):
            sonuc = yonetici.deneyCalistir(500000, "rastgele", algoritmalar=list(bonus.ALGORITMALAR))
        self.assertEqual(uret.call_count, 6)
        self.assertEqual(len(gorulenler), 24)
        self.assertEqual(len(sonuc["ham_sonuclar"]), 20)
        for i in range(5):
            grup = gorulenler[4 + 4*i:8 + 4*i]
            self.assertTrue(all(s[1] is grup[0][1] for s in grup))
            kayma = i % 4
            self.assertEqual([s[0] for s in grup], list(bonus.ALGORITMALAR[kayma:] + bonus.ALGORITMALAR[:kayma]))

    def test_karesel_ve_gecersiz_boyut_engeli(self):
        for adlar in [None, ["selection"], ["insertion"], ["bubble"], ["quick", "bubble"]]:
            with self.assertRaises(ValueError):
                yonetici.deneyCalistir(500000, "rastgele", algoritmalar=adlar)
        with self.assertRaises(ValueError):
            yonetici.deneyCalistir(500001, "rastgele", algoritmalar=["quick"])
        for tipler in [[], ["yanlis"], ["rastgele", "rastgele"]]:
            with self.assertRaises(ValueError):
                bonus.buyukVeriDeneyi(tipler, self.klasor)

    def test_devam_mukerrer_uretmez(self):
        with patch.object(bonus, "deneyCalistir", side_effect=self.sahte_kucuk_deney) as deney:
            bonus.buyukVeriDeneyi(["rastgele"], self.klasor)
            bonus.buyukVeriDeneyi(["rastgele"], self.klasor)
            self.assertEqual(deney.call_count, 1)
        self.assertEqual(len(self.oku("ham")), 20)

    def test_kesintide_tamamlanan_grup_korunur(self):
        ilk = self.sahte_kucuk_deney(500000, "rastgele", 5, 317, list(bonus.ALGORITMALAR))
        with patch.object(bonus, "deneyCalistir", side_effect=[ilk, KeyboardInterrupt()]), \
                patch.object(bonus.time, "sleep"):
            with self.assertRaises(KeyboardInterrupt):
                bonus.buyukVeriDeneyi(["rastgele", "sirali"], self.klasor)
        self.assertEqual(len(self.oku("ham")), 20)
        with patch.object(bonus, "deneyCalistir", side_effect=self.sahte_kucuk_deney) as deney:
            bonus.buyukVeriDeneyi(["rastgele", "sirali"], self.klasor)
            self.assertEqual(deney.call_count, 1)
        self.assertEqual(len(self.oku("ham")), 40)

    def test_csv_hatasi_kontrol_noktasindan_onarilir(self):
        with patch.object(bonus, "deneyCalistir", side_effect=self.sahte_kucuk_deney), \
                patch.object(bonus, "_csvleri_yaz", side_effect=OSError("Disk")):
            with self.assertRaises(OSError):
                bonus.buyukVeriDeneyi(["rastgele"], self.klasor)
        with patch.object(bonus, "deneyCalistir", side_effect=AssertionError("Yeniden ölçülmemeli")):
            bonus.buyukVeriDeneyi(["rastgele"], self.klasor)
        self.assertEqual(len(self.oku("ham")), 20)

    def test_basarisiz_sonuc_gizlenmez(self):
        def bozuk(*args, **kwargs):
            sonuc = self.sahte_kucuk_deney(*args, **kwargs)
            sonuc["ham_sonuclar"][0]["basarili_mi"] = False
            sonuc["ozet_sonuclar"][0]["basarili_mi"] = False
            return sonuc
        with patch.object(bonus, "deneyCalistir", side_effect=bozuk):
            sonuc = bonus.buyukVeriDeneyi(["rastgele"], self.klasor)
        self.assertFalse(bonus._sonuc_basarili(sonuc["rastgele"], "rastgele"))
        self.assertEqual(self.oku("ham")[0]["basarili_mi"], "False")


if __name__ == "__main__":
    unittest.main()
