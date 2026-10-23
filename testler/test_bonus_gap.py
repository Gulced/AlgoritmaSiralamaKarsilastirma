import contextlib
from collections import Counter
import csv
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from algoritmalar.shell import klasik_gapler, knuth_gapler, shellSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar
from cekirdek.veri_uretimi import veriUret
from deneyler import bonus_gap as bonus


class BonusGapTestleri(unittest.TestCase):
    def test_gap_dizileri(self):
        for n, klasik, knuth in [
            (0, [], []), (1, [], []), (2, [1], [1]),
            (8, [4, 2, 1], [4, 1]), (10, [5, 2, 1], [4, 1]),
            (40, [20, 10, 5, 2, 1], [13, 4, 1]),
            (100, [50, 25, 12, 6, 3, 1], [40, 13, 4, 1]),
        ]:
            with self.subTest(n=n):
                self.assertEqual(klasik_gapler(n), klasik)
                self.assertEqual(knuth_gapler(n), knuth)

    def test_iki_yontem_dogruluk_ve_butunluk(self):
        for giris, beklenen in [([], []), ([7], [7]),
            ([1, 2, 3, 4], [1, 2, 3, 4]), ([4, 3, 2, 1], [1, 2, 3, 4]),
            ([8, 3, 5, 1], [1, 3, 5, 8]), ([2, 2, 2], [2, 2, 2]),
            ([5, 5, 2, 2], [2, 2, 5, 5]), ([-1, 0, -3], [-3, -1, 0]),
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5])]:
            for yontem in bonus.GAP_YONTEMLERI:
                with self.subTest(giris=giris, yontem=yontem):
                    dizi = giris.copy()
                    self.assertIsNone(shellSort(dizi, Sayaclar(), yontem))
                    self.assertEqual(dizi, beklenen)
                    self.assertEqual(Counter(dizi), Counter(giris))
                    self.assertTrue(isSorted(dizi))

    def test_klasik_sayaclar_ve_varsayilan_korunur(self):
        for giris, karsilastirma, hareket in [
            ([8, 3, 5, 1], 7, 15), ([1, 2, 3, 4], 5, 10),
            ([4, 3, 2, 1], 6, 14), ([5, 5, 5, 5], 5, 10),
        ]:
            for yontem in (None, "klasik"):
                with self.subTest(giris=giris, yontem=yontem):
                    dizi = giris.copy()
                    sayaclar = Sayaclar()
                    if yontem is None:
                        shellSort(dizi, sayaclar)
                    else:
                        shellSort(dizi, sayaclar, yontem)
                    self.assertEqual(sayaclar, Sayaclar(karsilastirma, hareket))

    def test_knuth_elle_hesaplanan_sayaclar(self):
        for giris, karsilastirma, hareket in [([], 0, 0), ([7], 0, 0),
            ([1, 2], 1, 2), ([2, 1], 1, 3), ([8, 3, 5, 1], 6, 11),
            ([1, 2, 3, 4], 3, 6), ([1, 2, 3, 4, 5], 5, 10),
            ([5, 4, 3, 2, 1], 8, 14)]:
            with self.subTest(giris=giris):
                sayaclar = Sayaclar()
                shellSort(giris, sayaclar, "knuth")
                self.assertEqual(sayaclar, Sayaclar(karsilastirma, hareket))

    def test_gecersiz_yontem_ve_boyut(self):
        for giris in [[], [7], [2, 1]]:
            with self.assertRaises(ValueError):
                shellSort(giris, Sayaclar(), "yanlis")
            with self.assertRaises(ValueError):
                bonus.gapOlcum("yanlis", giris)
        for boyutlar in [[], [50000], [100000], [500000], [100, 100]]:
            with self.assertRaises(ValueError):
                bonus.gapDeneyi(boyutlar)

    def test_ayni_girdi_kopyalar_sayaclar_ve_denge(self):
        gorulenler = []

        def izlenen(dizi, sayaclar, gap_yontemi):
            gorulenler.append((dizi, sayaclar, gap_yontemi, dizi.copy()))
            self.assertEqual(sayaclar, Sayaclar())
            shellSort(dizi, sayaclar, gap_yontemi)

        with patch.object(bonus, "shellSort", side_effect=izlenen), \
                patch.object(bonus, "veriUret", wraps=veriUret) as uretim, \
                contextlib.redirect_stdout(io.StringIO()):
            sonuc = bonus.gapDeneyi([100])
        self.assertEqual(uretim.call_count, 24)
        self.assertEqual(len(gorulenler), 48)
        self.assertEqual(len({id(s[0]) for s in gorulenler}), 48)
        self.assertEqual(len({id(s[1]) for s in gorulenler}), 48)
        for i in range(0, 48, 2):
            self.assertEqual(gorulenler[i][3], gorulenler[i + 1][3])
        self.assertEqual([g[2] for g in gorulenler[2:6]], ["klasik", "knuth", "knuth", "klasik"])
        self.assertEqual([g[2] for g in gorulenler[14:18]], ["knuth", "klasik", "klasik", "knuth"])
        for o in sonuc["ozet_sonuclar"]:
            ham = [s for s in sonuc["ham_sonuclar"] if s["gap_yontemi"] == o["gap_yontemi"] and s["veri_tipi"] == o["veri_tipi"]]
            self.assertEqual({(s["seed"], s["tekrar"]) for s in ham}, {(317+i, i+1) for i in range(5)})
            for oa, ha in [("ortalama_sure_ms", "sure_ms"), ("ortalama_karsilastirma", "karsilastirma_sayisi"), ("ortalama_hareket", "hareket_sayisi")]:
                self.assertAlmostEqual(o[oa], sum(s[ha] for s in ham) / 5)

    def test_warmup_dislanir_ve_sahte_ortalamalar(self):
        sayi = 0

        def sahte(yontem, dizi):
            nonlocal sayi
            sayi += 1
            sure = 999999 if sayi <= 2 else 1000
            return dict(sure_ns=sure, sure_ms=sure/1e6, karsilastirma_sayisi=7,
                        hareket_sayisi=3, sirali_mi=True, eleman_butunlugu=True, basarili_mi=True)

        with patch.object(bonus, "VERI_TIPLERI", ("rastgele",)), \
                patch.object(bonus, "gapOlcum", side_effect=sahte), \
                contextlib.redirect_stdout(io.StringIO()):
            sonuc = bonus.gapDeneyi([100])
        self.assertEqual(sayi, 12)
        self.assertEqual(len(sonuc["ham_sonuclar"]), 10)
        for o in sonuc["ozet_sonuclar"]:
            self.assertEqual(o["ortalama_sure_ms"], 0.001)
            self.assertEqual(o["ortalama_karsilastirma"], 7)
            self.assertEqual(o["ortalama_hareket"], 3)

    def test_csv_basliklar_ve_mukerrer_korumasi(self):
        with contextlib.redirect_stdout(io.StringIO()):
            sonuc = bonus.gapDeneyi([100])
        with tempfile.TemporaryDirectory() as gecici:
            yollar = bonus.gapCsvKaydet(sonuc, gecici)
            for yol, alanlar, adet in [(yollar[0], bonus.HAM_ALANLAR, 40), (yollar[1], bonus.OZET_ALANLAR, 8)]:
                with yol.open(encoding="utf-8", newline="") as dosya:
                    okuyucu = csv.DictReader(dosya)
                    self.assertEqual(okuyucu.fieldnames, alanlar)
                    self.assertEqual(len(list(okuyucu)), adet)
            onceki = [p.read_bytes() for p in yollar]
            with self.assertRaises(FileExistsError):
                bonus.gapCsvKaydet(sonuc, gecici)
            self.assertEqual([p.read_bytes() for p in yollar], onceki)

    def test_olcum_sinirlari_ve_basarisizlik(self):
        olaylar = []

        def saat():
            olaylar.append("saat")
            return len(olaylar) * 100

        def sirala(dizi, sayaclar, gap_yontemi):
            olaylar.append("algoritma")
            shellSort(dizi, sayaclar, gap_yontemi)

        def dogrula(dizi):
            olaylar.append("dogrulama")
            return isSorted(dizi)

        with patch.object(bonus.time, "perf_counter_ns", side_effect=saat), \
                patch.object(bonus, "shellSort", side_effect=sirala), \
                patch.object(bonus, "isSorted", side_effect=dogrula):
            sonuc = bonus.gapOlcum("knuth", [2, 1])
        self.assertEqual(olaylar, ["saat", "algoritma", "saat", "dogrulama"])
        self.assertEqual(sonuc["sure_ns"], 200)
        with patch.object(bonus, "shellSort", side_effect=lambda d, s, gap_yontemi: d.__setitem__(0, 1)):
            sonuc = bonus.gapOlcum("knuth", [2, 1])
        self.assertTrue(sonuc["sirali_mi"])
        self.assertFalse(sonuc["eleman_butunlugu"])
        self.assertFalse(sonuc["basarili_mi"])


if __name__ == "__main__":
    unittest.main()
