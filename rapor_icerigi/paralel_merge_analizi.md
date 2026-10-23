# Bonus 4 — Paralel Merge Sort teorik analizi

## Bonusun amacı

Mevcut sıralı Merge Sort'un hangi bölümlerinin eşzamanlı yürütülebileceğini ve
ideal hızlanmanın neden sınırlı olduğunu incelemek amaçlanmıştır. Bu belge bir
teorik incelemedir. Paralel sıralama kodu yazılmamış, paralel deney yapılmamış
ve yeni sıralama süresi ölçülmemiştir. Tablolardaki gerçek referanslar daha önce
kaydedilmiş başarılı beş tekrarın ortalamalarıdır.

## Paralelleştirme yaklaşımı

`algoritmalar/merge.py`, aralığı ikiye ayırır; önce sol, sonra sağ parçayı
özyinelemeli sıralar ve `_birlestir` ile birleştirir. Alt listeler oluşturmaz;
n elemanlı tek bir yardımcı tampon paylaşılır. Eşit değerlerde soldan seçim
kararlılığı korur. Kodun mevcut hali tamamen sıralıdır.

Sol ve sağ parçalar ayrık indekslere eriştiğinden sıralanmaları bağımsızdır.
Teorik olarak farklı çekirdeklerde eşzamanlı çalışabilirler. Üst düzey
birleştirme iki parçanın da tamamlanmasını bekler. Bu modelde her birleştirme
mevcut kodun sıralı taraması olarak kalır; farklı alt dalların birleştirmeleri
ise aynı anda ilerleyebilir.

Uygulama geliştirilseydi sınırlı çalışan havuzu ve küçük parçalar için sıralı
çalışma eşiği gerekli olurdu. Her alt probleme yeni süreç açmak uygun değildir.
İş/süreç oluşturma, görev planlama, veri aktarımı ve sonuç bekleme maliyetleri
özellikle küçük dizilerde kazancı aşabilir. Paralel sayaçlar da ortak bir
nesneye denetimsiz yazmak yerine görev başına tutulup birleştirilmelidir.

Paylaşılan bellekte n elemanlı tamponun ayrık aralıkları eşzamanlı kullanılabilir;
aynı aralığa çakışan yazımlar önlenmeli, üst birleştirme öncesinde senkronizasyon
sağlanmalıdır. İşlemci önbelleği ve bellek bant genişliği de hızlanmayı sınırlar.
Süreçlere liste gönderme, Python nesnelerinin serileştirilmesi ve kopyalanması
nedeniyle ek bellek ve iletişim maliyeti oluşturabilir; mevcut sıralı kodun O(n)
alanını her multiprocessing tasarımının toplam RAM garantisi olarak kullanamayız.

### Python yürütme ortamı

Bu proje Python 3.13.13 kullanıyor; inceleme sırasında `.venv` için
`sys._is_gil_enabled()` sonucu `True` bulundu. GIL etkin CPython'da bu saf Python,
CPU ağırlıklı sıralama için thread kullanımı çok çekirdekli hızlanma garantilemez.
3.13'te ayrı free-threaded derlemeler bulunması, bu ortamın otomatik olarak
GIL'siz olduğu anlamına gelmez. [Resmi threading açıklaması](https://docs.python.org/3.13/library/threading.html).

Multiprocessing ayrı yorumlayıcılarla GIL sınırlamasını aşabilir; buna karşılık
süreç başlatma ve nesne aktarımı maliyetlidir. Python 3.13 macOS ortamında
varsayılan `spawn`, yeni yorumlayıcı başlatır. Paylaşılan bellek seçilirse yaşam
döngüsü ve senkronizasyon ayrıca yönetilir. [Resmi multiprocessing açıklaması](https://docs.python.org/3.13/library/multiprocessing.html).

## Sözde kod

Aşağıdaki özgün sözde kod yalnızca bağımlılıkları gösterir; çalışan Python kodu
veya uygulanmış bir paralel sistem değildir. İdeal kritik yol modelinde görev
başlatma ve bekleme ek maliyeti ihmal edilir.

```text
PARALEL_SIRALA(dizi, tampon, başlangıç, bitiş):
    aralıkta en fazla bir eleman varsa dön
    orta = (başlangıç + bitiş) // 2
    sol_görev = PARALEL_BAŞLAT:
        PARALEL_SIRALA(dizi, tampon, başlangıç, orta)
    PARALEL_SIRALA(dizi, tampon, orta, bitiş)
    sol_görev tamamlanana kadar BEKLE
    SIRALI_BİRLEŞTİR(dizi, tampon, başlangıç, orta, bitiş)
```

## Karmaşıklık ve kritik yol

Mevcut sıralı Merge Sort'un birleştirme adımı her seviyede toplam doğrusal iş
yapar. Toplam iş ve ek alan:

- T1(n) = 2T1(n/2) + Θ(n) = Θ(n log n), dolayısıyla O(n log n).
- n elemanlı tampon O(n), özyineleme yığını O(log n); toplam ek alan O(n).

Alt problemler paralel fakat birleştirme sıralı olan ideal modelde:

- T∞(n) = T∞(n/2) + Θ(n) = Θ(n), dolayısıyla O(n).
- Kritik yol boyunca n + n/2 + n/4 + … = Θ(n) birleştirme işi birikir.
- Teorik paralellik T1/T∞ = Θ(log n), dolayısıyla O(log n).

Burada Θ sonuçları, mevcut birleştirmenin doğrusal tarama yapmasına dayanır.
Sınırsız sayıda çalışan olsa bile kökteki sıralı birleştirme kaldırılamaz.
İdeal Tp en az max(T1/p, T∞) olduğundan hızlanma p ile sınırsız doğrusal
büyüyemez; sabit n için kritik yol bir sınır koyar. Bu, sabit iki çalışanlı
bir model değildir: tüm seviyelerde bağımsız görevlerin ideal olarak
zamanlanabildiği iş/kritik-yol modelidir.

Birleştirmenin kendisini de paralelleştiren gelişmiş yöntemlerde farklı,
daha kısa kritik yollar mümkün olabilir. Buradaki kod böyle bir yöntem
uygulamaz; bu yöntemlere ait kazanımlar mevcut sonuçlara atfedilemez.

## Amdahl yasası

S(p) = 1 / ((1-f) + f/p).

p pozitif tam sayı çalışan sayısı, f ise paralelleştirilebilir işin varsayımsal
oranıdır. Aşağıdaki hızlanmalar ölçüm değil, yalnızca formülden hesaplanmıştır.

| Varsayımsal f | p=1 | p=2 | p=4 | p=8 |
| --- | --- | --- | --- | --- |
| 0,5 | 1,000000 | 1,333333 | 1,600000 | 1,777778 |
| 0,75 | 1,000000 | 1,600000 | 2,285714 | 2,909091 |
| 0,9 | 1,000000 | 1,818182 | 3,076923 | 4,705882 |
| 0,95 | 1,000000 | 1,904762 | 3,478261 | 5,925926 |

Örneğin f=0,90 ve p=8 için hızlanma yaklaşık 4,706'dır; 8 değildir.
p sonsuza giderken f<1 için üst sınır 1/(1-f) olur. Sabit problem boyutu,
sabit f ve ihmal edilen ek maliyetler varsayılır. Buradaki f değerleri Merge
Sort kodundan veya CSV sürelerinden ölçülmemiştir. Amdahl tablosuyla iş/kritik-yol
analizi farklı modellerdir; f=0,90 bütün n ve p değerleri için kanıtlanmış bir
Merge Sort özelliği olarak kullanılamaz.

## Gerçek sıralı ölçümlerle teorik tahminlerin ayrımı

Aşağıdaki değerler rastgele dağılımın mevcut CSV kayıtlarından okunmuştur.
Bunlar saf Python ve sayaç artırımları dahil sıralı algoritma çağrılarının
beş tekrarlı ortalamalarıdır. Veri üretimi, kopyalama, doğrulama, kayıt ve
warm-up bu ortalamalara dahil değildir. Bu aşamada yeniden ölçülmemiştir.

| Boyut | Gerçek sıralı ortalama (ms) | Kaynak CSV |
| --- | --- | --- |
| 10000 | 20,638967 | sonuclar/deneyler/ozet_10000.csv |
| 50000 | 111,532533 | sonuclar/deneyler/ozet_50000.csv |
| 100000 | 252,013850 | sonuclar/deneyler/ozet_100000.csv |
| 500000 | 1376,906517 | sonuclar/bonuslar/buyuk_veri_ozet.csv |

## Teorik sonuç tablosu

**Gerçek paralel ölçüm yapılmadı.** Aşağıdaki tüm süreler f=0,90 varsayımıyla
T_teorik = T_gerçek_sıralı / S(p) olarak hesaplanan **teorik tahminlerdir**.
Ölçülmüş sıralı Python süresini ideal hızlanmaya bölmek, gerçek Python
paralel yürütme süresini vermez. İki tablo bu nedenle ayrı sunulmuştur.

| Boyut | 2 çalışan, teorik ms | 4 çalışan, teorik ms | 8 çalışan, teorik ms |
| --- | --- | --- | --- |
| 10000 | 11,351432 | 6,707664 | 4,385780 |
| 50000 | 61,342893 | 36,248073 | 23,700663 |
| 100000 | 138,607617 | 81,904501 | 53,552943 |
| 500000 | 757,298584 | 447,494618 | 292,592635 |

## Varsayımlar ve sınırlılıklar

- f=0,50/0,75/0,90/0,95 örnek varsayımlardır; profil ölçümüne dayanmaz.
- Problem boyutu sabittir; çalışan sayısı artarken veri boyutu artırılmaz.
- Çalışanlar aynı hızda ve yeterli fiziksel kaynak varmış gibi ele alınır.
- Görev oluşturma, süreç iletişimi, senkronizasyon, dengesizlik, GIL,
  bellek bant genişliği ve önbellek maliyetleri Amdahl hesabına eklenmemiştir.
- Çalışan sayısı fiziksel çekirdek sayısıyla aynı olmak zorunda değildir;
  bu tablo donanımda 8 etkin çekirdek bulunduğunu doğrulamaz.
- Kaynak sıralı ölçümler farklı zamanlarda alınmıştır. Ondalık hassasiyet,
  aynı sayıda basamakla deneysel doğruluk veya tekrarlanabilir süre garantisi değildir.
- CSV kaynağının ondalık metni değiştirilmeden korunur; hesaplar Decimal ile
  yapılır. Gösterim tabloları altı ondalık basamağa yuvarlanmıştır.

## Sonuç

Merge Sort'un ayrık alt problemleri paralelleşmeye uygundur; ancak mevcut
sıralı birleştirmeyi koruyan modelin kritik yolu Θ(n), paralelliği Θ(log n)
ile sınırlıdır. Mevcut deneyler yalnızca sıralı Merge Sort'u doğrular.
Gerçek hızlanmanın belirlenmesi ayrı bir paralel uygulama ve kontrollü
ölçüm gerektirir; bu bonus aşamasında bunlar yapılmamıştır.

Analiz çıktısı `sonuclar/analizler/paralel_merge_teorik.csv` içinde 4
`gercek_sirali_olcum` ve 12 `teorik_tahmin` kaydıdır. Kaynak CSV'ler değiştirilmez.
Modülü tekrar çalıştırmak mevcut teorik CSV'nin üzerine yazmaz:

```bash
.venv/bin/python -m analizler.paralel_merge_analizi
```
