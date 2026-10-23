on run argv
    set belgeYolu to item 1 of argv
    tell application "Microsoft Word"
        open file name belgeYolu
        set raporBelgesi to active document
        repaginate raporBelgesi
        repeat with icerikTablosu in (get tables of contents of raporBelgesi)
            update icerikTablosu
        end repeat
        repaginate raporBelgesi
        repeat with icerikTablosu in (get tables of contents of raporBelgesi)
            update page numbers icerikTablosu
            set color index of font object of text object of icerikTablosu to black
            set font size of font object of text object of icerikTablosu to 12
        end repeat
        set sayfaSayisi to compute statistics raporBelgesi statistic statistic pages
        save raporBelgesi
        return "Sayfa=" & sayfaSayisi & "; Icındekiler=" & (count tables of contents of raporBelgesi)
    end tell
end run
