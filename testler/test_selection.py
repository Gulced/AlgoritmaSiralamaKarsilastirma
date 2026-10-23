import unittest
from collections import Counter

from algoritmalar.selection import selectionSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar


class SelectionSortTestleri(unittest.TestCase):
    def test_dogruluk_ve_sayaclar(self):
        # Son iki değer beklenen karşılaştırma ve hareket sayılarıdır.
        ornekler = [
            ("Bos", [], [], 0, 0),
            ("Tek elemanli", [7], [7], 0, 0),
            ("Sirali", [1, 2, 3, 4], [1, 2, 3, 4], 6, 0),
            ("Ters sirali", [4, 3, 2, 1], [1, 2, 3, 4], 6, 6),
            ("Karisik", [8, 3, 5, 1], [1, 3, 5, 8], 6, 3),
            ("Tekrarli", [5, 5, 2, 2], [2, 2, 5, 5], 6, 6),
            ("Negatif", [-1, -3, 0, -2], [-3, -2, -1, 0], 6, 9),
            ("Hepsi ayni", [5, 5, 5, 5], [5, 5, 5, 5], 6, 0),
        ]
        for aciklama, dizi, beklenen, karsilastirma, hareket in ornekler:
            with self.subTest(ornek=aciklama):
                ilk_elemanlar = Counter(dizi)
                ayni_dizi = dizi
                sayaclar = Sayaclar()

                sonuc = selectionSort(dizi, sayaclar)

                self.assertIsNone(sonuc)
                self.assertIs(dizi, ayni_dizi)
                self.assertEqual(dizi, beklenen)
                self.assertTrue(isSorted(dizi))
                self.assertEqual(Counter(dizi), ilk_elemanlar)
                self.assertEqual(sayaclar.karsilastirma_sayisi, karsilastirma)
                self.assertEqual(sayaclar.hareket_sayisi, hareket)

    def test_sayaclar_bagimsiz_ve_baslangicta_sifir(self):
        ilk_sayaclar = Sayaclar()
        ikinci_sayaclar = Sayaclar()
        self.assertEqual(ilk_sayaclar.karsilastirma_sayisi, 0)
        self.assertEqual(ilk_sayaclar.hareket_sayisi, 0)

        selectionSort([2, 1], ilk_sayaclar)

        self.assertEqual(ilk_sayaclar.karsilastirma_sayisi, 1)
        self.assertEqual(ilk_sayaclar.hareket_sayisi, 3)
        self.assertEqual(ikinci_sayaclar.karsilastirma_sayisi, 0)
        self.assertEqual(ikinci_sayaclar.hareket_sayisi, 0)


if __name__ == "__main__":
    unittest.main()
