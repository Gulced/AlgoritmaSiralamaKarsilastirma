"""Bubble Sort adımlarını gösterir; performans ölçümü yapmaz."""

from dataclasses import dataclass
import re


def _diziyi_dogrula(dizi):
    if not 5 <= len(dizi) <= 20:
        raise ValueError("Lütfen 5 ile 20 arasında eleman girin.")
    if any(type(deger) is not int for deger in dizi):
        raise ValueError("Bütün elemanlar tam sayı olmalıdır.")


def girdiyiCoz(metin):
    """Virgül veya boşlukla ayrılmış, işaretli tam sayıları okur."""
    if not isinstance(metin, str) or not re.fullmatch(
        r"\s*[+-]?[0-9]+(?:(?:\s*,\s*|\s+)[+-]?[0-9]+)*\s*", metin
    ):
        raise ValueError("Tam sayıları virgül veya boşlukla ayırın. Örnek: 8, -3, 5, 1, 5")
    parcalar = re.split(r"[,\s]+", metin.strip())
    if not 5 <= len(parcalar) <= 20:
        raise ValueError("Lütfen 5 ile 20 arasında eleman girin.")
    try:
        dizi = [int(parca) for parca in parcalar]
    except ValueError as hata:
        raise ValueError("Bir tam sayı okunamadı; çok uzun sayı girişini kısaltın.") from hata
    return dizi


@dataclass(frozen=True)
class Adim:
    """Tuple görüntüleri sonradan değiştirilemez; gezinti sıralamayı çalıştırmaz."""

    dizi: tuple[int, ...]
    tur: str
    aciklama: str
    indeksler: tuple[int, int] | None = None
    degerler: tuple[int, int] | None = None
    takas: bool = False


def adimlariOlustur(baslangic_dizisi):
    """Deneydeki Bubble Sort ile aynı tur sınırları ve erken durma kuralı."""
    _diziyi_dogrula(baslangic_dizisi)
    dizi = list(baslangic_dizisi)
    adimlar = [Adim(tuple(dizi), "baslangic", "Başlangıç dizisi. İlerlemek için Sonraki düğmesine basın.")]
    erken_durdu = False
    for son_indeks in range(len(dizi) - 1, 0, -1):
        degisim_oldu = False
        for indeks in range(son_indeks):
            sol, sag = dizi[indeks], dizi[indeks + 1]
            takas = sol > sag
            karar = "Takas gerekiyor." if takas else "Takas yapılmaz."
            adimlar.append(Adim(tuple(dizi), "karsilastirma",
                f"{indeks} ve {indeks + 1}. indeksler karşılaştırılıyor: {sol} > {sag} "
                f"{'doğru' if takas else 'yanlış'}. {karar}",
                (indeks, indeks + 1), (sol, sag), takas))
            if takas:
                gecici = dizi[indeks]
                dizi[indeks] = dizi[indeks + 1]
                dizi[indeks + 1] = gecici
                degisim_oldu = True
                adimlar.append(Adim(tuple(dizi), "takas",
                    f"{indeks} ve {indeks + 1}. indekslerdeki {sol} ile {sag} takas edildi.",
                    (indeks, indeks + 1), (sol, sag), True))
        if not degisim_oldu:
            erken_durdu = True
            break
    neden = " Son turda takas yapılmadığı için erken duruldu." if erken_durdu else ""
    adimlar.append(Adim(tuple(dizi), "tamamlandi", "Sıralama tamamlandı." + neden))
    return tuple(adimlar)


class BubbleUygulamasi:
    def __init__(self, pencere):
        import tkinter as tk
        from tkinter import messagebox, ttk

        self.pencere = pencere
        self.hata_goster = messagebox.showerror
        self.adimlar = ()
        self.adim_indeksi = 0
        pencere.title("BMT317 — Bubble Sort Adım Görselleştirmesi")
        pencere.geometry("1000x680")
        pencere.minsize(760, 600)
        govde = ttk.Frame(pencere, padding=18)
        govde.pack(fill="both", expand=True)
        ttk.Label(govde, text="Bubble Sort — adım adım", font=("Helvetica", 20, "bold")).pack(anchor="w")
        ttk.Label(govde, text="5–20 tam sayı girin. Virgül veya boşluk kullanabilirsiniz. İndeksler 0'dan başlar.").pack(anchor="w", pady=(6, 10))
        giris_satiri = ttk.Frame(govde)
        giris_satiri.pack(fill="x")
        self.giris = ttk.Entry(giris_satiri, font=("Helvetica", 14))
        self.giris.pack(side="left", fill="x", expand=True)
        self.giris.insert(0, "8, 3, 5, 1, 4")
        self.giris.bind("<Return>", lambda olay: self.yukle())
        ttk.Button(giris_satiri, text="Diziyi Göster", command=self.yukle).pack(side="left", padx=(8, 0))
        self.tuval = tk.Canvas(govde, background="#ffffff", highlightthickness=1,
                               highlightbackground="#d0d7de", height=340)
        self.tuval.pack(fill="both", expand=True, pady=(16, 8))
        self.tuval.bind("<Configure>", lambda olay: self.goster())
        ttk.Label(govde, text="Turuncu: ilk eleman   •   Mor: ikinci eleman   •   Yeşil: sıralama tamamlandı").pack(anchor="w")
        self.durum = ttk.Label(govde, wraplength=920, font=("Helvetica", 12))
        self.durum.pack(anchor="w", fill="x", pady=(12, 4))
        self.dizi_yazisi = ttk.Label(govde, wraplength=920)
        self.dizi_yazisi.pack(anchor="w", fill="x", pady=(0, 10))
        dugmeler = ttk.Frame(govde)
        dugmeler.pack(fill="x")
        self.baslangic_dugmesi = ttk.Button(dugmeler, text="Başlangıca Dön", command=lambda: self.git(0))
        self.onceki_dugmesi = ttk.Button(dugmeler, text="Önceki", command=lambda: self.git(self.adim_indeksi - 1))
        self.sonraki_dugmesi = ttk.Button(dugmeler, text="Sonraki", command=lambda: self.git(self.adim_indeksi + 1))
        self.son_dugmesi = ttk.Button(dugmeler, text="Sona Git", command=lambda: self.git(len(self.adimlar) - 1))
        for dugme in (self.baslangic_dugmesi, self.onceki_dugmesi, self.sonraki_dugmesi, self.son_dugmesi):
            dugme.pack(side="left", padx=(0, 8))
        ttk.Label(govde, text="Eğitim amaçlı adım gösterimi; performans ölçümü değildir.").pack(anchor="w", pady=(10, 0))
        self.yukle()

    def yukle(self):
        try:
            yeni_adimlar = adimlariOlustur(girdiyiCoz(self.giris.get()))
        except ValueError as hata:
            self.hata_goster("Geçersiz dizi", str(hata), parent=self.pencere)
            return
        self.adimlar = yeni_adimlar
        self.adim_indeksi = 0
        self.goster()

    def git(self, indeks):
        if self.adimlar:
            self.adim_indeksi = max(0, min(indeks, len(self.adimlar) - 1))
            self.goster()

    def goster(self):
        if not self.adimlar:
            return
        adim = self.adimlar[self.adim_indeksi]
        self.durum.config(text=f"Adım {self.adim_indeksi}/{len(self.adimlar) - 1} — {adim.aciklama}")
        self.dizi_yazisi.config(text=f"Dizi: {list(adim.dizi)}")
        self.baslangic_dugmesi.config(state="disabled" if self.adim_indeksi == 0 else "normal")
        self.onceki_dugmesi.config(state="disabled" if self.adim_indeksi == 0 else "normal")
        sonda = self.adim_indeksi == len(self.adimlar) - 1
        self.son_dugmesi.config(state="disabled" if sonda else "normal")
        self.sonraki_dugmesi.config(state="disabled" if sonda else "normal")
        tuval = self.tuval
        tuval.delete("all")
        genislik = max(tuval.winfo_width(), 700)
        yukseklik = max(tuval.winfo_height(), 250)
        sol_bosluk, ust_bosluk = 45, 35
        grafik_yuksekligi = yukseklik - 90
        en_buyuk = max(0, max(adim.dizi))
        en_kucuk = min(0, min(adim.dizi))
        aralik = en_buyuk - en_kucuk or 1
        # Önce oran almak büyük tam sayılarda float taşmasını önler.
        sifir_y = ust_bosluk + (en_buyuk / aralik) * grafik_yuksekligi
        tuval.create_line(sol_bosluk - 10, sifir_y, genislik - 15, sifir_y, fill="#566573")
        tuval.create_text(20, sifir_y, text="0", fill="#34495e")
        sutun_araligi = (genislik - sol_bosluk - 20) / len(adim.dizi)
        for indeks, deger in enumerate(adim.dizi):
            x1 = sol_bosluk + indeks * sutun_araligi + 4
            x2 = sol_bosluk + (indeks + 1) * sutun_araligi - 4
            deger_y = sifir_y - (deger / aralik) * grafik_yuksekligi
            renk = "#3b9b77" if adim.tur == "tamamlandi" else "#79a9cf"
            if adim.indeksler:
                if indeks == adim.indeksler[0]:
                    renk = "#e6922e"
                elif indeks == adim.indeksler[1]:
                    renk = "#9867bc"
            tuval.create_rectangle(x1, min(sifir_y, deger_y), x2,
                                   max(sifir_y, deger_y) + (2 if deger == 0 else 0),
                                   fill=renk, outline="")
            etiket = str(deger)
            if len(etiket) > 12:
                etiket = etiket[:8] + "…"
            etiket_y = deger_y - 13 if deger >= 0 else deger_y + 13
            tuval.create_text((x1 + x2)/2, etiket_y, text=etiket, font=("Helvetica", 10))
            tuval.create_text((x1 + x2)/2, yukseklik - 16, text=str(indeks), fill="#566573")


def uygulamayiBaslat():
    import tkinter as tk

    pencere = tk.Tk()
    BubbleUygulamasi(pencere)
    pencere.mainloop()


if __name__ == "__main__":
    uygulamayiBaslat()
