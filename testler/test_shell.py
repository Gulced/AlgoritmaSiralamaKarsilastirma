import unittest
from collections import Counter

from algoritmalar.shell import klasik_gapler, shellSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar


class ShellSortTestleri(unittest.TestCase):
    def test_gapler(self):
        for uzunluk, beklenen in [
            (8, [4, 2, 1]), (10, [5, 2, 1]), (1, []), (0, []),
        ]:
            with self.subTest(uzunluk=uzunluk):
                self.assertEqual(klasik_gapler(uzunluk), beklenen)

    def test_dogruluk_ve_eleman_butunlugu(self):
        ornekler = [
            ("Bos", [], []),
            ("Tek elemanli", [7], [7]),
            ("Sirali", [1, 2, 3, 4], [1, 2, 3, 4]),
            ("Ters sirali", [4, 3, 2, 1], [1, 2, 3, 4]),
            ("Karisik cift uzunluk", [8, 3, 5, 1], [1, 3, 5, 8]),
            ("Tekrarli", [5, 5, 2, 2], [2, 2, 5, 5]),
            ("Negatif", [-1, -3, 0, -2], [-3, -2, -1, 0]),
            ("Hepsi esit", [5, 5, 5, 5], [5, 5, 5, 5]),
            ("Tek uzunluk", [9, 1, 7, 3, 5], [1, 3, 5, 7, 9]),
            ("Birden fazla aralik", [8, 7, 6, 5, 4, 3, 2, 1],
             [1, 2, 3, 4, 5, 6, 7, 8]),
        ]
        for aciklama, dizi, beklenen in ornekler:
            with self.subTest(ornek=aciklama):
                ilk_elemanlar = Counter(dizi)
                sonuc = shellSort(dizi, Sayaclar())
                self.assertIsNone(sonuc)
                self.assertEqual(dizi, beklenen)
                self.assertTrue(isSorted(dizi))
                self.assertEqual(Counter(dizi), ilk_elemanlar)

    def test_elle_hesaplanan_sayaclar(self):
        # Karşılaştırma ve hareket beklentileri; indeks kontrolleri hariçtir.
        ornekler = [
            ([], 0, 0), ([7], 0, 0),
            ([1, 2], 1, 2), ([2, 1], 1, 3),
            ([1, 3, 2], 3, 5),
            ([1, 2, 3, 4], 5, 10),
            ([4, 3, 2, 1], 6, 14),
            ([8, 3, 5, 1], 7, 15),
            ([5, 5, 5, 5], 5, 10),
        ]
        for dizi, karsilastirma, hareket in ornekler:
            with self.subTest(dizi=dizi.copy()):
                sayaclar = Sayaclar()
                shellSort(dizi, sayaclar)
                self.assertEqual(sayaclar.karsilastirma_sayisi, karsilastirma)
                self.assertEqual(sayaclar.hareket_sayisi, hareket)

    def test_sayaclar_bagimsiz(self):
        ilk_sayaclar = Sayaclar()
        ikinci_sayaclar = Sayaclar()
        shellSort([2, 1], ilk_sayaclar)
        self.assertEqual(ikinci_sayaclar.karsilastirma_sayisi, 0)
        self.assertEqual(ikinci_sayaclar.hareket_sayisi, 0)


if __name__ == "__main__":
    unittest.main()
