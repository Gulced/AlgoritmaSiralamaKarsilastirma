import unittest
from unittest.mock import patch

from cekirdek.veri_uretimi import veriUret
from deneyler import deney_yoneticisi as yonetici
from deneyler import olcum


class DeneyYoneticisiTestleri(unittest.TestCase):
    def test_pilot_sayilari_seedler_ve_ortalamalar(self):
        sonuc = yonetici.deneyCalistir(100, "rastgele")
        self.assertEqual(len(sonuc["ham_sonuclar"]), 35)
        self.assertEqual(len(sonuc["ozet_sonuclar"]), 7)
        self.assertEqual(len(sonuc["isinma_sonuclari"]), 7)
        for ozet in sonuc["ozet_sonuclar"]:
            ham = [s for s in sonuc["ham_sonuclar"] if s["algoritma"] == ozet["algoritma"]]
            self.assertEqual([s["seed"] for s in ham], list(range(317, 322)))
            self.assertEqual([s["tekrar"] for s in ham], [1, 2, 3, 4, 5])
            self.assertTrue(ozet["basarili_mi"])
            for ozet_alan, ham_alan in [("ortalama_sure_ms", "sure_ms"),
                                       ("ortalama_karsilastirma", "karsilastirma_sayisi"),
                                       ("ortalama_hareket", "hareket_sayisi")]:
                self.assertAlmostEqual(ozet[ozet_alan], sum(s[ham_alan] for s in ham) / 5)

    def test_ortak_girdi_bagimsiz_kopya_sayac_ve_donen_sira(self):
        girisler = []
        kopyalar = []
        sayaclar = []
        sira = []
        gercek_olcum = olcum.tekOlcum

        def izlenen_olcum(ad, dizi):
            girisler.append(dizi)
            sira.append(ad)
            return gercek_olcum(ad, dizi)

        def izlenen_algoritma(dizi, sayac):
            kopyalar.append(dizi)
            sayaclar.append(sayac)
            self.assertEqual(sayac.karsilastirma_sayisi, 0)
            self.assertEqual(sayac.hareket_sayisi, 0)
            olcum.quickSort(dizi, sayac)

        adlar = list(olcum.ALGORITMALAR)
        with patch.object(yonetici, "tekOlcum", side_effect=izlenen_olcum), \
                patch.object(yonetici, "veriUret", wraps=veriUret) as uretim, \
                patch.dict(olcum.ALGORITMALAR, {ad: izlenen_algoritma for ad in adlar}):
            yonetici.deneyCalistir(100, "rastgele")
        self.assertEqual(uretim.call_count, 6)
        self.assertEqual(len({id(d) for d in kopyalar}), 42)
        self.assertEqual(len({id(s) for s in sayaclar}), 42)
        for tekrar in range(5):
            baslangic = 7 + tekrar * 7
            grup = girisler[baslangic:baslangic + 7]
            for girdi in grup:
                self.assertIs(girdi, grup[0])
                self.assertEqual(girdi, veriUret(100, "rastgele", 317 + tekrar))
            self.assertIsNot(kopyalar[baslangic], grup[0])
            self.assertEqual(sira[baslangic:baslangic + 7],
                             adlar[tekrar:] + adlar[:tekrar])

    def test_isinma_dislanir_ve_basarisiz_olcum_gizlenmez(self):
        def sahte(sure, basarili=True):
            return dict(sure_ns=sure, karsilastirma_sayisi=sure,
                        hareket_sayisi=sure, sirali=basarili,
                        eleman_butunlugu=True, basarili=basarili)
        with patch.object(yonetici, "tekOlcum", side_effect=[
            sahte(999999), sahte(100), sahte(9999, False), sahte(300),
        ]):
            sonuc = yonetici.deneyCalistir(100, "rastgele", 3, algoritmalar=["quick"])
        ozet = sonuc["ozet_sonuclar"][0]
        self.assertFalse(ozet["basarili_mi"])
        self.assertEqual(ozet["ortalama_karsilastirma"], 200)
        self.assertAlmostEqual(ozet["ortalama_sure_ms"], 0.0002)
        self.assertEqual(len(sonuc["ham_sonuclar"]), 3)
        self.assertFalse(sonuc["ham_sonuclar"][1]["basarili_mi"])

    def test_tumu_basarisiz_ortalama_yok(self):
        with patch.dict(olcum.ALGORITMALAR, quick=lambda d, s: None):
            sonuc = yonetici.deneyCalistir(100, "ters_sirali", 1, algoritmalar=["quick"])
        self.assertFalse(sonuc["ozet_sonuclar"][0]["basarili_mi"])
        self.assertIsNone(sonuc["ozet_sonuclar"][0]["ortalama_sure_ms"])

    def test_gecersiz_parametreler_olcum_baslatmaz(self):
        for parametreler in [
            {"boyut": 99}, {"boyut": 100.0}, {"veri_tipi": "yanlis"},
            {"tekrar_sayisi": 0}, {"tekrar_sayisi": -1}, {"tekrar_sayisi": True},
            {"algoritmalar": ["yanlis"]}, {"algoritmalar": []},
            {"algoritmalar": ["quick", "quick"]}, {"algoritmalar": "quick"},
            {"ana_seed": "317"},
        ]:
            with self.subTest(parametreler=parametreler):
                ayarlar = dict(boyut=100, veri_tipi="rastgele")
                ayarlar.update(parametreler)
                with patch.object(yonetici, "tekOlcum") as olc:
                    with self.assertRaises(ValueError):
                        yonetici.deneyCalistir(**ayarlar)
                    olc.assert_not_called()
