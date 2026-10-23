# BMT317 teslim kontrolü — 23 Ekim 2026

- Teslim PDF'si: output/pdf/BMT317_Siralama_Algoritmalari_Raporu.pdf — **45 A4 sayfa** (tablo genişlikleri ve şekil boyutları düzeltildikten sonra; önceki sürüm 47 sayfaydı).
- Düzenlenebilir Word dosyası ve rapor üreticisi aynı içerik düzeltmelerini içerir.
- “Zaman sınırını belirler” ifadesi yerine başlangıç ve bitiş zamanlarının ölçüldüğü açıklandı. Süre ölçümü, gerçek timeout desteği olarak gösterilmiyor.
- Bonus 5 açıklamaları birinci tekil şahsa uyarlandı: “tarafımdan kontrol edildi”, “kendi ekran görüntülerimden”.
- Mimari anlatımından rapor üretici dosyalarının adları ve Word üreticilerine ilişkin ifadeler çıkarıldı. Kontrol noktaları bölümü kısaltıldı; fsync/os.replace ayrıntıları kaldırıldı. Tekrarlanan sınırlılık ifadeleri azaltıldı.
- Bellek tablosunda “çağrı yığını üst sınırı” ve “çağrı yığını” Türkçe karakterlerle yazılıyor. Kaynak CSV'lerde değişiklik yapılmadı; düzeltme sadece sunum katmanında.
- İstenen beş ek/yazım düzeltmesi nihai PDF metninde doğrulandı: Şekil 10'da, Şekil 35'te, 2.800'dür, 1,10'dur, 3.337.856'dır.
- Kapak + sekiz numaralı bölüm korundu. Ekler başlığı yok. 168 kombinasyonluk tablo Bölüm 5.13'te; CSV kesitleri Bölüm 4.5.1'de; üç gerçek Tkinter ekran görüntüsü Bonus 5'te.
- 35 şekil, 10 tablo. İçindekilerdeki sekiz ana bölümün sayfa numaraları nihai PDF'deki gerçek yerleriyle karşılaştırıldı: 8/8 uyumlu.
- PDF'nin sayfaları PNG'ye dönüştürülerek yerleşimi incelendi. Son karakter düzeltmesinden sonra yalnızca sayfa 25'in piksel içeriği değişti; o sayfa ayrıca yeniden incelendi. Metin sınırı kontrolünde sayfa kenarları dışında metin bulunmadı.
- Rapor için **10 test başarılı, 0 başarısız**. Algoritma veya performans deneyleri çalıştırılmadı.
- Önceki 23 CSV dahil 279 kaynak/sonuç dosyasının SHA-256 değerleri değişmedi. Commit/push yapılmadı.
- Word'ün doğrudan PDF dışa aktarımı AppleEvent zaman aşımı verdi. İçindekileri güncellenmiş Word belgesinden PDF, paketli LibreOffice ile oluşturuldu ve ayrıca kontrol edildi.

Yeniden üretim: `.venv/bin/python -m rapor.rapor_olustur --pdf`

Bu komut Word alanlarını güncellemek için macOS Word otomasyon izni, PDF dönüşümü için LibreOffice gerektirir. Açık eski Word kopyası, yeniden oluşturulan dosyanın üzerine kaydedilmemelidir. Özgün BMT317 yönergesi erişilebilir dosyalarda bulunmadığından kapsam denetimi konuşmada verilen gereksinimlere dayanır.
