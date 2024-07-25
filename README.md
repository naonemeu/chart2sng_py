# English
## About
A Python 3 script that converts from the .chart (Clone Hero) to the .sng/xml (Freetar Editor) format. No real utility unless you still happen to play Guitar Flash, for whatever reason...

The only publicly existing\* chart -> sng is inside a executable that no longer works (at least on my end, due to dll errors), and it had some major issues, like:
* Notes would drift away and desync if the chart had any BPM variations during the song
* Would convert forced notes alongside normal ones (this converter ignores the forced/tap note flag)
* Didn't convert Star Power

This script addresses all those issues, while also automatically parsing song info data from the .chart file

\*in such a case there's a private/internal one.

## Note
Seems to work perfectly as long all BPM changes happens during a note. It may not work well with charts that have too many BPM variations in empty parts.

## Note for Guitar Flash Custom creators
Free to use, regardless of who you are. Just follow the license, I guess?

# Português
## Sobre
Um script de Python 3 que converte do formato .chart (Clone Hero) para .sng/xml (Freetar Editor). Não tem uma utilidade real, a não ser que por qualquer motivo você ainda jogue Guitar Flash...

O unico convesor que existe PUBLICAMENTE\* chart -> sng está dentro de um executavel que não funciona mais (pelo menos pra mim, por causa de erros de DLL) e tinha alguns problemas, como:
* Notas ficavam atrasadas e fora do tempo se tivessem qualquer variação de BPM durante a música.
* Convertia notas forçadas junto com as normais (esse conversor ignora indicadores de nota forçada/flag)
* Não convertia star power

Esse script corrige todos esses problemas, e também coloca os dados no arquivo de saida a partir dos dados do arquivo .chart

\*Caso exista algum conversor privado que seja melhor.

## Nota
Funciona perfeitamente, desde que todos os pontos de BPM sejam juntos com um nota. Para pontos de BPM sem nota no meio, pode dessincronizar a chart.

## Note para criadores do Guitar Flash Custom.
Uso livre, independente de quem você seja. Só siga a licenca, eu acho?
