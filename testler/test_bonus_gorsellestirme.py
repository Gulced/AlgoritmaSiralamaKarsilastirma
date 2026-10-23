from collections import Counter
from dataclasses import FrozenInstanceError
import unittest

from algoritmalar.bubble import bubbleSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar
from gorsellestirme.bubble_gorsel import adimlariOlustur, girdiyiCoz


class BonusGorsellestirmeTestleri(unittest.TestCase):
    def test_gercek_algoritma_ile_sonuc_ve_sayaclar(self):
        for giris in ([1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [8, 3, 5, 1, 4],
                      [5, 2, 5, 2, 1], [-1, -5, 0, 3, -2], [0] * 5,
                      list(range(20, 0, -1))):
            with self.subTest(giris=giris):
                ilk = giris.copy()
                adimlar = adimlariOlustur(giris)
                dizi = giris.copy()
                sayaclar = Sayaclar()
                bubbleSort(dizi, sayaclar)
                self.assertEqual(giris, ilk)
                self.assertEqual(list(adimlar[-1].dizi), dizi)
                self.assertTrue(isSorted(adimlar[-1].dizi))
                self.assertEqual(Counter(adimlar[-1].dizi), Counter(giris))
                self.assertEqual(sum(a.tur == "karsilastirma" for a in adimlar), sayaclar.karsilastirma_sayisi)
                self.assertEqual(sum(a.tur == "takas" for a in adimlar) * 3, sayaclar.hareket_sayisi)

    def test_gercek_islem_ve_aciklama_tutarliligi(self):
        adimlar = adimlariOlustur([8, -3, 5, 1, 5])
        for onceki, adim in zip(adimlar, adimlar[1:]):
            if adim.tur == "karsilastirma":
                i, j = adim.indeksler
                self.assertEqual(j, i + 1)
                self.assertEqual(adim.dizi, onceki.dizi)
                self.assertEqual(adim.degerler, (adim.dizi[i], adim.dizi[j]))
                self.assertEqual(adim.takas, adim.degerler[0] > adim.degerler[1])
                self.assertIn(f"{adim.degerler[0]} > {adim.degerler[1]}", adim.aciklama)
                self.assertIn("Takas gerekiyor." if adim.takas else "Takas yapılmaz.", adim.aciklama)
            elif adim.tur == "takas":
                self.assertEqual(onceki.tur, "karsilastirma")
                self.assertTrue(onceki.takas)
                i, j = adim.indeksler
                beklenen = list(onceki.dizi)
                beklenen[i], beklenen[j] = beklenen[j], beklenen[i]
                self.assertEqual(adim.dizi, tuple(beklenen))
                self.assertEqual(adim.degerler, onceki.degerler)
                self.assertIn("takas edildi", adim.aciklama)
            else:
                self.assertEqual(adim.tur, "tamamlandi")
                self.assertEqual(adim.dizi, onceki.dizi)

    def test_gezinti_goruntuleri_degistirmez(self):
        adimlar = adimlariOlustur([5, 4, 3, 2, 1])
        onceki = tuple(a.dizi for a in adimlar)
        for indeks in (0, 1, 2, 1, 0, len(adimlar)-1, 2, 1):
            self.assertEqual(adimlar[indeks].dizi, onceki[indeks])
        self.assertEqual(tuple(a.dizi for a in adimlar), onceki)
        with self.assertRaises(FrozenInstanceError):
            adimlar[0].dizi = ()
        with self.assertRaises(TypeError):
            adimlar[0].dizi[0] = 99

    def test_erken_durma_ve_kisalan_turlar(self):
        sirali = adimlariOlustur([1, 2, 3, 4, 5])
        self.assertEqual(sum(a.tur == "karsilastirma" for a in sirali), 4)
        self.assertEqual(sum(a.tur == "takas" for a in sirali), 0)
        self.assertIn("erken duruldu", sirali[-1].aciklama)
        ters = adimlariOlustur([5, 4, 3, 2, 1])
        self.assertEqual([a.indeksler[0] for a in ters if a.tur == "karsilastirma"],
                         [0, 1, 2, 3, 0, 1, 2, 0, 1, 0])

    def test_gecerli_girdiler(self):
        for metin in ("8,-3,5,1,5", " 8 -3 5 1 5 ", "8, -3 5, +1, 5"):
            self.assertEqual(girdiyiCoz(metin), [8, -3, 5, 1, 5])
        self.assertEqual(girdiyiCoz(" ".join(map(str, range(20)))) , list(range(20)))

    def test_gecersiz_girdiler(self):
        for metin in ("", "1,2,3,4", "1,2,3,4,5,", "1,,2,3,4,5", "1,2,3,4,x",
                      "1,2,3,4,1.5", "1;2;3;4;5", "1,2,3,4,1e3", "--1,2,3,4,5",
                      " ".join(map(str, range(21)))):
            with self.subTest(metin=metin):
                with self.assertRaises(ValueError):
                    girdiyiCoz(metin)
        for dizi in ([], [1], list(range(21)), [1, 2, 3, 4, True], [1, 2, 3, 4, 1.5]):
            with self.assertRaises(ValueError):
                adimlariOlustur(dizi)


if __name__ == "__main__":
    unittest.main()
