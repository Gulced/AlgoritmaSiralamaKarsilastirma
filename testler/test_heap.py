import random
import unittest
from collections import Counter

from algoritmalar.heap import _asagi_suz, _max_yigin_olustur, heapSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar


class HeapSortTestleri(unittest.TestCase):
    def test_dogruluk_ve_eleman_butunlugu(self):
        for dizi, beklenen in [
            ([], []), ([7], [7]),
            ([1, 2, 3, 4], [1, 2, 3, 4]),
            ([4, 3, 2, 1], [1, 2, 3, 4]),
            ([8, 3, 5, 1], [1, 3, 5, 8]),
            ([5, 5, 2, 2], [2, 2, 5, 5]),
            ([-1, -3, 0, -2], [-3, -2, -1, 0]),
            ([5, 5, 5, 5], [5, 5, 5, 5]),
            ([9, 1, 7, 3, 5], [1, 3, 5, 7, 9]),
        ]:
            with self.subTest(dizi=dizi.copy()):
                ilk_elemanlar = Counter(dizi)
                self.assertIsNone(heapSort(dizi, Sayaclar()))
                self.assertEqual(dizi, beklenen)
                self.assertTrue(isSorted(dizi))
                self.assertEqual(Counter(dizi), ilk_elemanlar)

    def test_elle_hesaplanan_sayaclar(self):
        for dizi, karsilastirma, hareket in [
            ([], 0, 0), ([7], 0, 0),
            ([1, 2], 1, 6), ([2, 1], 1, 3),
            ([1, 1], 1, 3),
            ([1, 2, 3], 3, 12), ([3, 2, 1], 3, 9),
        ]:
            with self.subTest(dizi=dizi.copy()):
                sayaclar = Sayaclar()
                heapSort(dizi, sayaclar)
                self.assertEqual(sayaclar.karsilastirma_sayisi, karsilastirma)
                self.assertEqual(sayaclar.hareket_sayisi, hareket)

    def test_max_yigin_olusturma(self):
        for dizi in [[], [7], [1, 2], [1, 2, 3, 4, 5],
                     [8, 3, 5, 1], [5, 5, 2, 2], [-3, 0, -1]]:
            with self.subTest(dizi=dizi.copy()):
                ilk_elemanlar = Counter(dizi)
                _max_yigin_olustur(dizi, Sayaclar())
                for cocuk in range(1, len(dizi)):
                    ebeveyn = (cocuk - 1) // 2
                    self.assertGreaterEqual(dizi[ebeveyn], dizi[cocuk])
                self.assertEqual(Counter(dizi), ilk_elemanlar)

    def test_asagi_suzme_siniri_ve_basarisiz_karsilastirmalar(self):
        dizi = [3, 2, 1, 99]
        sayaclar = Sayaclar()
        _asagi_suz(dizi, 3, 0, sayaclar)
        self.assertEqual(dizi, [3, 2, 1, 99])
        self.assertEqual(sayaclar, Sayaclar(2, 0))

    def test_on_bin_karisik_eleman_yinelemeli_suzme(self):
        beklenen = list(range(10000))
        dizi = beklenen.copy()
        random.Random(317).shuffle(dizi)
        ilk_elemanlar = Counter(dizi)
        # Özyineleme sınırını artırmadan büyük girdiyi sırala.
        heapSort(dizi, Sayaclar())
        self.assertEqual(dizi, beklenen)
        self.assertTrue(isSorted(dizi))
        self.assertEqual(Counter(dizi), ilk_elemanlar)

    def test_sayaclar_sifirlanmaz_ve_bagimsizdir(self):
        sayaclar = Sayaclar(10, 20)
        diger_sayaclar = Sayaclar()
        heapSort([2, 1], sayaclar)
        self.assertEqual(sayaclar, Sayaclar(11, 23))
        self.assertEqual(diger_sayaclar, Sayaclar())


if __name__ == "__main__":
    unittest.main()
