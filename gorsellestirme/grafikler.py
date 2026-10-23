"""Deney CSV dosyalarından rapor grafiklerini üretir.

Yalnızca `sonuclar/` altındaki gerçek ölçümleri okur; hiçbir değer uydurulmaz.
Çıktılar `sonuclar/grafikler/` klasörüne PNG olarak yazılır ve aynı klasördeki
`grafik_listesi.md` dosyasına başlık/açıklama olarak eklenir.

Çalıştırma (proje kökünden):
    .venv/bin/python -m gorsellestirme.grafikler
"""

import csv
import math
from collections import defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
SONUCLAR = KOK / "sonuclar"
CIKTI = SONUCLAR / "grafikler"

BOYUTLAR = [100, 1000, 5000, 10000, 50000, 100000]
ALGORITMALAR = ["selection", "insertion", "bubble", "shell", "quick", "merge", "heap"]
DAGILIMLAR = ["rastgele", "sirali", "ters_sirali", "kismen_sirali"]

AD = {a: a.capitalize() + " Sort" for a in ALGORITMALAR}
DAGILIM_AD = {"rastgele": "Rastgele", "sirali": "Sıralı",
              "ters_sirali": "Ters sıralı", "kismen_sirali": "Kısmen sıralı"}

# Kategorik palet: sabit sırayla, algoritma kimliğine bağlı (sıralamaya değil).
RENK = {"selection": "#2a78d6", "insertion": "#eb6834", "bubble": "#1baf7a",
        "shell": "#eda100", "quick": "#e87ba4", "merge": "#6250d6", "heap": "#e34948"}
# Renge ek ikinci kanal: işaretçi (renk körlüğü ve siyah-beyaz baskı için).
ISARET = {"selection": "o", "insertion": "s", "bubble": "^", "shell": "D",
          "quick": "v", "merge": "P", "heap": "X"}
DAGILIM_RENK = {"rastgele": "#2a78d6", "sirali": "#1baf7a",
                "ters_sirali": "#eb6834", "kismen_sirali": "#6250d6"}

YUZEY, METIN, IKINCIL, IZGARA = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"

def grafikOrtaminiHazirla():
    """Çizim bağımlılıklarını yalnızca grafik üretileceğinde yükler."""
    global plt, FuncFormatter
    import matplotlib

    matplotlib.use("Agg")  # Pencere açmadan dosyaya çizer.
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    plt.rcParams.update({
        "figure.facecolor": YUZEY, "axes.facecolor": YUZEY, "savefig.facecolor": YUZEY,
        "text.color": METIN, "axes.labelcolor": IKINCIL, "axes.edgecolor": IZGARA,
        "xtick.color": IKINCIL, "ytick.color": IKINCIL, "axes.grid": True,
        "grid.color": IZGARA, "grid.linewidth": 0.7, "axes.axisbelow": True,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.labelsize": 9.5, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
        "legend.fontsize": 8.5, "legend.frameon": False, "font.size": 9.5,
        "lines.linewidth": 2, "lines.markersize": 6, "figure.dpi": 100,
    })


LISTE = []  # (dosya, başlık, açıklama)


# --------------------------------------------------------------------- veri
def oku(yol):
    with open(yol, encoding="utf-8", newline="") as dosya:
        return list(csv.DictReader(dosya))


def sayi(deger):
    return float(deger)


def ozet_yukle():
    """(algoritma, dağılım, n) -> {sure_ms, karsilastirma, hareket}"""
    veri = {}
    for boyut in BOYUTLAR:
        for s in oku(SONUCLAR / "deneyler" / f"ozet_{boyut}.csv"):
            veri[s["algoritma"], s["veri_tipi"], boyut] = {
                "sure": sayi(s["ortalama_sure_ms"]),
                "karsilastirma": sayi(s["ortalama_karsilastirma"]),
                "hareket": sayi(s["ortalama_hareket"]),
            }
    return veri


def ham_yukle():
    """(algoritma, dağılım, n) -> beş tekrarın süre listesi (ms)"""
    veri = defaultdict(list)
    for boyut in BOYUTLAR:
        for s in oku(SONUCLAR / "deneyler" / f"ham_{boyut}.csv"):
            veri[s["algoritma"], s["veri_tipi"], boyut].append(sayi(s["sure_ms"]))
    return veri


# ------------------------------------------------------------------ yardımcı
def sayi_bicimi(x, _pos=None):
    if x == 0:
        return "0"
    if x >= 1e9:
        return f"{x / 1e9:g} Mr"
    if x >= 1e6:
        return f"{x / 1e6:g} Mn"
    if x >= 1e3:
        return f"{x / 1e3:g} B"
    return f"{x:g}"


def sure_bicimi(ms):
    if ms >= 60_000:
        return f"{ms / 60_000:.1f} dk"
    if ms >= 1000:
        return f"{ms / 1000:.1f} sn"
    if ms >= 1:
        return f"{ms:.1f} ms"
    return f"{ms * 1000:.0f} µs"


def sure_ekseni(ms, _pos=None):
    """Log eksen etiketi: 10^k ms değerleri için okunaklı ms/sn birimi."""
    if ms >= 1000:
        return f"{ms / 1000:g} sn"
    if ms >= 1:
        return f"{ms:g} ms"
    return f"{ms * 1000:g} µs"


def kaydet(fig, dosya, baslik, aciklama):
    CIKTI.mkdir(parents=True, exist_ok=True)
    fig.savefig(CIKTI / dosya, dpi=200, bbox_inches="tight")
    plt.close(fig)
    LISTE.append((dosya, baslik, aciklama))
    print("yazıldı:", dosya)


def boyut_ekseni(ax):
    ax.set_xscale("log")
    ax.set_xticks(BOYUTLAR)
    ax.get_xaxis().set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
    ax.minorticks_off()
    ax.tick_params(axis="x", rotation=30)
    ax.set_xlabel("Veri boyutu n (log ölçek)")


def referans_cizgileri(ax, veri, dagilim, metrik):
    """Seçili ölçüte n² ve n·log n eğilim çizgilerini gri kesikli ekler (legend'da etiketli)."""
    if metrik == "hareket":
        return
    n0 = BOYUTLAR[0]
    gorunen = [veri[a, dagilim, n0][metrik] for a in ALGORITMALAR]
    taban = sorted(gorunen)[len(gorunen) // 2]  # ölçek için ortanca başlangıç
    ax.plot(BOYUTLAR, [taban * (n / n0) ** 2 for n in BOYUTLAR], ls=":", lw=1.4,
            color="#8a8984", zorder=1, label="n² eğilimi")
    ax.plot(BOYUTLAR, [taban * (n * math.log(n)) / (n0 * math.log(n0)) for n in BOYUTLAR],
            ls="--", lw=1.2, color="#8a8984", zorder=1, label="n·log n eğilimi")


def cizgi_ciz(ax, veri, dagilim, metrik, algolar=ALGORITMALAR, referans=True):
    if referans:
        referans_cizgileri(ax, veri, dagilim, metrik)
    for a in algolar:
        y = [veri[a, dagilim, n][metrik] for n in BOYUTLAR]
        ax.plot(BOYUTLAR, y, color=RENK[a], marker=ISARET[a], label=AD[a], zorder=3,
                markeredgecolor=YUZEY, markeredgewidth=1)
    boyut_ekseni(ax)
    if metrik == "hareket":
        ax.set_yscale("symlog", linthresh=10)
        ax.set_ylim(bottom=0)
    else:
        ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(
        sure_ekseni if metrik == "sure" else sayi_bicimi))


METRIK_AD = {"sure": "Ortalama çalışma süresi", "karsilastirma": "Ortalama karşılaştırma sayısı",
             "hareket": "Ortalama veri hareketi (atama) sayısı"}
METRIK_DOSYA = {"sure": "sure", "karsilastirma": "karsilastirma", "hareket": "hareket"}


# ------------------------------------------------------------------ grafikler
def boyuta_gore(veri):
    """Zorunlu grafikler 1–3: süre, karşılaştırma, hareket; boyuta göre."""
    sira = 1
    for metrik in ("sure", "karsilastirma", "hareket"):
        # Tek panel: her dağılım ayrı dosya.
        for d in DAGILIMLAR:
            fig, ax = plt.subplots(figsize=(7.2, 4.6))
            cizgi_ciz(ax, veri, d, metrik)
            ax.set_ylabel(METRIK_AD[metrik] + (" (symlog)" if metrik == "hareket" else " (log)"))
            ax.set_title(f"{METRIK_AD[metrik]} – {DAGILIM_AD[d]} veri")
            ax.legend(ncol=2, loc="upper left")
            kaydet(fig, f"{sira:02d}_{METRIK_DOSYA[metrik]}_{d}.png",
                   f"{METRIK_AD[metrik]}, {DAGILIM_AD[d]} veri",
                   "Veri boyutu log; hareket ekseni sıfırı koruyan symlog, diğerleri log. Referanslar ölçüm değildir.")
            sira += 1
        # 2x2 özet panel.
        fig, eksenler = plt.subplots(2, 2, figsize=(12, 8.2), sharex=True)
        for ax, d in zip(eksenler.flat, DAGILIMLAR):
            cizgi_ciz(ax, veri, d, metrik)
            ax.set_title(DAGILIM_AD[d])
            ax.set_xlabel("")
            ax.tick_params(axis="x", rotation=30)
        for ax in eksenler[1]:
            ax.set_xlabel("Veri boyutu n (log ölçek)")
        for ax in eksenler[:, 0]:
            ax.set_ylabel(METRIK_AD[metrik] + (" (symlog)" if metrik == "hareket" else " (log)"))
        tutamaklar, etiketler = eksenler[0, 0].get_legend_handles_labels()
        fig.legend(tutamaklar, etiketler, loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.04))
        fig.suptitle(f"{METRIK_AD[metrik]} – dört veri dağılımı", x=0.01, ha="left",
                     fontsize=13, fontweight="bold")
        fig.tight_layout(rect=(0, 0.04, 1, 0.97))
        kaydet(fig, f"{sira:02d}_{METRIK_DOSYA[metrik]}_panel.png",
               f"{METRIK_AD[metrik]}: dört dağılım yan yana",
               "Dört dağılım; x log, y hareket için symlog, diğer ölçütlerde log.")
        sira += 1


def hizli_algoritmalar(veri):
    """Shell, Quick, Merge ve Heap sonuçları doğrusal eksende büyütülmüş."""
    hizli = ["shell", "quick", "merge", "heap"]
    fig, eksenler = plt.subplots(2, 2, figsize=(12, 8.2), sharex=True)
    for ax, d in zip(eksenler.flat, DAGILIMLAR):
        for a in hizli:
            y = [veri[a, d, n]["sure"] for n in BOYUTLAR]
            ax.plot(BOYUTLAR, y, color=RENK[a], marker=ISARET[a], label=AD[a],
                    markeredgecolor=YUZEY, markeredgewidth=1)
        ax.set_title(DAGILIM_AD[d])
        ax.set_ylabel("Ortalama süre (ms)")
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
    for ax in eksenler[1]:
        ax.set_xlabel("Veri boyutu n")
    tutamaklar, etiketler = eksenler[0, 0].get_legend_handles_labels()
    fig.legend(tutamaklar, etiketler, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Hızlı algoritmalar (Shell, Quick, Merge, Heap) – doğrusal eksen", x=0.01,
                 ha="left", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    kaydet(fig, "20_hizli_algoritmalar_dogrusal.png", "Hızlı dört algoritma, doğrusal eksen",
           "Shell, Quick, Merge ve Heap için büyütülmüş görünüm; ortak bir karmaşıklık garantisi ima edilmez.")


def kareseller_ve_hizlilar(veri):
    """O(n²) algoritmaların boyutla patlaması: n=100.000 sıralama süreleri."""
    fig, ax = plt.subplots(figsize=(8, 4.8))
    x = range(len(ALGORITMALAR))
    degerler = [veri[a, "rastgele", 100000]["sure"] for a in ALGORITMALAR]
    cubuklar = ax.bar(x, degerler, color=[RENK[a] for a in ALGORITMALAR], width=0.62)
    ax.set_yscale("log")
    ax.set_xticks(list(x), [AD[a].replace(" Sort", "") for a in ALGORITMALAR])
    ax.yaxis.set_major_formatter(FuncFormatter(sure_ekseni))
    for c, d in zip(cubuklar, degerler):
        ax.annotate(sure_bicimi(d), (c.get_x() + c.get_width() / 2, d), ha="center",
                    va="bottom", fontsize=8.5, xytext=(0, 3), textcoords="offset points")
    ax.set_ylabel("Ortalama süre (log ölçek)")
    ax.set_title("n = 100.000, rastgele veri: algoritmalar arası süre farkı")
    ax.grid(axis="x", visible=False)
    kaydet(fig, "21_n100000_sure_cubuk.png", "n=100.000 rastgele veride süre karşılaştırması",
           "Yedi algoritmanın en büyük zorunlu boyuttaki süresi; log eksen.")


def dagilim_etkisi(veri):
    """Zorunlu grafik 4: veri dağılımının performansa etkisi."""
    sira = 30
    for n in (10000, 100000):
        for metrik in ("sure", "karsilastirma", "hareket"):
            fig, ax = plt.subplots(figsize=(10, 4.8))
            genislik = 0.2
            for i, d in enumerate(DAGILIMLAR):
                ofset = (i - 1.5) * genislik
                y = [veri[a, d, n][metrik] for a in ALGORITMALAR]
                ax.bar([k + ofset for k in range(len(ALGORITMALAR))], y, genislik * 0.92,
                       color=DAGILIM_RENK[d], label=DAGILIM_AD[d])
            ax.set_xticks(range(len(ALGORITMALAR)), [AD[a].replace(" Sort", "") for a in ALGORITMALAR])
            if metrik == "hareket":
                ax.set_yscale("symlog", linthresh=10)
                ax.set_ylim(bottom=0)
            else:
                ax.set_yscale("log")
            ax.yaxis.set_major_formatter(FuncFormatter(
                sure_ekseni if metrik == "sure" else sayi_bicimi))
            ax.set_ylabel(METRIK_AD[metrik] + (" (symlog)" if metrik == "hareket" else " (log)"))
            ax.set_title(f"Veri dağılımının etkisi – {METRIK_AD[metrik].lower()} (n = {n:,})".replace(",", "."))
            ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1))
            ax.grid(axis="x", visible=False)
            kaydet(fig, f"{sira}_dagilim_{METRIK_DOSYA[metrik]}_n{n}.png",
                   f"Dağılım etkisi: {METRIK_AD[metrik].lower()} (n={n})",
                   "Her algoritma için dört dağılım; hareket symlog, diğer ölçütler log eksen.")
            sira += 1

    # Kayıp oranı: rastgele veriye göre yavaşlama/hızlanma çarpanı.
    for n in (10000, 100000):
        fig, ax = plt.subplots(figsize=(10, 4.8))
        genislik = 0.26
        digerler = DAGILIMLAR[1:]
        for i, d in enumerate(digerler):
            ofset = (i - 1) * genislik
            oran = [veri[a, d, n]["sure"] / veri[a, "rastgele", n]["sure"] for a in ALGORITMALAR]
            ax.bar([k + ofset for k in range(len(ALGORITMALAR))], oran, genislik * 0.92,
                   color=DAGILIM_RENK[d], label=DAGILIM_AD[d])
        ax.axhline(1, color=IKINCIL, lw=1, ls="--")
        ax.set_yscale("log")
        ax.set_xticks(range(len(ALGORITMALAR)), [AD[a].replace(" Sort", "") for a in ALGORITMALAR])
        ax.set_ylabel("Süre / rastgele veri süresi (log)")
        ax.set_title(f"Rastgele veriye göre süre oranı, n = {n:,}".replace(",", "."))
        ax.annotate("1 = rastgele veriyle aynı süre", (len(ALGORITMALAR) - 0.5, 1), fontsize=8,
                    color=IKINCIL, ha="right", va="bottom")
        ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.1))
        ax.grid(axis="x", visible=False)
        kaydet(fig, f"{sira}_dagilim_oran_n{n}.png", f"Rastgele veriye göre süre oranı (n={n})",
               "1'in altı: rastgele veriden hızlı; üstü: yavaş.")
        sira += 1


def isi_haritalari(veri):
    """Algoritma × dağılım ısı haritaları (n=100.000)."""
    n = 100000
    for metrik, dosya in (("sure", "40_isi_sure_n100000.png"),
                          ("karsilastirma", "41_isi_karsilastirma_n100000.png"),
                          ("hareket", "42_isi_hareket_n100000.png")):
        deger = [[veri[a, d, n][metrik] for d in DAGILIMLAR] for a in ALGORITMALAR]
        logd = [[math.log10(max(v, 1e-3)) for v in satir] for satir in deger]
        fig, ax = plt.subplots(figsize=(7.4, 4.8))
        im = ax.imshow(logd, cmap="Blues", aspect="auto")
        renk_olcegi = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
        renk_olcegi.set_label("log₁₀(değer); 0 için renk tabanı 0,001")
        ax.grid(False)
        ax.set_xticks(range(4), [DAGILIM_AD[d] for d in DAGILIMLAR])
        ax.set_yticks(range(7), [AD[a] for a in ALGORITMALAR])
        ax.tick_params(length=0)
        for i, satir in enumerate(deger):
            for j, v in enumerate(satir):
                koyu = logd[i][j] > (max(map(max, logd)) + min(map(min, logd))) / 2
                metin = sure_bicimi(v) if metrik == "sure" else sayi_bicimi(v)
                ax.text(j, i, metin, ha="center", va="center", fontsize=8.5,
                        color="#ffffff" if koyu else METIN)
        for kenar in ax.spines.values():
            kenar.set_visible(False)
        ax.set_title(f"{METRIK_AD[metrik]} – n = 100.000 (renk: log ölçek)")
        kaydet(fig, dosya, f"Isı haritası: {METRIK_AD[metrik].lower()} (n=100.000)",
               "Algoritma × dağılım; koyu hücre = yüksek değer.")


def buyume_ve_teori(veri):
    """Teorik Big-O ile deneysel eğilimin karşılaştırılması."""
    # (a) Normalize: süre / n² ve süre / (n log n)
    for d in ("rastgele", "ters_sirali"):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.8))
        for a in ALGORITMALAR:
            y1 = [veri[a, d, n]["sure"] / n ** 2 * 1e6 for n in BOYUTLAR]
            y2 = [veri[a, d, n]["sure"] / (n * math.log2(n)) * 1e6 for n in BOYUTLAR]
            ax1.plot(BOYUTLAR, y1, color=RENK[a], marker=ISARET[a], label=AD[a],
                     markeredgecolor=YUZEY, markeredgewidth=1)
            ax2.plot(BOYUTLAR, y2, color=RENK[a], marker=ISARET[a], label=AD[a],
                     markeredgecolor=YUZEY, markeredgewidth=1)
        for ax, bas in ((ax1, "Süre / n²  (ns)"), (ax2, "Süre / (n·log₂ n)  (ns)")):
            boyut_ekseni(ax)
            ax.set_yscale("log")
            ax.set_ylabel(bas + " (log)")
        ax1.set_title("n² ile normalize edilen ölçümler")
        ax2.set_title("n·log₂ n ile normalize edilen ölçümler")
        tutamaklar, etiketler = ax1.get_legend_handles_labels()
        fig.legend(tutamaklar, etiketler, loc="lower center", ncol=7, bbox_to_anchor=(0.5, -0.04))
        fig.suptitle(f"Normalize süre – {DAGILIM_AD[d]} veri", x=0.01, ha="left",
                     fontsize=13, fontweight="bold")
        fig.tight_layout(rect=(0, 0.03, 1, 0.96))
        kaydet(fig, f"50_normalize_sure_{d}.png", f"Teorik karmaşıklık testi (normalize süre), {DAGILIM_AD[d]}",
               "Sonlu ölçüm aralığındaki eğilim; asimptotik üst sınırın kanıtı değildir.")

    # (b) Ampirik büyüme üssü: log-log eğim (n=10.000 → 100.000)
    for d in DAGILIMLAR:
        fig, ax = plt.subplots(figsize=(8, 4.6))
        n1, n2 = 10000, 100000
        for i, a in enumerate(ALGORITMALAR):
            e = math.log(veri[a, d, n2]["sure"] / veri[a, d, n1]["sure"]) / math.log(n2 / n1)
            ax.bar(i, e, 0.62, color=RENK[a])
            ax.annotate(f"{e:.2f}", (i, e), ha="center", va="bottom", fontsize=8.5,
                        xytext=(0, 3), textcoords="offset points")
        ax.axhline(2, color=IKINCIL, ls="--", lw=1)
        ax.axhline(1, color=IKINCIL, ls=":", lw=1)
        ax.annotate("O(n²) → 2", (6.45, 2), fontsize=8, color=IKINCIL, ha="right", va="bottom")
        ax.annotate("O(n) → 1", (6.45, 1), fontsize=8, color=IKINCIL, ha="right", va="bottom")
        ax.set_xticks(range(7), [AD[a].replace(" Sort", "") for a in ALGORITMALAR])
        ax.set_ylabel("Deneysel büyüme üssü k  (süre ∝ nᵏ)")
        ax.set_title(f"Büyüme üssü, n: 10.000 → 100.000 – {DAGILIM_AD[d]} veri")
        ax.grid(axis="x", visible=False)
        kaydet(fig, f"51_buyume_ussu_{d}.png", f"Deneysel büyüme üssü, {DAGILIM_AD[d]} veri",
               "k = log(t₂/t₁)/log(n₂/n₁); O(n²) için ≈2, O(n log n) için ≈1,1 beklenir.")


def eleman_basina(veri):
    """Shell, Quick, Merge ve Heap için eleman başına ölçümler ve log₂ n referansı."""
    for metrik, ad, dosya in (("karsilastirma", "Eleman başına karşılaştırma", "52_eleman_basi_karsilastirma.png"),
                              ("hareket", "Eleman başına veri hareketi", "53_eleman_basi_hareket.png")):
        fig, ax = plt.subplots(figsize=(7.4, 4.8))
        for a in ("shell", "quick", "merge", "heap"):
            y = [veri[a, "rastgele", n][metrik] / n for n in BOYUTLAR]
            ax.plot(BOYUTLAR, y, color=RENK[a], marker=ISARET[a], label=AD[a],
                    markeredgecolor=YUZEY, markeredgewidth=1)
        log2 = [math.log2(n) for n in BOYUTLAR]
        ax.plot(BOYUTLAR, log2, ls=":", color="#8a8984", lw=1.2)
        ax.annotate("log₂ n", (BOYUTLAR[-1], log2[-1]), fontsize=8, color=IKINCIL,
                    ha="right", va="bottom")
        boyut_ekseni(ax)
        ax.set_ylabel(ad + (" (C/n)" if metrik == "karsilastirma" else " (H/n)"))
        ax.set_title(ad + " – rastgele veri")
        ax.legend(ncol=2, loc="upper left")
        kaydet(fig, dosya, ad + " (Shell, Quick, Merge, Heap)",
               "log₂ n yalnızca referans eğrisidir; Shell için n log n garantisi yoktur.")


def insertion_siralida(veri):
    """Insertion Sort'un sıralı/kısmen sıralı veride avantajı."""
    fig, eksenler = plt.subplots(1, 2, figsize=(12.5, 4.8), sharey=True)
    for ax, d in zip(eksenler, ("sirali", "kismen_sirali")):
        for a in ALGORITMALAR:
            y = [veri[a, d, n]["sure"] for n in BOYUTLAR]
            kalin = a == "insertion"
            ax.plot(BOYUTLAR, y, color=RENK[a], marker=ISARET[a], label=AD[a],
                    lw=3 if kalin else 1.6, zorder=4 if kalin else 2,
                    markeredgecolor=YUZEY, markeredgewidth=1)
        boyut_ekseni(ax)
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(FuncFormatter(sure_ekseni))
        ax.set_title(DAGILIM_AD[d] + " veri")
    eksenler[0].set_ylabel("Ortalama süre (log)")
    tutamaklar, etiketler = eksenler[0].get_legend_handles_labels()
    fig.legend(tutamaklar, etiketler, loc="lower center", ncol=7, bbox_to_anchor=(0.5, -0.04))
    fig.suptitle("Insertion Sort sıralı ve kısmen sıralı veride (kalın çizgi)", x=0.01, ha="left",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    kaydet(fig, "54_insertion_sirali_veri.png", "Insertion Sort'un sıralı veride avantajı",
           "Sıralı veride Insertion yaklaşık O(n) çalışır; O(n log n) algoritmalarla yarışır.")

    # Karşılaştırma sayısı: Insertion sıralıda n-1.
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    for d in DAGILIMLAR:
        y = [veri["insertion", d, n]["karsilastirma"] for n in BOYUTLAR]
        ax.plot(BOYUTLAR, y, color=DAGILIM_RENK[d], marker="o", label=DAGILIM_AD[d],
                markeredgecolor=YUZEY, markeredgewidth=1)
    boyut_ekseni(ax)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(sayi_bicimi))
    ax.set_ylabel("Karşılaştırma sayısı (log)")
    ax.set_title("Insertion Sort: dağılıma göre karşılaştırma sayısı")
    ax.legend(loc="upper left")
    kaydet(fig, "55_insertion_dagilim_karsilastirma.png", "Insertion Sort karşılaştırma sayısı, dört dağılım",
           "Sıralı veride n-1, ters sıralıda ≈ n²/2.")


def kararlilik(veri, ham):
    """Dağılımlar arası süre farkı ve tekrar değişkenliği."""
    n = 100000
    fig, ax = plt.subplots(figsize=(8, 4.8))
    oranlar = []
    for a in ALGORITMALAR:
        suredeger = [veri[a, d, n]["sure"] for d in DAGILIMLAR]
        oranlar.append(max(suredeger) / min(suredeger))
    cubuklar = ax.bar(range(7), oranlar, 0.62, color=[RENK[a] for a in ALGORITMALAR])
    ax.set_yscale("log")
    for c, o in zip(cubuklar, oranlar):
        ax.annotate(f"{o:.1f}×", (c.get_x() + c.get_width() / 2, o), ha="center", va="bottom",
                    fontsize=8.5, xytext=(0, 3), textcoords="offset points")
    ax.set_xticks(range(7), [AD[a].replace(" Sort", "") for a in ALGORITMALAR])
    ax.set_ylabel("En yavaş / en hızlı dağılım süresi (log)")
    ax.set_title("Dağılım duyarlılığı, n = 100.000 (1× = dağılımdan bağımsız)")
    ax.grid(axis="x", visible=False)
    kaydet(fig, "56_dagilim_duyarliligi.png", "Algoritmaların dağılım duyarlılığı",
           "Dört dağılımın ortalama sürelerinin en büyüğü / en küçüğü; eşit anahtar kararlılığıyla ilgili değildir.")

    # Tekrarlar arası değişkenlik (varyasyon katsayısı) n=100.000 rastgele
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for i, a in enumerate(ALGORITMALAR):
        deger = ham[a, "rastgele", n]
        ort = sum(deger) / len(deger)
        std = (sum((v - ort) ** 2 for v in deger) / (len(deger) - 1)) ** 0.5
        ax.bar(i, std / ort * 100, 0.62, color=RENK[a])
        ax.annotate(f"%{std / ort * 100:.1f}", (i, std / ort * 100), ha="center", va="bottom",
                    fontsize=8.5, xytext=(0, 3), textcoords="offset points")
    ax.set_xticks(range(7), [AD[a].replace(" Sort", "") for a in ALGORITMALAR])
    ax.set_ylabel("Varyasyon katsayısı (%)")
    ax.set_title("5 tekrar arasındaki süre değişkenliği, n = 100.000, rastgele")
    ax.grid(axis="x", visible=False)
    kaydet(fig, "57_tekrar_degiskenligi.png", "Tekrarlar arası süre değişkenliği (varyasyon katsayısı)",
           "Beş ölçüm arasındaki standart sapma / ortalama.")


def sure_karsilastirma_iliskisi(ham):
    """Süre ile karşılaştırma+hareket işlem sayısının ilişkisi (tüm ham ölçümler)."""
    fig, ax = plt.subplots(figsize=(7.6, 5))
    islem = defaultdict(list)
    for boyut in BOYUTLAR:
        for s in oku(SONUCLAR / "deneyler" / f"ham_{boyut}.csv"):
            islem[s["algoritma"]].append((sayi(s["karsilastirma_sayisi"]) + sayi(s["hareket_sayisi"]),
                                          sayi(s["sure_ms"])))
    for a in ALGORITMALAR:
        x, y = zip(*islem[a])
        ax.scatter(x, y, s=14, color=RENK[a], marker=ISARET[a], alpha=0.7, label=AD[a],
                   edgecolors="none")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(sayi_bicimi))
    ax.yaxis.set_major_formatter(FuncFormatter(sure_ekseni))
    ax.set_xlabel("Toplam işlem sayısı (karşılaştırma + hareket, log)")
    ax.set_ylabel("Süre (log)")
    ax.set_title("Süre ile sayaç toplamının birlikte değişimi")
    ax.legend(ncol=2, loc="upper left", markerscale=1.4)
    kaydet(fig, "58_sure_islem_iliskisi.png", "Süre – toplam işlem sayısı ilişkisi",
           "840 ham kayıt; sayaç toplamı farklı işlemlerin maliyetini eşitlemez ve nedensellik kanıtlamaz.")


def pivot_bonusu():
    """Bonus 1: Quick Sort orta vs ilk eleman pivotu."""
    satirlar = oku(SONUCLAR / "bonuslar" / "pivot_ozet.csv")
    veri = {(s["pivot_yontemi"], s["veri_tipi"], int(s["boyut"])): s for s in satirlar}
    boyutlar = sorted({b for _, _, b in veri})
    renk = {"orta": "#2a78d6", "ilk": "#eb6834"}
    ad = {"orta": "Orta eleman", "ilk": "İlk eleman"}
    for metrik, alan, baslik in (("sure", "ortalama_sure_ms", "Süre"),
                                 ("karsilastirma", "ortalama_karsilastirma", "Karşılaştırma sayısı")):
        fig, eksenler = plt.subplots(2, 2, figsize=(11, 7.6), sharex=True)
        for ax, d in zip(eksenler.flat, DAGILIMLAR):
            for p in ("orta", "ilk"):
                y = [sayi(veri[p, d, n][alan]) for n in boyutlar]
                ax.plot(boyutlar, y, color=renk[p], marker="o" if p == "orta" else "s", label=ad[p],
                        markeredgecolor=YUZEY, markeredgewidth=1)
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xticks(boyutlar)
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
            ax.minorticks_off()
            ax.yaxis.set_major_formatter(FuncFormatter(
                sure_ekseni if metrik == "sure" else sayi_bicimi))
            ax.set_title(DAGILIM_AD[d])
            ax.set_ylabel(baslik + " (log)")
        for ax in eksenler[1]:
            ax.set_xlabel("Veri boyutu n (log)")
        tutamaklar, etiketler = eksenler[0, 0].get_legend_handles_labels()
        fig.legend(tutamaklar, etiketler, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.01))
        fig.suptitle(f"Bonus 1 – Quick Sort pivot karşılaştırması: {baslik.lower()}", x=0.01,
                     ha="left", fontsize=13, fontweight="bold")
        fig.tight_layout(rect=(0, 0.04, 1, 0.97))
        kaydet(fig, f"60_pivot_{metrik}.png", f"Quick Sort pivot: {baslik.lower()}",
               "Orta ve ilk eleman pivotu, dört dağılım; ilk pivot sıralı veride O(n²).")

    # Çubuk: n=10.000'de oran
    n = boyutlar[-1]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    oran = [sayi(veri["ilk", d, n]["ortalama_sure_ms"]) / sayi(veri["orta", d, n]["ortalama_sure_ms"])
            for d in DAGILIMLAR]
    cub = ax.bar(range(4), oran, 0.6, color=[DAGILIM_RENK[d] for d in DAGILIMLAR])
    ax.axhline(1, color=IKINCIL, ls="--", lw=1)
    ax.set_yscale("log")
    for c, o in zip(cub, oran):
        ax.annotate(f"{o:.1f}×", (c.get_x() + c.get_width() / 2, o), ha="center", va="bottom",
                    fontsize=9, xytext=(0, 3), textcoords="offset points")
    ax.set_xticks(range(4), [DAGILIM_AD[d] for d in DAGILIMLAR])
    ax.set_ylabel("İlk pivot süresi / orta pivot süresi (log)")
    ax.set_title(f"İlk pivot, orta pivota göre kaç kat yavaş? (n = {n:,})".replace(",", "."))
    ax.grid(axis="x", visible=False)
    kaydet(fig, "61_pivot_oran.png", "İlk pivot / orta pivot süre oranı",
           "1'in üzeri: ilk eleman pivotu daha yavaş.")


def gap_bonusu():
    """Bonus 2: Shell Sort klasik (n/2) vs Knuth gap dizisi."""
    satirlar = oku(SONUCLAR / "bonuslar" / "gap_ozet.csv")
    veri = {(s["gap_yontemi"], s["veri_tipi"], int(s["boyut"])): s for s in satirlar}
    boyutlar = sorted({b for _, _, b in veri})
    renk = {"klasik": "#2a78d6", "knuth": "#eb6834"}
    ad = {"klasik": "Klasik (n//2, sonra gap//2)", "knuth": "Knuth (1, 4, 13, 40, …)"}
    for metrik, alan, baslik in (("sure", "ortalama_sure_ms", "Süre"),
                                 ("karsilastirma", "ortalama_karsilastirma", "Karşılaştırma sayısı"),
                                 ("hareket", "ortalama_hareket", "Veri hareketi")):
        fig, eksenler = plt.subplots(2, 2, figsize=(11, 7.6), sharex=True)
        for ax, d in zip(eksenler.flat, DAGILIMLAR):
            for g in ("klasik", "knuth"):
                y = [sayi(veri[g, d, n][alan]) for n in boyutlar]
                ax.plot(boyutlar, y, color=renk[g], marker="o" if g == "klasik" else "s", label=ad[g],
                        markeredgecolor=YUZEY, markeredgewidth=1)
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xticks(boyutlar)
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
            ax.minorticks_off()
            ax.yaxis.set_major_formatter(FuncFormatter(
                sure_ekseni if metrik == "sure" else sayi_bicimi))
            ax.set_title(DAGILIM_AD[d])
            ax.set_ylabel(baslik + " (log)")
        for ax in eksenler[1]:
            ax.set_xlabel("Veri boyutu n (log)")
        tutamaklar, etiketler = eksenler[0, 0].get_legend_handles_labels()
        fig.legend(tutamaklar, etiketler, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.01))
        fig.suptitle(f"Bonus 2 – Shell Sort gap karşılaştırması: {baslik.lower()}", x=0.01,
                     ha="left", fontsize=13, fontweight="bold")
        fig.tight_layout(rect=(0, 0.04, 1, 0.97))
        kaydet(fig, f"62_gap_{metrik}.png", f"Shell Sort gap dizisi: {baslik.lower()}",
               "Klasik ve Knuth gap dizisi, dört dağılım.")

    n = boyutlar[-1]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    oran = [sayi(veri["klasik", d, n]["ortalama_sure_ms"]) / sayi(veri["knuth", d, n]["ortalama_sure_ms"])
            for d in DAGILIMLAR]
    cub = ax.bar(range(4), oran, 0.6, color=[DAGILIM_RENK[d] for d in DAGILIMLAR])
    ax.axhline(1, color=IKINCIL, ls="--", lw=1)
    for c, o in zip(cub, oran):
        ax.annotate(f"{o:.2f}×", (c.get_x() + c.get_width() / 2, o), ha="center", va="bottom",
                    fontsize=9, xytext=(0, 3), textcoords="offset points")
    ax.set_xticks(range(4), [DAGILIM_AD[d] for d in DAGILIMLAR])
    ax.set_ylabel("Klasik süre / Knuth süre")
    ax.set_title(f"Knuth gap'i klasiğe göre kaç kat hızlı? (n = {n:,})".replace(",", "."))
    ax.grid(axis="x", visible=False)
    kaydet(fig, "63_gap_oran.png", "Klasik / Knuth süre oranı",
           "1'in üzeri: Knuth dizisi daha hızlı.")


def buyuk_veri_bonusu():
    """Bonus 3: n = 500.000."""
    satirlar = oku(SONUCLAR / "bonuslar" / "buyuk_veri_ozet.csv")
    algolar = ["shell", "quick", "merge", "heap"]
    veri = {(s["algoritma"], s["veri_tipi"]): s for s in satirlar}
    for alan, baslik, dosya in (("ortalama_sure_ms", "Süre", "70_buyuk_veri_sure.png"),
                                ("ortalama_karsilastirma", "Karşılaştırma sayısı", "71_buyuk_veri_karsilastirma.png"),
                                ("ortalama_hareket", "Veri hareketi", "72_buyuk_veri_hareket.png")):
        fig, ax = plt.subplots(figsize=(10, 4.8))
        genislik = 0.2
        for i, d in enumerate(DAGILIMLAR):
            y = [sayi(veri[a, d][alan]) for a in algolar]
            ax.bar([k + (i - 1.5) * genislik for k in range(4)], y, genislik * 0.92,
                   color=DAGILIM_RENK[d], label=DAGILIM_AD[d])
        ax.set_xticks(range(4), [AD[a] for a in algolar])
        ax.yaxis.set_major_formatter(FuncFormatter(
            sure_ekseni if alan == "ortalama_sure_ms" else sayi_bicimi))
        ax.set_ylabel(baslik)
        ax.set_title(f"Bonus 3 – n = 500.000: {baslik.lower()}")
        ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1))
        ax.grid(axis="x", visible=False)
        kaydet(fig, dosya, f"n=500.000: {baslik.lower()}", "Shell, Quick, Merge, Heap; dört dağılım.")

    # 100.000 → 500.000 büyüme çarpanı (rastgele)
    ozet100 = {s["algoritma"]: sayi(s["ortalama_sure_ms"])
               for s in oku(SONUCLAR / "deneyler" / "ozet_100000.csv") if s["veri_tipi"] == "rastgele"}
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    for i, a in enumerate(algolar):
        kat = sayi(veri[a, "rastgele"]["ortalama_sure_ms"]) / ozet100[a]
        ax.bar(i, kat, 0.6, color=RENK[a])
        ax.annotate(f"{kat:.1f}×", (i, kat), ha="center", va="bottom", fontsize=9,
                    xytext=(0, 3), textcoords="offset points")
    ax.axhline(5, color=IKINCIL, ls=":", lw=1.2, label="Doğrusal model: 5×")
    model_orani = 5 * math.log(500000) / math.log(100000)
    ax.axhline(model_orani, color=IKINCIL, ls="--", lw=1,
               label=f"n·log n modeli: {model_orani:.2f}× (tahmin)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
    ax.set_xticks(range(4), [AD[a] for a in algolar])
    ax.set_ylabel("Süre(500.000) / Süre(100.000)")
    ax.set_title("n beş katına çıkınca süre kaç kat arttı? (rastgele veri)")
    ax.grid(axis="x", visible=False)
    kaydet(fig, "73_buyuk_veri_buyume.png", "100.000 → 500.000 süre büyüme çarpanı",
           "n·log n teorisinin ölçüyle karşılaştırması.")


def bellek_grafikleri():
    """Ek bellek kullanımı (tracemalloc)."""
    satirlar = [s for s in oku(SONUCLAR / "bellek_sonuclari.csv") if s["basarili_mi"] == "True"]
    veri = {(s["algoritma"], s["veri_tipi"], int(s["boyut"])): sayi(s["olculen_tepe_bellek_kib"])
            for s in satirlar}
    boyutlar = sorted({b for _, _, b in veri})
    for n in boyutlar:
        algolar = [a for a in ALGORITMALAR if (a, "rastgele", n) in veri]
        fig, ax = plt.subplots(figsize=(8, 4.8))
        for i, a in enumerate(algolar):
            y = veri[a, "rastgele", n]
            ax.bar(i, y, 0.62, color=RENK[a])
            ax.annotate(f"{y:.2f} KiB" if y < 100 else f"{y:,.0f} KiB".replace(",", "."), (i, y),
                        ha="center", va="bottom", fontsize=8.5, xytext=(0, 3), textcoords="offset points")
        ax.set_yscale("log")
        ax.set_xticks(range(len(algolar)), [AD[a].replace(" Sort", "") for a in algolar])
        ax.set_ylabel("Ölçülen tepe ek bellek (KiB, log)")
        ax.set_title(f"Ek bellek kullanımı, n = {n:,} (rastgele veri)".replace(",", "."))
        ax.grid(axis="x", visible=False)
        kaydet(fig, f"80_bellek_n{n}.png", f"Ek bellek kullanımı (n={n})",
               "tracemalloc ile ölçülen tepe Python tahsisi; Merge O(n) tampon nedeniyle öne çıkar.")

    if len(boyutlar) > 1:
        fig, ax = plt.subplots(figsize=(7.6, 4.8))
        for a in ("shell", "quick", "merge", "heap"):
            y = [veri[a, "rastgele", n] for n in boyutlar if (a, "rastgele", n) in veri]
            ax.plot(boyutlar, y, color=RENK[a], marker=ISARET[a], label=AD[a],
                    markeredgecolor=YUZEY, markeredgewidth=1)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xticks(boyutlar)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
        ax.minorticks_off()
        ax.set_xlabel("Veri boyutu n (log)")
        ax.set_ylabel("Tepe ek bellek (KiB, log)")
        ax.set_title("İki boyutta ölçülen tepe Python tahsisleri")
        ax.legend(loc="upper left")
        kaydet(fig, "81_bellek_buyume.png", "Ek bellek büyümesi",
               "İki boyutun karşılaştırılması; tek başına alan karmaşıklığını kanıtlamaz.")


def paralel_merge_bonusu():
    """Bonus 4: Amdahl yasası ile teorik paralel Merge Sort."""
    satirlar = oku(SONUCLAR / "analizler" / "paralel_merge_teorik.csv")
    teorik = [s for s in satirlar if s["kayit_turu"] == "teorik_tahmin"]
    oranlar = sorted({sayi(s["paralel_oran_f"]) for s in teorik})
    # Amdahl eğrisi: S(p) = 1 / ((1-f) + f/p) – dosyadaki f değerleriyle.
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    p_deger = list(range(1, 65))
    for f, renk in zip(oranlar, ("#2a78d6", "#eb6834", "#1baf7a", "#6250d6")):
        ax.plot(p_deger, [1 / ((1 - f) + f / p) for p in p_deger], color=renk, label=f"f = {f:g}")
    ax.plot(p_deger, p_deger, ls=":", color="#8a8984", lw=1.2)
    ax.annotate("ideal (doğrusal)", (60, 60), fontsize=8, color=IKINCIL, ha="right", va="bottom")
    ax.set_xlabel("Çalışan sayısı p")
    ax.set_ylabel("Teorik hızlanma S(p)")
    ax.set_title("Bonus 4 – Amdahl yasası: paralel Merge Sort (teorik)")
    ax.legend(title="Paralel kesir", loc="upper left")
    kaydet(fig, "90_paralel_amdahl.png", "Amdahl hızlanma eğrisi (teorik)",
           "Gerçek paralel ölçüm değildir; yalnızca teorik modeldir.")

    boyutlar = sorted({int(s["boyut"]) for s in teorik})
    fig, ax = plt.subplots(figsize=(8, 4.8))
    gercek = {int(s["boyut"]): sayi(s["sure_ms"]) for s in satirlar
              if s["kayit_turu"] == "gercek_sirali_olcum"}
    calisanlar = sorted({int(s["calisan_sayisi"]) for s in teorik})
    ax.plot(boyutlar, [gercek[n] for n in boyutlar], color="#0b0b0b", marker="o",
            label="Ölçülen sıralı (1 çalışan)", lw=2.4)
    palet = ("#2a78d6", "#eb6834", "#1baf7a")
    for p, renk in zip(calisanlar, palet):
        y = [sayi(s["sure_ms"]) for n in boyutlar for s in teorik
             if int(s["boyut"]) == n and int(s["calisan_sayisi"]) == p]
        ax.plot(boyutlar, y, color=renk, marker="s", ls="--", label=f"Teorik, {p} çalışan")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(boyutlar)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
    ax.minorticks_off()
    ax.yaxis.set_major_formatter(FuncFormatter(sure_ekseni))
    ax.set_xlabel("Veri boyutu n (log)")
    ax.set_ylabel("Süre (log)")
    ax.set_title("Merge Sort: ölçülen sıralı süre ve teorik paralel tahminler")
    ax.legend(loc="upper left")
    kaydet(fig, "91_paralel_sure_tahmini.png", "Ölçülen sıralı ve teorik paralel Merge süresi",
           "Kesikli çizgiler Amdahl modelinden hesaplanmış varsayımsal süreler.")


def liste_yaz():
    satir = ["# Grafik listesi", "",
             "Bu dosya `python -m gorsellestirme.grafikler` tarafından otomatik üretilir.", "",
             "| Dosya | Başlık | Açıklama |", "| --- | --- | --- |"]
    satir += [f"| `{d}` | {b} | {a} |" for d, b, a in LISTE]
    (CIKTI / "grafik_listesi.md").write_text("\n".join(satir) + "\n", encoding="utf-8")


def main():
    grafikOrtaminiHazirla()
    LISTE.clear()
    veri = ozet_yukle()
    ham = ham_yukle()
    boyuta_gore(veri)
    hizli_algoritmalar(veri)
    kareseller_ve_hizlilar(veri)
    dagilim_etkisi(veri)
    isi_haritalari(veri)
    buyume_ve_teori(veri)
    eleman_basina(veri)
    insertion_siralida(veri)
    kararlilik(veri, ham)
    sure_karsilastirma_iliskisi(ham)
    pivot_bonusu()
    gap_bonusu()
    buyuk_veri_bonusu()
    bellek_grafikleri()
    paralel_merge_bonusu()
    liste_yaz()
    print(f"\nToplam {len(LISTE)} grafik: {CIKTI}")


if __name__ == "__main__":
    main()
