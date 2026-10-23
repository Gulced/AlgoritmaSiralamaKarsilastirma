import unittest
from collections import Counter

from algoritmalar.insertion import insertionSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar


class InsertionSortTestleri(unittest.TestCase):
    def test_dogruluk_ve_sayaclar(self):
        # Her satırdaki son iki sayı karşılaştırma ve hareket beklentisidir.
        ornekler = [
            ("Bos", [], [], 0, 0),
            ("Tek elemanli", [7], [7], 0, 0),
            ("Sirali", [1, 2, 3, 4], [1, 2, 3, 4], 3, 6),
            ("Ters sirali", [4, 3, 2, 1], [1, 2, 3, 4], 6, 12),
            ("Karisik", [8, 3, 5, 1], [1, 3, 5, 8], 6, 11),
            ("Negatif", [-1, -3, 0, -2], [-3, -2, -1, 0], 5, 9),
            ("Tekrarli", [5, 5, 2, 2], [2, 2, 5, 5], 6, 10),
            ("Hepsi ayni", [5, 5, 5, 5], [5, 5, 5, 5], 3, 6),
            ("Son basarisiz karsilastirma", [1, 3, 2], [1, 2, 3], 3, 5),
            ("Iki eleman", [2, 1], [1, 2], 1, 3),
        ]
        for aciklama, dizi, beklenen, karsilastirma, hareket in ornekler:
            with self.subTest(ornek=aciklama):
                ilk_elemanlar = Counter(dizi)
                sayaclar = Sayaclar()
                sonuc = insertionSort(dizi, sayaclar)

                self.assertIsNone(sonuc)
                self.assertEqual(dizi, beklenen)
                self.assertTrue(isSorted(dizi))
                self.assertEqual(Counter(dizi), ilk_elemanlar)
                self.assertEqual(sayaclar.karsilastirma_sayisi, karsilastirma)
                self.assertEqual(sayaclar.hareket_sayisi, hareket)

    def test_sirali_dizide_kaydirma_yok(self):
        dizi = [1, 2, 3, 4, 5]
        sayaclar = Sayaclar()
        insertionSort(dizi, sayaclar)

        # Her turda yalnızca geçiciye alma ve son yerleştirme vardır.
        temel_atamalar = 2 * (len(dizi) - 1)
        self.assertEqual(sayaclar.hareket_sayisi - temel_atamalar, 0)
        self.assertEqual(sayaclar.karsilastirma_sayisi, len(dizi) - 1)


if __name__ == "__main__":
    unittest.main()
