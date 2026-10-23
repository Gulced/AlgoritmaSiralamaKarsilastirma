import contextlib
import csv
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deneyler import tam_deney as tam


def sahte_deney(boyut, tip, tekrar_sayisi, ana_seed, algoritmalar):
    ad = algoritmalar[0]
    ham = [dict(algoritma=ad, veri_tipi=tip, boyut=boyut, seed=ana_seed + i,
                tekrar=i + 1, sure_ns=1000, sure_ms=0.001,
                karsilastirma_sayisi=2, hareket_sayisi=3,
                sirali_mi=True, eleman_butunlugu=True, basarili_mi=True)
           for i in range(tekrar_sayisi)]
    ozet = dict(algoritma=ad, veri_tipi=tip, boyut=boyut, tekrar_sayisi=tekrar_sayisi,
                ortalama_sure_ms=0.001, ortalama_karsilastirma=2,
                ortalama_hareket=3, basarili_mi=True)
    return dict(ham_sonuclar=ham, ozet_sonuclar=[ozet],
                isinma_sonuclari={ad: {"basarili": True}})


class TamDeneyTestleri(unittest.TestCase):
    def setUp(self):
        self.gecici = tempfile.TemporaryDirectory()
        self.addCleanup(self.gecici.cleanup)
        self.klasor = Path(self.gecici.name)
        self.cikti = contextlib.redirect_stdout(io.StringIO())
        self.cikti.__enter__()
        self.addCleanup(self.cikti.__exit__, None, None, None)

    def satirlar(self, ad):
        with (self.klasor / ad).open(encoding="utf-8", newline="") as dosya:
            return list(csv.DictReader(dosya))

    def test_tum_dagilimlar_algoritmalar_ve_satir_sayilari(self):
        with patch.object(tam, "deneyCalistir", side_effect=sahte_deney) as deney:
            tam.asamaliDeney([100], klasor=self.klasor, bekleme=0)
        self.assertEqual(deney.call_count, 28)
        self.assertEqual(len(self.satirlar("ham_100.csv")), 140)
        self.assertEqual(len(self.satirlar("ozet_100.csv")), 28)
        for cagri in deney.call_args_list:
            self.assertEqual(cagri.kwargs["tekrar_sayisi"], 5)
            self.assertEqual(cagri.kwargs["ana_seed"], 317)
        self.assertEqual({c.args[1] for c in deney.call_args_list}, set(tam.VERI_TIPLERI))
        self.assertEqual({c.kwargs["algoritmalar"][0] for c in deney.call_args_list}, set(tam.ALGORITMALAR))

    def test_boyut_ve_algoritma_secimi(self):
        with patch.object(tam, "deneyCalistir", side_effect=sahte_deney) as deney:
            tam.asamaliDeney([1000], ["quick"], self.klasor, bekleme=0)
        self.assertEqual(deney.call_count, 4)
        self.assertTrue(all(c.args[0] == 1000 for c in deney.call_args_list))
        self.assertEqual(len(self.satirlar("ham_1000.csv")), 20)
        self.assertFalse((self.klasor / "ham_100.csv").exists())

    def test_gecersiz_secimler(self):
        for boyutlar, adlar in [([], None), ([500000], None), ([100, 100], None),
                                ([100], []), ([100], ["yanlis"])]:
            with self.subTest(boyutlar=boyutlar, adlar=adlar):
                with self.assertRaises(ValueError):
                    tam.asamaliDeney(boyutlar, adlar, self.klasor)

    def test_yeniden_baslatma_cogaltmaz(self):
        with patch.object(tam, "deneyCalistir", side_effect=sahte_deney) as deney:
            tam.asamaliDeney([100], ["quick"], self.klasor, bekleme=0)
            tam.asamaliDeney([100], ["quick"], self.klasor, bekleme=0)
            self.assertEqual(deney.call_count, 4)
            tam.asamaliDeney([100], ["quick"], self.klasor, bekleme=0, yeniden=True)
            self.assertEqual(deney.call_count, 8)
        self.assertEqual(len(self.satirlar("ham_100.csv")), 20)

    def test_kesintiden_sonra_devam(self):
        ilk = sahte_deney(100, "rastgele", 5, 317, ["quick"])
        with patch.object(tam, "deneyCalistir", side_effect=[ilk, KeyboardInterrupt()]):
            with self.assertRaises(KeyboardInterrupt):
                tam.asamaliDeney([100], ["quick"], self.klasor, bekleme=0)
        self.assertEqual(len(self.satirlar("ham_100.csv")), 5)
        with patch.object(tam, "deneyCalistir", side_effect=sahte_deney) as deney:
            tam.asamaliDeney([100], ["quick"], self.klasor, bekleme=0)
            self.assertEqual(deney.call_count, 3)
        self.assertEqual(len(self.satirlar("ham_100.csv")), 20)

    def test_csv_yazimi_kesilirse_kontrol_noktasindan_onarim(self):
        with patch.object(tam, "deneyCalistir", side_effect=sahte_deney), \
                patch.object(tam, "_csvleri_kaydet", side_effect=OSError("Disk hatası")):
            with self.assertRaises(OSError):
                tam.asamaliDeney([100], ["quick"], self.klasor, bekleme=0)
        with patch.object(tam, "deneyCalistir", side_effect=sahte_deney) as deney:
            tam.asamaliDeney([100], ["quick"], self.klasor, bekleme=0)
            self.assertEqual(deney.call_count, 3)
        self.assertEqual(len(self.satirlar("ham_100.csv")), 20)

    def test_basarisiz_grup_korunur_ve_yeniden_denenir(self):
        def bozuk(*args, **kwargs):
            sonuc = sahte_deney(*args, **kwargs)
            sonuc["ham_sonuclar"][0]["basarili_mi"] = False
            sonuc["ozet_sonuclar"][0]["basarili_mi"] = False
            return sonuc
        with patch.object(tam, "deneyCalistir", side_effect=bozuk):
            tam.asamaliDeney([100], ["quick"], self.klasor, bekleme=0)
        self.assertTrue(all(s["basarili_mi"] == "False" for s in self.satirlar("ozet_100.csv")))
        with patch.object(tam, "deneyCalistir", side_effect=sahte_deney) as deney:
            tam.asamaliDeney([100], ["quick"], self.klasor, bekleme=0)
            self.assertEqual(deney.call_count, 4)
        self.assertEqual(len(self.satirlar("ham_100.csv")), 20)

    def test_varsayilan_cli_deney_baslatmaz(self):
        with patch.object(tam, "asamaliDeney") as calistir, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                tam.komutSatiri([])
            calistir.assert_not_called()

    def test_atomik_yazma_hatasi_onceki_dosyayi_korur(self):
        yol = self.klasor / "deneme.csv"
        yol.write_text("önceki", encoding="utf-8")
        with patch.object(tam.os, "replace", side_effect=OSError("Disk hatası")):
            with self.assertRaises(OSError):
                tam._atomik_yaz(yol, "yeni")
        self.assertEqual(yol.read_text(encoding="utf-8"), "önceki")
        self.assertEqual(list(self.klasor.glob("*.tmp")), [])
