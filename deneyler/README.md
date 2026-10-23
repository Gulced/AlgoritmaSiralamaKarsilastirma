# Deney ve kayıt kullanımı

Proje kökünde yalnızca küçük pilotu başlatmak için:

```bash
.venv/bin/python -m deneyler.pilot
```

Pilot n=100, rastgele dağılım, yedi algoritma ve beş gerçek tekrar kullanır.
Her algoritmaya bir warm-up yapılır; bu yedi hazırlık sonucu CSV'ye ve
ortalamalara katılmaz. Gerçek tekrar seed'leri 317..321, hazırlık seed'i 316'dır.
Her seed için tek başlangıç verisi üretilir; `tekOlcum` algoritmaya ayrı kopya
ve sayaç verir. Algoritma sırası her tekrarda bir konum döner.

`deneyCalistir` ölçüm yapar, dosya yazmaz. Algoritma seçimi örneği:
`deneyCalistir(100, "rastgele", algoritmalar=["quick", "merge"])`.
Fonksiyon tüm desteklenen boyutları kabul eder; büyük çalışmalar yalnızca
bilinçli ve açık çağrıyla başlatılmalıdır. Modül içe aktarma ve `main.py`
deney başlatmaz. Tam deney matrisi henüz uygulanmamıştır.

Özet ortalamaları yalnızca başarılı gerçek ölçümleri içerir. Bir warm-up veya
gerçek ölçüm başarısızsa özet `basarili_mi=False` olur. Hiç başarılı ölçüm
yoksa ortalamalar `None`, CSV'de boş alandır. `tekrar_sayisi` istenen gerçek
tekrar sayısıdır; başarılı ölçüm adedi ham kayıtlardan anlaşılır. Başarısız
ölçümler ham CSV'de korunur. Algoritma/dosya sistemi istisnaları gizlenmez.

Süre yalnızca algoritma çağrısını ve sayaç işlemlerini içerir; veri üretimi,
kopyalama, sayaç oluşturma, doğrulama ve kayıt süre dışında kalır.
Süreler işlemci zamanlamasına göre değişir. Warm-up tam deneylerde algoritma
ve dağılıma göre değerlendirilmelidir. Sıralı ve ters sıralı dağılımlarda
seed değişse de veri doğal olarak aynıdır.

`csvKaydet(sonuc)` UTF-8 ile `sonuclar/ham_sonuclar.csv` ve
`sonuclar/ozet_sonuclar.csv` oluşturur. Varsayılan kayıt modu mevcut
dosyalardan biri varsa hata verir; satır eklemez. Tekrar kaydetmek için farklı
klasör kullanın veya açıkça `uzerine_yaz=True` verin. Pilot CLI mevcut
sonuçları korur ve üzerine yazmaz. Ondalıklar nokta ile dokuz basamak yazılır;
nanonsaniyeler tamsayı olarak korunur. İki dosyanın yazımı tek bir atomik işlem
değildir; disk hatasında kısmi çıktı kalabilir, hata çağırana iletilir.
