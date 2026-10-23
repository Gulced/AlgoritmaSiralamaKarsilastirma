import unittest
from collections import Counter

from algoritmalar.quick import pivot_indeksi_sec, quickSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar


class QuickSortTestleri(unittest.TestCase):
    def test_dogruluk_ve_eleman_butunlugu(self):
        for dizi, beklenen in [
            ([], []), ([7], [7]),
            ([1, 2, 3, 4], [1, 2, 3, 4]),
            ([4, 3, 2, 1], [1, 2, 3, 4]),
            ([8, 3, 5, 1], [1, 3, 5, 8]),
            ([5, 5, 2, 2], [2, 2, 5, 5]),
            ([5, 5, 5, 5], [5, 5, 5, 5]),
            ([-1, -3, 0, -2], [-3, -2, -1, 0]),
            ([9, 1, 7, 3, 5], [1, 3, 5, 7, 9]),
        ]:
            with self.subTest(dizi=dizi.copy()):
                ilk_elemanlar = Counter(dizi)
                self.assertIsNone(quickSort(dizi, Sayaclar()))
                self.assertEqual(dizi, beklenen)
                self.assertTrue(isSorted(dizi))
                self.assertEqual(Counter(dizi), ilk_elemanlar)

    def test_pivot_alt_dizinin_orta_indeksi(self):
        self.assertEqual(pivot_indeksi_sec(2, 8, "orta"), 5)
        self.assertEqual(pivot_indeksi_sec(3, 8, "orta"), 5)

    def test_gecersiz_pivot(self):
        for dizi in [[], [7], [2, 1]]:
            with self.subTest(dizi=dizi):
                onceki_dizi = dizi.copy()
                sayaclar = Sayaclar()
                with self.assertRaisesRegex(ValueError, "Geçersiz pivot yöntemi"):
                    quickSort(dizi, sayaclar, "gecersiz")
                self.assertEqual(dizi, onceki_dizi)
                self.assertEqual(sayaclar, Sayaclar())

    def test_elle_hesaplanan_sayaclar(self):
        # Hareketlere her bölümlemenin pivot kopyası da dahildir.
        for dizi, karsilastirma, hareket in [
            ([], 0, 0), ([7], 0, 0),
            ([1, 2], 3, 1), ([2, 1], 2, 4),
            ([1, 1], 2, 4),
            ([1, 2, 3], 4, 1), ([3, 2, 1], 4, 4),
        ]:
            with self.subTest(dizi=dizi.copy()):
                sayaclar = Sayaclar()
                quickSort(dizi, sayaclar)
                self.assertEqual(sayaclar.karsilastirma_sayisi, karsilastirma)
                self.assertEqual(sayaclar.hareket_sayisi, hareket)

    def test_sayaclar_sifirlanmaz_ve_bagimsizdir(self):
        sayaclar = Sayaclar(10, 20)
        diger_sayaclar = Sayaclar()
        quickSort([2, 1], sayaclar)
        self.assertEqual(sayaclar, Sayaclar(12, 24))
        self.assertEqual(diger_sayaclar, Sayaclar())

    def test_buyuk_sirali_ve_ters_sirali(self):
        beklenen = list(range(10000))
        for dizi in [beklenen.copy(), list(range(9999, -1, -1))]:
            with self.subTest(ilk_eleman=dizi[0]):
                ilk_elemanlar = Counter(dizi)
                quickSort(dizi, Sayaclar())
                self.assertEqual(dizi, beklenen)
                self.assertTrue(isSorted(dizi))
                self.assertEqual(Counter(dizi), ilk_elemanlar)

    def test_buyuk_esit_degerli_dizi(self):
        dizi = [5] * 10000
        quickSort(dizi, Sayaclar())
        self.assertEqual(dizi, [5] * 10000)
        self.assertTrue(isSorted(dizi))


if __name__ == "__main__":
    unittest.main()
