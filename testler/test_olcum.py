import unittest
from unittest.mock import patch

from deneyler import olcum


class OlcumTestleri(unittest.TestCase):
    def test_yedi_algoritma_ve_giris_korunmasi(self):
        self.assertEqual(set(olcum.ALGORITMALAR),
                         {"selection", "insertion", "bubble", "shell", "quick", "merge", "heap"})
        for ad in olcum.ALGORITMALAR:
            with self.subTest(algoritma=ad):
                dizi = [8, 3, 5, 1]
                sonuc = olcum.tekOlcum(ad, dizi)
                self.assertEqual(dizi, [8, 3, 5, 1])
                self.assertTrue(sonuc["sirali"])
                self.assertTrue(sonuc["eleman_butunlugu"])
                self.assertTrue(sonuc["basarili"])
                self.assertIsInstance(sonuc["sure_ns"], int)
                self.assertGreaterEqual(sonuc["sure_ns"], 0)

    def test_sayaclar_dogru_aktarilir(self):
        sonuc = olcum.tekOlcum("selection", [8, 3, 5, 1])
        self.assertEqual(sonuc["karsilastirma_sayisi"], 6)
        self.assertEqual(sonuc["hareket_sayisi"], 3)

    def test_bos_ve_tek_eleman(self):
        for ad in olcum.ALGORITMALAR:
            for dizi in [[], [7]]:
                with self.subTest(algoritma=ad, dizi=dizi):
                    sonuc = olcum.tekOlcum(ad, dizi)
                    self.assertTrue(sonuc["basarili"])
                    self.assertEqual(sonuc["karsilastirma_sayisi"], 0)
                    self.assertEqual(sonuc["hareket_sayisi"], 0)

    def test_bes_tekrar_bagimsiz_kopya_ve_sayac(self):
        gorulen_diziler = []
        gorulen_sayaclar = []

        def izlenen_algoritma(dizi, sayaclar):
            self.assertEqual(dizi, [2, 1])
            self.assertEqual(sayaclar.karsilastirma_sayisi, 0)
            gorulen_diziler.append(dizi)
            gorulen_sayaclar.append(sayaclar)
            olcum.selectionSort(dizi, sayaclar)

        dizi = [2, 1]
        with patch.dict(olcum.ALGORITMALAR, selection=izlenen_algoritma):
            sonuc = olcum.tekrarliOlcum("selection", dizi)
        self.assertEqual(len(sonuc["olcumler"]), 5)
        self.assertEqual(len({id(dizi) for dizi in gorulen_diziler}), 6)
        self.assertEqual(len({id(sayac) for sayac in gorulen_sayaclar}), 6)
        self.assertTrue(sonuc["basarili"])
        self.assertEqual(dizi, [2, 1])

    def test_isinma_haric_ortalamalar(self):
        sonuclar = [dict(sure_ns=sure, karsilastirma_sayisi=sure * 2,
                         hareket_sayisi=sure * 3, basarili=True)
                    for sure in [99999, 10, 20, 30, 40, 50]]
        with patch.object(olcum, "tekOlcum", side_effect=sonuclar) as sahte:
            sonuc = olcum.tekrarliOlcum("quick", [2, 1])
        self.assertEqual(sahte.call_count, 6)
        self.assertEqual(sonuc["isinma_sonucu"], sonuclar[0])
        self.assertEqual(sonuc["olcumler"], sonuclar[1:])
        self.assertEqual(sonuc["ortalama_sure_ns"], 30)
        self.assertEqual(sonuc["ortalama_karsilastirma_sayisi"], 60)
        self.assertEqual(sonuc["ortalama_hareket_sayisi"], 90)

    def test_gecersiz_algoritma(self):
        for fonksiyon in [olcum.tekOlcum, olcum.tekrarliOlcum]:
            with self.assertRaisesRegex(ValueError, "Bilinmeyen algoritma"):
                fonksiyon("gecersiz", [])

    def test_gecersiz_tekrar(self):
        for tekrar in [0, -1, 1.5, True]:
            with self.subTest(tekrar=tekrar):
                with self.assertRaises(ValueError):
                    olcum.tekrarliOlcum("quick", [], tekrar)

    def test_sirali_ama_elemanlari_bozuk_sonuc(self):
        def bozuk_algoritma(dizi, sayaclar):
            dizi[0] = 1
        with patch.dict(olcum.ALGORITMALAR, selection=bozuk_algoritma):
            sonuc = olcum.tekrarliOlcum("selection", [2, 1], 1)
        for tekil in [sonuc["isinma_sonucu"], *sonuc["olcumler"]]:
            self.assertTrue(tekil["sirali"])
            self.assertFalse(tekil["eleman_butunlugu"])
            self.assertFalse(tekil["basarili"])
        self.assertFalse(sonuc["basarili"])

    def test_sirasiz_sonuc_basarisizdir(self):
        with patch.dict(olcum.ALGORITMALAR, selection=lambda dizi, sayaclar: None):
            sonuc = olcum.tekOlcum("selection", [2, 1])
        self.assertFalse(sonuc["sirali"])
        self.assertTrue(sonuc["eleman_butunlugu"])
        self.assertFalse(sonuc["basarili"])

    def test_zamanlama_sirasi(self):
        olaylar = []

        def saat():
            olaylar.append("saat")
            return len(olaylar) * 100

        def algoritma(dizi, sayaclar):
            olaylar.append("algoritma")
            olcum.selectionSort(dizi, sayaclar)

        def dogrula(dizi):
            olaylar.append("dogrulama")
            return True

        with patch.dict(olcum.ALGORITMALAR, selection=algoritma), \
                patch.object(olcum.time, "perf_counter_ns", side_effect=saat), \
                patch.object(olcum, "isSorted", side_effect=dogrula):
            sonuc = olcum.tekOlcum("selection", [2, 1])
        self.assertEqual(olaylar, ["saat", "algoritma", "saat", "dogrulama"])
        self.assertEqual(sonuc["sure_ns"], 200)


if __name__ == "__main__":
    unittest.main()
