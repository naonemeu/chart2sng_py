# About
A Python 3 script that converts from the .chart (Clone Hero) to the .sng/xml (Freetar Editor) format. No real utility unless you still happen to play Guitar Flash, for whatever reason...

The only publicly existing\* chart -> sng is inside a executable that no longer works (at least on my end, due to dll errors), and it had some major issues, like:
* Notes would drift away and desync if the chart had any BPM variations during the song
* Would convert special notes alongside normal ones
* Didn't convert Star Power
This script addresses all those issues, while also automatically parsing song info data from the .chart file

\*in such a case there's a private/internal one.

# Note
Seems to work perfectly as long all BPM changes happens during a note. It may not work well with charts that have too many BPM variations in empty parts.

# Informações extras (Português)
No video anterior fiz o "sng2chart", e ai tive a ideia de fazer o inverso. 
Um pouco de dor de cabeça e ta ai: "chart2sng"

Há muito tempo atrás, eu usava um conversor que tinha no Guitar Flash Custom antigo, mas tinha alguns problemas, como:

* Problema de sincronia com chart que tinhas variações de BPM
* Convertia nota forçada junto com as normais
* Não convertia Star Power

Esse script resolve tudo isso ai, mas fica  como um "experimento", até porque eu não jogo o Guitar Flash seriamente faz muito tempo. 
O resto do vídeo é uma demonstração de como fica uma chart convertida com esse script

Link: https://github.com/naonemeu/chart2sng_py
