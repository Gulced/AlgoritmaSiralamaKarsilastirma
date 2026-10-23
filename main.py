import platform

from algoritmalar.bubble import bubbleSort
from algoritmalar.heap import heapSort
from algoritmalar.insertion import insertionSort
from algoritmalar.merge import mergeSort
from algoritmalar.quick import quickSort
from algoritmalar.selection import selectionSort
from algoritmalar.shell import shellSort
from cekirdek.dogrulama import isSorted
from cekirdek.sayaclar import Sayaclar

# Programın başlığını ve kullanılan Python sürümünü gösterir.
program_basligi = "BMT317 - Sıralama Algoritmalarının Performans Karşılaştırması"
python_surumu = platform.python_version()

print(program_basligi)
print(f"Python sürümü: {python_surumu}")

baslangic_dizisi = [8, 3, 5, 1]

print(f"Başlangıç dizisi: {baslangic_dizisi}")
for algoritma_adi, algoritma in [
    ("Selection Sort", selectionSort),
    ("Insertion Sort", insertionSort),
    ("Bubble Sort", bubbleSort),
    ("Shell Sort", shellSort),
    ("Quick Sort", quickSort),
    ("Merge Sort", mergeSort),
    ("Heap Sort", heapSort),
]:
    dizi = baslangic_dizisi.copy()
    sayaclar = Sayaclar()
    algoritma(dizi, sayaclar)

    print(f"\n{algoritma_adi}")
    print(f"Sıralanmış dizi: {dizi}")
    print(f"Karşılaştırma sayısı: {sayaclar.karsilastirma_sayisi}")
    print(f"Hareket sayısı: {sayaclar.hareket_sayisi}")
    print(f"Dizi sıralı mı? {isSorted(dizi)}")
