"""Raporun dayandığı kayıtların kapsamını ve hesaplarını okuma yoluyla denetler."""

import math
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]


def raporVerileriniDogrula(sonuclar=KOK / 'sonuclar'):
    """Eksik/başarısız kaydı raporda tamamlanmış gibi göstermeyi önler."""
    from gorsellestirme.grafikler import ALGORITMALAR, BOYUTLAR, DAGILIMLAR, oku

    for boyut in BOYUTLAR:
        ham = oku(sonuclar / 'deneyler' / f'ham_{boyut}.csv')
        ozet = oku(sonuclar / 'deneyler' / f'ozet_{boyut}.csv')
        beklenen = {(a, d) for a in ALGORITMALAR for d in DAGILIMLAR}
        gruplar = {}
        for kayit in ham:
            anahtar = (kayit['algoritma'], kayit['veri_tipi'])
            gruplar.setdefault(anahtar, []).append(kayit)
            if any(kayit[alan] != 'True' for alan in ('sirali_mi', 'eleman_butunlugu', 'basarili_mi')):
                raise ValueError(f'Başarısız zorunlu ölçüm: {boyut}, {anahtar}')
        if set(gruplar) != beklenen or len(ozet) != 28:
            raise ValueError(f'Eksik veya mükerrer deney grubu: {boyut}')
        gorulen = set()
        for kayit in ozet:
            anahtar = (kayit['algoritma'], kayit['veri_tipi'])
            if anahtar not in beklenen or anahtar in gorulen:
                raise ValueError(f'Geçersiz özet anahtarı: {boyut}, {anahtar}')
            gorulen.add(anahtar)
            if kayit['basarili_mi'] != 'True' or int(kayit['tekrar_sayisi']) != 5:
                raise ValueError(f'Başarısız/eksik özet: {boyut}, {anahtar}')
            tekrarlar = gruplar[anahtar]
            if len(tekrarlar) != 5 or {(int(k['seed']), int(k['tekrar'])) for k in tekrarlar} != {(317+i, 1+i) for i in range(5)}:
                raise ValueError(f'Eksik veya mükerrer tekrar: {boyut}, {anahtar}')
            for ham_alan, ozet_alan in [('sure_ms', 'ortalama_sure_ms'), ('karsilastirma_sayisi', 'ortalama_karsilastirma'), ('hareket_sayisi', 'ortalama_hareket')]:
                ortalama = sum(float(k[ham_alan]) for k in tekrarlar) / 5
                if not math.isclose(ortalama, float(kayit[ozet_alan]), rel_tol=1e-9, abs_tol=1e-6):
                    raise ValueError(f'Ham/özet uyuşmazlığı: {boyut}, {anahtar}, {ozet_alan}')
    return True
