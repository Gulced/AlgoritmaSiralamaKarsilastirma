import random
import unittest
from collections import Counter

from cekirdek.veri_uretimi import veriUret


VERI_TIPLERI = ("rastgele", "sirali", "ters_sirali", "kismen_sirali")


class VeriUretimiTestleri(unittest.TestCase):
    def test_boyut_ve_ayni_degerler(self):
        for veri_tipi in VERI_TIPLERI:
            with self.subTest(veri_tipi=veri_tipi):
                dizi = veriUret(100, veri_tipi)
                self.assertEqual(len(dizi), 100)
                self.assertEqual(Counter(dizi), Counter(range(100)))
                self.assertTrue(all(type(deger) is int for deger in dizi))

    def test_ayni_seed_ve_bes_tekrar(self):
        for veri_tipi in VERI_TIPLERI:
            for seed in range(317, 322):
                with self.subTest(veri_tipi=veri_tipi, seed=seed):
                    self.assertEqual(veriUret(100, veri_tipi, seed),
                                     veriUret(100, veri_tipi, seed))
        self.assertEqual(veriUret(100, "rastgele"),
                         veriUret(100, "rastgele", 317))

    def test_farkli_seedler(self):
        diziler = [tuple(veriUret(100, "rastgele", seed))
                   for seed in range(317, 322)]
        self.assertEqual(len(set(diziler)), 5)

    def test_sirali_ve_ters_sirali(self):
        self.assertEqual(veriUret(5, "sirali"), [0, 1, 2, 3, 4])
        self.assertEqual(veriUret(5, "ters_sirali"), [4, 3, 2, 1, 0])

    def test_kismen_sirali_degisiklik_sayisi(self):
        for boyut in [2, 3, 19, 20, 29, 100, 1000]:
            with self.subTest(boyut=boyut):
                dizi = veriUret(boyut, "kismen_sirali")
                degisen_sayisi = sum(deger != indeks
                                    for indeks, deger in enumerate(dizi))
                self.assertEqual(degisen_sayisi, max(2, boyut // 10))

    def test_secilen_konumlar_ve_dongusel_kaydirma(self):
        boyut = 100
        seed = 319
        konumlar = random.Random(seed).sample(range(boyut), 10)
        secilenler = set(konumlar)
        dizi = veriUret(boyut, "kismen_sirali", seed)
        for sira, konum in enumerate(konumlar):
            self.assertEqual(dizi[konum], konumlar[sira - 1])
            self.assertNotEqual(dizi[konum], konum)
        for indeks in range(boyut):
            if indeks not in secilenler:
                self.assertEqual(dizi[indeks], indeks)

    def test_hatalar(self):
        with self.assertRaisesRegex(ValueError, "negatif"):
            veriUret(-1, "rastgele")
        for boyut in [0, 1, 100]:
            with self.subTest(boyut=boyut):
                with self.assertRaisesRegex(ValueError, "Bilinmeyen"):
                    veriUret(boyut, "gecersiz")

    def test_bos_ve_tek_elemanli(self):
        for veri_tipi in VERI_TIPLERI:
            with self.subTest(veri_tipi=veri_tipi):
                self.assertEqual(veriUret(0, veri_tipi), [])
                self.assertEqual(veriUret(1, veri_tipi), [0])

    def test_bagimsiz_listeler(self):
        for veri_tipi in VERI_TIPLERI:
            for boyut in [0, 1, 20]:
                with self.subTest(veri_tipi=veri_tipi, boyut=boyut):
                    ilk = veriUret(boyut, veri_tipi)
                    ikinci = veriUret(boyut, veri_tipi)
                    self.assertIsNot(ilk, ikinci)
                    ilk.append(-1)
                    self.assertNotIn(-1, ikinci)

    def test_global_rastgele_durumu_korunur(self):
        onceki_durum = random.getstate()
        for veri_tipi in VERI_TIPLERI:
            veriUret(100, veri_tipi)
        self.assertEqual(random.getstate(), onceki_durum)

    def test_odev_boyutlari(self):
        for boyut in [100, 1000, 5000, 10000, 50000, 100000]:
            beklenen = Counter(range(boyut))
            for veri_tipi in VERI_TIPLERI:
                with self.subTest(boyut=boyut, veri_tipi=veri_tipi):
                    dizi = veriUret(boyut, veri_tipi)
                    self.assertEqual(len(dizi), boyut)
                    self.assertEqual(Counter(dizi), beklenen)


if __name__ == "__main__":
    unittest.main()
