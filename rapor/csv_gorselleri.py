"""Kayıtlı CSV'lerden seçilmiş satır/sütun kesitleri çizer; kaynakları değiştirmez."""

import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

KOK = Path(__file__).resolve().parents[1]


def csvKesitleriOlustur(hedef):
    hedef = Path(hedef)
    hedef.mkdir(parents=True, exist_ok=True)
    font_dizini = Path('/System/Library/Fonts/Supplemental')
    normal = ImageFont.truetype(str(font_dizini / 'Times New Roman.ttf'), 32)
    kalin = ImageFont.truetype(str(font_dizini / 'Times New Roman Bold.ttf'), 32)
    tanimlar = [
        ('ham_100000', 'deneyler/ham_100000.csv',
         lambda k: k['algoritma'] == 'quick' and k['veri_tipi'] == 'rastgele',
         [('algoritma', 'Algoritma', 170), ('seed', 'Seed', 100), ('tekrar', 'Tekrar', 120),
          ('sure_ms', 'Süre (ms)', 340), ('karsilastirma_sayisi', 'Karşılaştırma', 310),
          ('hareket_sayisi', 'Hareket', 260)], 'n=100000; rastgele; ilk üç tekrar'),
        ('ozet_100000', 'deneyler/ozet_100000.csv',
         lambda k: k['algoritma'] in ('shell', 'quick', 'merge') and k['veri_tipi'] == 'rastgele',
         [('algoritma', 'Algoritma', 170), ('tekrar_sayisi', 'Tekrar', 120),
          ('ortalama_sure_ms', 'Ort. süre (ms)', 340),
          ('ortalama_karsilastirma', 'Ort. karşılaştırma', 390),
          ('ortalama_hareket', 'Ort. hareket', 330)], 'n=100000; rastgele; üç algoritmanın özeti'),
        ('bellek_sonuclari', 'bellek_sonuclari.csv',
         lambda k: k['boyut'] == '10000' and k['veri_tipi'] == 'rastgele' and k['algoritma'] in ('quick', 'merge', 'heap'),
         [('algoritma', 'Algoritma', 180), ('boyut', 'Boyut', 180),
          ('olculen_tepe_bellek_bayt', 'Tepe bellek (bayt)', 380),
          ('olculen_tepe_bellek_kib', 'Tepe bellek (KiB)', 380),
          ('basarili_mi', 'Başarılı', 180)], 'n=10000; rastgele; ayrı tracemalloc ölçümleri'),
    ]
    yollar = []
    for ad, kaynak, sec, kolonlar, not_metni in tanimlar:
        with (KOK / 'sonuclar' / kaynak).open(encoding='utf-8', newline='') as dosya:
            satirlar = [k for k in csv.DictReader(dosya) if sec(k)][:3]
        if len(satirlar) != 3:
            raise ValueError(f'CSV kesiti için üç kayıt bulunamadı: {kaynak}')
        en = sum(k[2] for k in kolonlar) + 40
        resim = Image.new('RGB', (en, 322), 'white')
        ciz = ImageDraw.Draw(resim)
        ciz.text((20, 10), Path(kaynak).name + ' — seçilmiş satır ve sütunlar', font=kalin, fill='black')
        ciz.text((20, 53), not_metni, font=normal, fill='black')
        x = 20
        for alan, baslik, genislik in kolonlar:
            degerler = [baslik] + [k[alan] for k in satirlar]
            for i, metin in enumerate(degerler):
                y = 102 + i * 50
                if ciz.textlength(metin, font=kalin if i == 0 else normal) > genislik - 14:
                    raise ValueError(f'Kesitte metin sütuna sığmıyor: {metin}')
                ciz.rectangle((x, y, x + genislik, y + 50), fill='#eeeeee' if i == 0 else 'white', outline='#999999', width=1)
                ciz.text((x + 7, y + 6), metin, font=kalin if i == 0 else normal, fill='black')
            x += genislik
        yol = hedef / f'csv_{ad}.png'
        resim.save(yol, dpi=(240, 240))
        yollar.append(yol)
    return yollar
