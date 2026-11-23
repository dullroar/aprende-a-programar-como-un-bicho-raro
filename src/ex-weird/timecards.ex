" El programa completo, como comandos de Ex. Ex lo lee por la entrada estándar; el búfer contiene cinco dados, un dígito por línea.
" Run:  printf '7\n3\n9\n0\n5\n' > dice.txt; ex -s dice.txt < timecards.ex      (nvi; for Vim: ex -s -u NONE)
" En este archivo no hay comando global, ni prueba de expresión regular, ni instrucción de bucle.
"
" 1. Las categorías son DIRECCIONES, como en la entrada de ed. Varios comandos pueden compartir una línea, separados por una barra.
1s/^/Meetings /|2s/^/Coding /|3s/^/Debugging /|4s/^/Learning /|5s/^/Meetings /
"
" 2. La CINTA: sesenta líneas bajo las tarjetas. Cada línea es  "total instrucción".  La posición de una línea es un número, y
"    una MARCA es un registro: la marca t dice dónde estamos en la cinta. Hasta un total de 40 la instrucción es "@a" (seguir).
"    Por encima de 40 es una comilla, que Ex lee como un comentario (no hacer nada). El límite de 40 es donde termina @a.
5a
0 @a
1 @a
2 @a
3 @a
4 @a
5 @a
6 @a
7 @a
8 @a
9 @a
10 @a
11 @a
12 @a
13 @a
14 @a
15 @a
16 @a
17 @a
18 @a
19 @a
20 @a
21 @a
22 @a
23 @a
24 @a
25 @a
26 @a
27 @a
28 @a
29 @a
30 @a
31 @a
32 @a
33 @a
34 @a
35 @a
36 @a
37 @a
38 @a
39 @a
40 @a
41 "
42 "
43 "
44 "
45 "
46 "
47 "
48 "
49 "
50 "
51 "
52 "
53 "
54 "
55 "
56 "
57 "
58 "
59 "
.
/^0 /k t
"
" 3. El PROGRAMA es la línea que sigue al próximo comando "a". Es texto. Se añade al búfer, se copia en el registro a,
"    y se quita de nuevo. El registro a es lo que ejecuta "@a". Lee las barras como saltos de línea; cada paso se explica aquí:
"      1t$                          copia la primera tarjeta ("Meetings 7") al final del búfer
"      $s/^.* \([0-9]\)$/'t+1\1k t/   reescribe esa copia como un COMANDO:  'tmarca más 17 líneas, guardado como la marca t
"      $ya d  y  $d                  copia el comando en el registro d y lo quita del búfer
"      1s/ \([0-9]\)$/ 1\1/          convierte el dígito de la tarjeta en horas:  "Meetings 17"
"      @d                           ejecuta el registro d: la marca t baja 17 líneas por la cinta. ESA ES LA SUMA
"      1t$ , 'tt$ , $s/ .*$// , $-1,$j , $p
"                                   copia la tarjeta, copia la línea de la cinta bajo la marca t, conserva solo su total,
"                                   júntalos en "Meetings 17 17" e imprímelo
"      'tt$ , $s/^[0-9]* // , $ya n , $d
"                                   copia otra vez la línea de la cinta, conserva solo su instrucción, cópiala en el registro n
"      1d                           la tarjeta queda gastada
"      @n                           ejecuta el registro n: "@a" vuelve a ejecutar el programa, un comentario lo termina. ESE ES EL BUCLE
$k s
$a
1t$|$s/^.* \([0-9]\)$/'t+1\1k t/|$ya d|$d|1s/ \([0-9]\)$/ 1\1/|@d|1t$|'tt$|$s/ .*$//|$-1,$j|$p|'tt$|$s/^[0-9]* //|$ya n|$d|1d|@n
.
's+1ya a
's+1d
"
" 4. Ponlo en marcha.
@a
q!
