"""Dizilerin sıralama doğruluğunu kontrol eden yardımcılar."""


def isSorted(dizi):
    # Yan yana iki elemanın sırası bozuksa dizi sıralı değildir.
    for sira in range(len(dizi) - 1):
        if dizi[sira] > dizi[sira + 1]:
            return False
    return True
