import unittest

from cekirdek.dogrulama import isSorted


class SiralilikTestleri(unittest.TestCase):
    def test_ornek_diziler(self):
        ornekler = [
            ("Sirali", [1, 2, 3, 4], True),
            ("Sirasiz", [1, 3, 2, 4], False),
            ("Bos", [], True),
            ("Tek elemanli", [7], True),
            ("Tekrarli ve sirali", [1, 2, 2, 3], True),
            ("Tekrarli ve sirasiz", [2, 2, 1], False),
        ]
        for aciklama, dizi, beklenen in ornekler:
            with self.subTest(ornek=aciklama):
                onceki_dizi = dizi.copy()
                self.assertIs(isSorted(dizi), beklenen)
                self.assertEqual(dizi, onceki_dizi)


if __name__ == "__main__":
    unittest.main()
