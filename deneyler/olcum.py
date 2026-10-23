"""Tekil ölçüm ve aynı başlangıç verisiyle tekrar altyapısı.

Süre yalnızca algoritma çağrısını kapsar: Python yürütme ve algoritmanın
sayaç artırma maliyeti dahildir. Kopyalama, sayaç nesnesi oluşturma ve
doğrulama dışarıdadır. perf_counter_ns sonuçları zamanlamaya göre değişir;
nanosaniye birimi nanosaniyelik ölçüm doğruluğu garantisi değildir.
Milisaniye dönüşümü: sure_ns / 1_000_000.

Farklı seed'lerin koordinasyonu gelecekte deney yöneticisinde yapılacaktır.
Tam deneylerde warm-up algoritma ve dağılıma göre dikkatle yönetilmelidir.
"""

from collections import Counter
import time

from algoritmalar.bubble import bubbleSort
from algoritmalar.heap import heapSort
from algoritmalar.insertion import insertionSort
from algoritmalar.merge import mergeSort
from algoritmalar.quick import quickSort
from algoritmalar.selection import selectionSort
from algoritmalar.shell import shellSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar


ALGORITMALAR = {
    "selection": selectionSort,
    "insertion": insertionSort,
    "bubble": bubbleSort,
    "shell": shellSort,
    "quick": quickSort,
    "merge": mergeSort,
    "heap": heapSort,
}


def tekOlcum(algoritma_adi, baslangic_dizisi):
    if algoritma_adi not in ALGORITMALAR:
        raise ValueError(f"Bilinmeyen algoritma adı: {algoritma_adi}")
    algoritma = ALGORITMALAR[algoritma_adi]
    dizi = baslangic_dizisi.copy()
    sayaclar = Sayaclar()

    baslangic = time.perf_counter_ns()
    algoritma(dizi, sayaclar)
    bitis = time.perf_counter_ns()

    sirali = isSorted(dizi)
    # İkinci büyük Counter yerine tek frekans tablosundan çıkarma yap.
    eleman_farklari = Counter(baslangic_dizisi)
    eleman_farklari.subtract(dizi)
    eleman_butunlugu = all(fark == 0 for fark in eleman_farklari.values())

    return {
        "algoritma_adi": algoritma_adi,
        "sure_ns": bitis - baslangic,
        "karsilastirma_sayisi": sayaclar.karsilastirma_sayisi,
        "hareket_sayisi": sayaclar.hareket_sayisi,
        "sirali": sirali,
        "eleman_butunlugu": eleman_butunlugu,
        "basarili": sirali and eleman_butunlugu,
    }


def tekrarliOlcum(algoritma_adi, baslangic_dizisi, tekrar_sayisi=5):
    """Bir warm-up ve aynı başlangıç dizisinde bağımsız ölçümler yapar."""
    if type(tekrar_sayisi) is not int or tekrar_sayisi <= 0:
        raise ValueError("Tekrar sayısı pozitif bir tam sayı olmalıdır.")

    isinma_sonucu = tekOlcum(algoritma_adi, baslangic_dizisi)
    olcumler = [tekOlcum(algoritma_adi, baslangic_dizisi)
                for _ in range(tekrar_sayisi)]

    return {
        "algoritma_adi": algoritma_adi,
        "tekrar_sayisi": tekrar_sayisi,
        "isinma_sonucu": isinma_sonucu,
        "olcumler": olcumler,
        "ortalama_sure_ns": sum(sonuc["sure_ns"] for sonuc in olcumler) / tekrar_sayisi,
        "ortalama_karsilastirma_sayisi": sum(
            sonuc["karsilastirma_sayisi"] for sonuc in olcumler) / tekrar_sayisi,
        "ortalama_hareket_sayisi": sum(
            sonuc["hareket_sayisi"] for sonuc in olcumler) / tekrar_sayisi,
        "basarili": isinma_sonucu["basarili"] and all(
            sonuc["basarili"] for sonuc in olcumler),
    }
