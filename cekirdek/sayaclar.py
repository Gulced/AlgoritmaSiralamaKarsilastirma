from dataclasses import dataclass


@dataclass
class Sayaclar:
    """Veri karşılaştırmalarını ve veri atamalarını tutar.

    Geçici değişkene eleman alma ve her dizi yazımı 1 harekettir.
    Böylece geçici değişken dahil bir swap 3 hareket sayılır.
    İndeks ve döngü koşulları veri karşılaştırması sayılmaz.
    """

    karsilastirma_sayisi: int = 0
    hareket_sayisi: int = 0
