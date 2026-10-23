import unittest
from collections import Counter
from unittest.mock import patch

from algoritmalar import merge
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar


class AnahtarliEleman:
    """Yalnızca anahtarla karşılaştırılan, kimliği ayırt edilebilir test verisi."""

    def __init__(self, anahtar, kimlik):
        self.anahtar = anahtar
        self.kimlik = kimlik

    def __le__(self, diger):
        return self.anahtar <= diger.anahtar

    def __gt__(self, diger):
        return self.anahtar > diger.anahtar


class MergeSortTestleri(unittest.TestCase):
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
                self.assertIsNone(merge.mergeSort(dizi, Sayaclar()))
                self.assertEqual(dizi, beklenen)
                self.assertTrue(isSorted(dizi))
                self.assertEqual(Counter(dizi), ilk_elemanlar)

    def test_elle_hesaplanan_sayaclar(self):
        # İki elemanı birleştirmek: 1 karşılaştırma, 2 tampon + 2 ana yazım.
        for dizi, karsilastirma, hareket in [
            ([], 0, 0), ([7], 0, 0),
            ([1, 2], 1, 4), ([2, 1], 1, 4),
            ([1, 3, 2], 2, 10),
            ([1, 2, 3, 4], 4, 16),
            ([4, 3, 2, 1], 4, 16),
            ([8, 3, 5, 1], 5, 16),
            ([5, 5, 5, 5], 4, 16),
        ]:
            with self.subTest(dizi=dizi.copy()):
                sayaclar = Sayaclar()
                merge.mergeSort(dizi, sayaclar)
                self.assertEqual(sayaclar.karsilastirma_sayisi, karsilastirma)
                self.assertEqual(sayaclar.hareket_sayisi, hareket)

    def test_tek_yardimci_dizinin_boyutu_ve_paylasimi(self):
        for uzunluk in [0, 1, 5, 8]:
            with self.subTest(uzunluk=uzunluk):
                dizi = list(range(uzunluk, 0, -1))
                with patch.object(merge, "_araligi_sirala",
                                  wraps=merge._araligi_sirala) as izlenen:
                    merge.mergeSort(dizi, Sayaclar())
                yardimci_dizi = izlenen.call_args_list[0].args[1]
                self.assertEqual(len(yardimci_dizi), uzunluk)
                self.assertIsNot(yardimci_dizi, dizi)
                for cagri in izlenen.call_args_list:
                    self.assertIs(cagri.args[0], dizi)
                    self.assertIs(cagri.args[1], yardimci_dizi)

    def test_kararlilik(self):
        dizi = [AnahtarliEleman(anahtar, kimlik) for anahtar, kimlik in [
            (2, "A"), (1, "B"), (2, "C"),
            (1, "D"), (2, "E"), (1, "F"),
        ]]
        ilk_elemanlar = Counter(dizi)
        merge.mergeSort(dizi, Sayaclar())
        self.assertTrue(isSorted(dizi))
        self.assertEqual([eleman.kimlik for eleman in dizi],
                         ["B", "D", "F", "A", "C", "E"])
        self.assertEqual(Counter(dizi), ilk_elemanlar)

    def test_on_bin_eleman(self):
        dizi = list(range(9999, -1, -1))
        ilk_elemanlar = Counter(dizi)
        merge.mergeSort(dizi, Sayaclar())
        self.assertEqual(dizi, list(range(10000)))
        self.assertTrue(isSorted(dizi))
        self.assertEqual(Counter(dizi), ilk_elemanlar)

    def test_sayaclar_sifirlanmaz_ve_bagimsizdir(self):
        sayaclar = Sayaclar(10, 20)
        diger_sayaclar = Sayaclar()
        merge.mergeSort([2, 1], sayaclar)
        self.assertEqual(sayaclar, Sayaclar(11, 24))
        self.assertEqual(diger_sayaclar, Sayaclar())


if __name__ == "__main__":
    unittest.main()
