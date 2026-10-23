import contextlib
from collections import Counter
import csv
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from algoritmalar.quick import pivot_indeksi_sec, quickSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar
from cekirdek.veri_uretimi import veriUret
from deneyler import bonus_pivot as bonus


class BonusPivotTestleri(unittest.TestCase):
    def test_orta_eski_sayaclar_ve_varsayilan(self):
        for giris, karsilastirma, hareket in [
            ([8, 3, 5, 1], 8, 5), ([1, 2], 3, 1), ([2, 1], 2, 4),
            ([1, 2, 3], 4, 1), ([3, 2, 1], 4, 4),
        ]:
            with self.subTest(giris=giris):
                for yontem in (None, "orta"):
                    dizi = giris.copy()
                    sayaclar = Sayaclar()
                    if yontem is None:
                        quickSort(dizi, sayaclar)
                    else:
                        quickSort(dizi, sayaclar, yontem)
                    self.assertTrue(isSorted(dizi))
                    self.assertEqual(sayaclar, Sayaclar(karsilastirma, hareket))
        self.assertEqual(pivot_indeksi_sec(3, 8, "ilk"), 3)
        self.assertEqual(pivot_indeksi_sec(3, 8, "orta"), 5)

    def test_iki_pivot_dogruluk_ve_butunluk(self):
        for giris, beklenen in [([], []), ([7], [7]),
            ([1, 2, 3, 4], [1, 2, 3, 4]), ([4, 3, 2, 1], [1, 2, 3, 4]),
            ([8, 3, 5, 1], [1, 3, 5, 8]), ([2, 2, 2], [2, 2, 2]),
            ([5, 5, 2, 2], [2, 2, 5, 5]), ([-1, 0, -3], [-3, -1, 0])]:
            for pivot in bonus.PIVOTLAR:
                with self.subTest(giris=giris, pivot=pivot):
                    dizi = giris.copy()
                    self.assertIsNone(quickSort(dizi, Sayaclar(), pivot))
                    self.assertEqual(dizi, beklenen)
                    self.assertEqual(Counter(dizi), Counter(giris))
                    self.assertTrue(isSorted(dizi))

    def test_ilk_kotu_bolunme_ve_yigin_guvenligi(self):
        for giris in [list(range(1000)), list(range(999, -1, -1)), [5] * 1000]:
            ilk = Counter(giris)
            sayaclar = Sayaclar()
            sirali_baslangic = giris == list(range(1000))
            quickSort(giris, sayaclar, "ilk")
            self.assertTrue(isSorted(giris))
            self.assertEqual(Counter(giris), ilk)
            if sirali_baslangic:
                self.assertEqual(sayaclar.karsilastirma_sayisi, (1000**2 + 3 * 1000 - 4) // 2)
                self.assertEqual(sayaclar.hareket_sayisi, 999)

    def test_gecersiz_pivot(self):
        for giris in [[], [1], [2, 1]]:
            with self.assertRaises(ValueError):
                quickSort(giris, Sayaclar(), "gecersiz")
            with self.assertRaises(ValueError):
                bonus.pivotOlcum("gecersiz", giris)

    def test_ayni_veri_kopyalar_sayaclar_ve_donen_sira(self):
        gorulenler = []
        gercek_quick = quickSort

        def izlenen(dizi, sayac, pivot_yontemi):
            gorulenler.append((dizi, sayac, pivot_yontemi, dizi.copy()))
            self.assertEqual(sayac, Sayaclar())
            gercek_quick(dizi, sayac, pivot_yontemi)

        with patch.object(bonus, "quickSort", side_effect=izlenen), \
                patch.object(bonus, "veriUret", wraps=veriUret) as uretim, \
                contextlib.redirect_stdout(io.StringIO()):
            sonuc = bonus.pivotDeneyi([100])
        self.assertEqual(len(sonuc["ham_sonuclar"]), 40)
        self.assertEqual(uretim.call_count, 24)
        self.assertEqual(len(gorulenler), 48)
        self.assertEqual(len({id(s[0]) for s in gorulenler}), 48)
        self.assertEqual(len({id(s[1]) for s in gorulenler}), 48)
        for i in range(0, 48, 2):
            self.assertEqual(gorulenler[i][3], gorulenler[i + 1][3])
        for tip in bonus.VERI_TIPLERI:
            for pivot in bonus.PIVOTLAR:
                rows = [s for s in sonuc["ham_sonuclar"] if s["veri_tipi"] == tip and s["pivot_yontemi"] == pivot]
                self.assertEqual([s["seed"] for s in rows], [317, 318, 319, 320, 321])
        self.assertEqual([g[2] for g in gorulenler[2:6]], ["orta", "ilk", "ilk", "orta"])

    def test_isinma_ortalamaya_katilmaz(self):
        def sahte(pivot, dizi):
            hazirlik = dizi == veriUret(100, "rastgele", 316)
            sure = 999999 if hazirlik else 1000
            return dict(sure_ns=sure, sure_ms=sure / 1e6, karsilastirma_sayisi=7,
                        hareket_sayisi=3, sirali_mi=True, eleman_butunlugu=True, basarili_mi=True)
        with patch.object(bonus, "VERI_TIPLERI", ("rastgele",)), \
                patch.object(bonus, "pivotOlcum", side_effect=sahte), \
                contextlib.redirect_stdout(io.StringIO()):
            sonuc = bonus.pivotDeneyi([100])
        self.assertEqual(len(sonuc["ham_sonuclar"]), 10)
        for ozet in sonuc["ozet_sonuclar"]:
            self.assertEqual(ozet["ortalama_sure_ms"], 0.001)
            self.assertEqual(ozet["ortalama_karsilastirma"], 7)
            self.assertEqual(ozet["ortalama_hareket"], 3)

    def test_csv_ve_tekrar_kayit_korumasi(self):
        with contextlib.redirect_stdout(io.StringIO()):
            sonuc = bonus.pivotDeneyi([100])
        with tempfile.TemporaryDirectory() as gecici:
            yollar = bonus.pivotCsvKaydet(sonuc, gecici)
            for yol, alanlar, sayi in [(yollar[0], bonus.HAM_ALANLAR, 40), (yollar[1], bonus.OZET_ALANLAR, 8)]:
                with yol.open(encoding="utf-8", newline="") as dosya:
                    okuyucu = csv.DictReader(dosya)
                    self.assertEqual(okuyucu.fieldnames, alanlar)
                    self.assertEqual(len(list(okuyucu)), sayi)
            onceki = [p.read_bytes() for p in yollar]
            with self.assertRaises(FileExistsError):
                bonus.pivotCsvKaydet(sonuc, gecici)
            self.assertEqual([p.read_bytes() for p in yollar], onceki)

    def test_guvenli_boyutlar_ve_basarisiz_sonuc(self):
        for boyutlar in [[], [50000], [100000], [100, 100]]:
            with self.assertRaises(ValueError):
                bonus.pivotDeneyi(boyutlar)
        with patch.object(bonus, "quickSort", side_effect=lambda d, s, pivot_yontemi: None):
            sonuc = bonus.pivotOlcum("ilk", [2, 1])
        self.assertFalse(sonuc["basarili_mi"])
        self.assertFalse(sonuc["sirali_mi"])
        self.assertTrue(sonuc["eleman_butunlugu"])


if __name__ == "__main__":
    unittest.main()
