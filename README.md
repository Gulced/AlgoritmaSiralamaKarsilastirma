# BMT317 — Sıralama Algoritmalarının Performans Karşılaştırması

Python ile yedi sıralama algoritmasının süre, veri karşılaştırması, veri hareketi
ve ek bellek gereksinimlerini inceleyen akademik çalışma. Algoritmalar hazır
`sort()` veya `sorted()` çağrılarına dayanmaz.

## Mevcut durum

- Zorunlu deneyler: **840 başarılı ham ölçüm, 168 özet kombinasyon**.
- Ayrı bellek analizi: **44 başarılı ölçüm**.
- Quick Sort pivot bonusu: **160 başarılı ölçüm, 32 özet**.
- Shell Sort gap bonusu: **160 başarılı ölçüm, 32 özet**.
- 500000 eleman bonusu: **80 başarılı ölçüm, 16 özet**.
- Paralel Merge Sort: yalnızca teorik analiz; gerçek paralel deney yapılmadı.
- Bubble Sort adım görselleştirmesi: bağımsız Tkinter uygulaması.
- Otomatik testler: **124 test metodu**.

Streamlit, performans grafikleri ve nihai PDF raporu henüz hazırlanmadı.
`rapor_icerigi/` içindeki teorik inceleme, nihai PDF raporu değildir.

## Yedi algoritma

| Algoritma | Modül / fonksiyon | Uygulama özelliği |
| --- | --- | --- |
| Selection Sort | `algoritmalar/selection.py` — `selectionSort` | Gereksiz swap yapmaz |
| Insertion Sort | `algoritmalar/insertion.py` — `insertionSort` | Kaydırarak yerleştirme |
| Bubble Sort | `algoritmalar/bubble.py` — `bubbleSort` | Erken durma, kısalan turlar |
| Shell Sort | `algoritmalar/shell.py` — `shellSort` | Varsayılan klasik gap; bonus Knuth |
| Quick Sort | `algoritmalar/quick.py` — `quickSort` | Varsayılan orta indeks pivotu; bonus ilk pivot |
| Merge Sort | `algoritmalar/merge.py` — `mergeSort` | Kararlı, tek yardımcı tampon |
| Heap Sort | `algoritmalar/heap.py` — `heapSort` | Max Heap ve yinelemeli sift-down |

Fonksiyonlar `fonksiyon(dizi, sayaclar)` biçiminde çağrılır, verilen listeyi
sıralar ve `None` döndürür. Shell ve Quick ek yöntem parametreleri alır.
Her bağımsız çalışmada yeni `Sayaclar()` kullanılır. Algoritmalar arayüz ve
kayıt modüllerinden bağımsızdır.

Quick küçük parçayı özyinelemeyle, büyük parçayı döngüyle işler; yığın alanı
O(log n) ile sınırlanır. İlk pivot kötü girdilerde yine O(n²) süre gerektirebilir.
Merge O(n) tampon kullanır. Mevcut Shell kodu gap listesini sakladığı için
O(log n) ek alan kullanır; O(1) olarak değerlendirilmez.

## Python ortamının kurulumu

Geliştirme ortamı: **Python 3.13.13, macOS Apple Silicon, PyCharm**.
Yalnızca standart kütüphane kullanılır; üçüncü taraf bağımlılık yoktur.
`requirements.txt` bunu belirtir. `.venv` depoya dahil edilmez.

Proje kökünde, kurulu Python sürümünü kontrol edip ortamı oluşturun:

```bash
python3.13 --version
python3.13 -m venv .venv
source .venv/bin/activate
python main.py
```

Ölçüm ortamıyla aynı sürüm için Python 3.13.13 kullanın. PyCharm'da mevcut
yerel yorumlayıcı olarak proje içindeki `.venv/bin/python` dosyasını seçin.

## Testler

```bash
.venv/bin/python -m unittest discover -s testler -v
```

Testler algoritmalar, sayaçlar, eleman bütünlüğü, veri üretimi, kayıt,
kesintiden devam ve teorik hesapları kapsar. Test komutu tam deney matrisini
başlatmaz; küçük girdiler ve gerektiğinde sahte ölçümler kullanır.

## Deney yöntemi

Zorunlu boyutlar: **100, 1000, 5000, 10000, 50000, 100000**.
Dağılımlar: `rastgele`, `sirali`, `ters_sirali`, `kismen_sirali`.

`veriUret` başlangıç değerlerini `0..n-1` olarak üretir. Yerel `random.Random`
ile deterministik Fisher–Yates karıştırması kullanılır; global rastgele durum
korunur. Kısmen sıralı veride seçilen yaklaşık %10 konum döngüsel kaydırılır;
n≥2 için en az iki konum değiştirilir. Dağılımlar aynı değerleri içerir.

Her kombinasyon için bir warm-up ve beş gerçek ölçüm vardır. Warm-up seed'i
316, gerçek tekrar seed'leri **317–321**'dir. Aynı tekrarın verisi algoritmalara
bağımsız kopyalarla verilir. Warm-up ortalamaya katılmaz.

`perf_counter_ns()` yalnızca algoritma çağrısını ölçer. Sayaç artırımları
dahildir; veri üretimi, kopyalama, sayaç oluşturma, doğrulama ve kayıt dışarıdadır.
Süreler donanım, yorumlayıcı ve işlemci zamanlamasına bağlıdır. Aşamalı zorunlu
deneyler algoritma başına ayrı gruplardır. Pivot/gap ve büyük veri bonusunda
çalışma sırası tekrarlar arasında değiştirilir. Sonuçlar farklı oturumlarda
alındığından mutlak süreler evrensel performans garantisi değildir.

### Sayaçlar ve doğrulama

- Her veri karşılaştırması, başarısız son karşılaştırmalar dahil **1** sayılır.
  İndeks ve döngü koşulları sayılmaz.
- Hareket ölçütü veri atamalarıdır. Geçiciye eleman alma ve her dizi yazımı
  **1 hareket**, geçici dahil her swap **3 hareket** sayılır.
- Merge'de tampon/ana dizi yazımları; Quick'te pivot kopyası sayılır.
  İndeks atamaları sayılmaz.
- Sıralılık `isSorted`, eleman bütünlüğü frekans farklarıyla doğrulanır.
  Başarısız ölçümler gizlenmez; özet ortalamaları başarılı gerçek ölçümlerden
  hesaplanır ve başarısızlık durumuna yansıtılır.

`sonuclar/deneyler/ham_<boyut>.csv` ve `ozet_<boyut>.csv` her boyutta
140 ham ve 28 özet satırı içerir. Kontrol noktaları yeniden başlatma için
saklanır. Bu dosyalar teslimin parçasıdır.

## Beş bonus

| Bonus | Kapsam | Çıktı |
| --- | --- | --- |
| 1 — Quick pivot | Orta/ilk; 100, 1000, 5000, 10000; dört dağılım | `sonuclar/bonuslar/pivot_*.csv` |
| 2 — Shell gap | Klasik/Knuth; aynı boyut ve dağılımlar | `sonuclar/bonuslar/gap_*.csv` |
| 3 — Büyük veri | 500000; Shell klasik, Quick orta, Merge, Heap | `sonuclar/bonuslar/buyuk_veri_*.csv` |
| 4 — Paralel Merge | İş/kritik yol ve Amdahl; paralel ölçüm yok | `sonuclar/analizler/paralel_merge_teorik.csv`, `rapor_icerigi/paralel_merge_analizi.md` |
| 5 — Bubble adımları | 5–20 tam sayı; Tkinter ile adım gezintisi | `gorsellestirme/bubble_gorsel.py` |

Ayrı `tracemalloc` analizi `sonuclar/bellek_sonuclari.csv` içindedir.
İzlenen Python tahsisleri toplam RAM veya matematiksel yardımcı alanın kesin
karşılığı değildir. Bellek ve süre ölçümleri birlikte yapılmamıştır.

## Tkinter görselleştirmesini başlatma

```bash
.venv/bin/python -m gorsellestirme.bubble_gorsel
```

PyCharm'da `gorsellestirme/bubble_gorsel.py` dosyasını açıp Run ile de
başlatabilirsiniz. Python'un Tkinter/Tk desteği ve masaüstü grafik oturumu gerekir.
Ek üçüncü taraf paket gerekmez.

5–20 tam sayıyı virgül veya boşlukla girip **Diziyi Göster** düğmesine basın.
Negatif ve tekrar eden sayılar desteklenir. **Sonraki**, **Önceki**,
**Başlangıca Dön**, **Sona Git** düğmeleri değişmez adım kayıtlarında gezinir.
Karşılaştırma ve takas ayrı görüntülerdir; indeksler 0'dan başlar. Negatif
sütunlar sıfır çizgisinin altındadır. Uzun sayı etiketleri kısaltılabilir.

Bu eğitim gösterimi performans ölçümü veya otomatik animasyon değildir.
Adım mantığı test edilmiştir. Tkinter içe aktarımı doğrulanmış, ancak masaüstü
penceresinin görsel doğrulaması geliştirme ortamında tamamlanmamıştır.

## Proje yapısı

```text
main.py
algoritmalar/       # Yedi algoritma
cekirdek/           # Sayaçlar, doğrulama, veri üretimi
deneyler/           # Ölçüm, kayıt, aşamalı deneyler ve bonuslar
analizler/          # Paralel Merge teorik hesapları
gorsellestirme/     # Tkinter Bubble adımları
testler/           # unittest testleri
sonuclar/          # Ham/özet CSV'ler ve kontrol noktaları
rapor_icerigi/      # Teorik inceleme; nihai PDF değil
requirements.txt
```

## Deneyleri yeniden çalıştırma

Mevcut sonuçlar korunmalıdır. Büyük deneyler uygulama açılışında başlamaz.
Aşamalı çalıştırıcı tamamlanan başarılı grupları varsayılan olarak atlar:

```bash
.venv/bin/python -m deneyler.tam_deney --boyutlar 100 --bekleme 1
```

`--yeniden` seçeneği seçilen grupları yeniden ölçüp değiştirir; yalnızca
bilinçli olarak kullanılmalıdır. Kontrol noktaları atomik yazılır. İki CSV
birlikte atomik değildir; sonraki başlatma kontrol noktalarından onarır.
Aynı çıktı klasöründe eşzamanlı çalıştırma desteklenmez; gerçek timeout yoktur.
Karesel algoritmalar ve ilk pivotun kötü girdileri çok uzun sürebilir.
Diğer komutlar için ilgili modül açıklamalarına ve `deneyler/README.md`
dosyasına bakın. Bazı bonus komutları mevcut çıktıyı reddeder; ayrı klasör
seçilmeden yeniden başlatılmamalıdır.

`.gitignore` sanal ortamı, IDE ayarlarını, önbellekleri, yerel gizli bilgileri
ve geçici dosyaları dışlar. Kaynak kod, ham CSV ve kontrol noktaları dışlanmaz.
