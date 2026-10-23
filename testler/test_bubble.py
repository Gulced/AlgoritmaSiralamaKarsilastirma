import unittest
from collections import Counter

from algoritmalar.bubble import bubbleSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar


class BubbleSortTestleri(unittest.TestCase):
    def test_dogruluk_ve_eleman_butunlugu(self):
        ornekler = [
            ("Bos", [], []),
            ("Tek elemanli", [7], [7]),
            ("Sirali", [1, 2, 3, 4], [1, 2, 3, 4]),
            ("Ters sirali", [4, 3, 2, 1], [1, 2, 3, 4]),
            ("Karisik", [8, 3, 5, 1], [1, 3, 5, 8]),
            ("Negatif", [-1, -3, 0, -2], [-3, -2, -1, 0]),
            ("Tekrarli", [5, 5, 2, 2], [2, 2, 5, 5]),
            ("Hepsi esit", [5, 5, 5, 5], [5, 5, 5, 5]),
        ]
        for aciklama, dizi, beklenen in ornekler:
            with self.subTest(ornek=aciklama):
                ilk_elemanlar = Counter(dizi)
                sonuc = bubbleSort(dizi, Sayaclar())
                self.assertIsNone(sonuc)
                self.assertEqual(dizi, beklenen)
                self.assertTrue(isSorted(dizi))
                self.assertEqual(Counter(dizi), ilk_elemanlar)

    def test_elle_hesaplanan_sayaclar(self):
        for dizi, karsilastirma, hareket in [
            ([], 0, 0), ([7], 0, 0),
            ([1, 2, 3, 4], 3, 0),
            ([3, 2, 1], 3, 9),
            ([2, 1], 1, 3),
            ([4, 3, 2, 1], 6, 18),
        ]:
            with self.subTest(dizi=dizi.copy()):
                sayaclar = Sayaclar()
                bubbleSort(dizi, sayaclar)
                self.assertEqual(sayaclar.karsilastirma_sayisi, karsilastirma)
                self.assertEqual(sayaclar.hareket_sayisi, hareket)

    def test_swap_sonrasinda_erken_durma(self):
        dizi = [2, 1, 3, 4, 5]
        sayaclar = Sayaclar()
        bubbleSort(dizi, sayaclar)

        self.assertEqual(dizi, [1, 2, 3, 4, 5])
        # İlk tur 4, değişimsiz ikinci tur 3 karşılaştırma; sonra durur.
        self.assertEqual(sayaclar.karsilastirma_sayisi, 7)
        self.assertEqual(sayaclar.hareket_sayisi, 3)

    def test_sayaclar_bagimsiz(self):
        ilk_sayaclar = Sayaclar()
        ikinci_sayaclar = Sayaclar()
        bubbleSort([2, 1], ilk_sayaclar)
        self.assertEqual(ikinci_sayaclar.karsilastirma_sayisi, 0)
        self.assertEqual(ikinci_sayaclar.hareket_sayisi, 0)


if __name__ == "__main__":
    unittest.main()
