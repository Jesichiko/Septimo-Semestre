Un **display numérico** es un dispositivo electrónico para **representar números decimales.** Dependiendo de cuantos digitos pueda representar, la cantidad maxima de posibles combinaciones de estos aumenta.

El **display numérico de 7 segmentos** es el display más común para poder representar un dígito. Este está formado por **7 segmentos** que se pueden encender o apagar para formar distintos números. 

![[Pasted image 20250906234157.png]]

Estos segmentos están representados con **letras**:
![[Pasted image 20250906234551.png]]
 Podemos representar (como en [[Sumadores booleanos]]) un display de 7 segmentos con **funciones booleanas para representar cada numero único con combinaciones de entradas distintas**: 

| $a$ | $b$ | $c$ | $d$ | $e$ | $f$ | $g$ | $\|$ | $f_1$ | $f_2$ | $f_3$ | $f_4$ | $f_5$ | $f_6$ | $f_7$ | $f_8$ | $f_9$ |
| --- | :-- | --- | --- | --- | --- | --- | ---- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| 0   | 1   | 1   | 0   | 0   | 0   | 0   |      | 1     | 0     | 0     | 0     | 0     | 0     | 0     | 0     | 0     |
| 1   | 1   | 0   | 1   | 1   | 0   | 1   |      | 0     | 1     | 0     | 0     | 0     | 0     | 0     | 0     | 0     |
| 1   | 1   | 1   | 1   | 0   | 0   | 1   |      | 0     | 0     | 1     | 0     | 0     | 0     | 0     | 0     | 0     |
| 0   | 1   | 1   | 0   | 0   | 1   | 1   |      | 0     | 0     | 0     | 1     | 0     | 0     | 0     | 0     | 0     |
| 1   | 0   | 1   | 1   | 0   | 1   | 1   |      | 0     | 0     | 0     | 0     | 1     | 0     | 0     | 0     | 0     |
| 0   | 0   | 1   | 1   | 1   | 1   | 1   |      | 0     | 0     | 0     | 0     | 0     | 1     | 0     | 0     | 0     |
| 1   | 1   | 1   | 0   | 0   | 0   | 1   |      | 0     | 0     | 0     | 0     | 0     | 0     | 1     | 0     | 0     |
| 1   | 1   | 1   | 1   | 1   | 1   | 1   |      | 0     | 0     | 0     | 0     | 0     | 0     | 0     | 1     | 0     |
| 1   | 1   | 1   | 0   | 0   | 1   | 1   |      | 0     | 0     | 0     | 0     | 0     | 0     | 0     | 0     | 1     |

Esto nos deja las siguientes funciones con sus reglas de correspondencia:
$$f_1=\bar{a}bc\bar{d}\bar{e}\bar{f}\bar{g}$$
$$f_2=ab\bar{c}de\bar{f}g$$
$$f_3=abcd\bar{e}\bar{f}g$$
$$f_4=\bar{a}bc\bar{d}\bar{e}fg$$
$$f_5=a\bar{b}cd\bar{e}fg$$
$$f_6=\bar{a}\bar{b}cdefg$$
$$f_7=abc\bar{d}\bar{e}\bar{f}g$$
$$f_8=abcdefg$$
$$f_9=abc\bar{d}\bar{e}fg$$
Para **entradas binarias** que representen el número a mostrar podemos **crear funciones booleanas** que expresen con que combinaciones de entradas binario se tiene que prender. 

| $x$ | $y$ | $z$ | $w$ | $\|$ | $a$ | $b$ | $c$ | $d$ | $e$ | $f$ | $g$ | $pd$ |
| --- | --- | --- | --- | ---- | --- | :-- | --- | --- | --- | --- | --- | ---- |
| 0   | 0   | 0   | 0   |      | 0   | 1   | 1   | 0   | 0   | 0   | 0   | 0    |
| 0   | 0   | 0   | 1   |      | 1   | 1   | 0   | 1   | 1   | 0   | 1   | 0    |
| 0   | 0   | 1   | 0   |      | 1   | 1   | 1   | 1   | 0   | 0   | 1   | 0    |
| 0   | 0   | 1   | 1   |      | 0   | 1   | 1   | 0   | 0   | 1   | 1   | 0    |
| 0   | 1   | 0   | 0   |      | 1   | 0   | 1   | 1   | 0   | 1   | 1   | 0    |
| 0   | 1   | 0   | 1   |      | 0   | 0   | 1   | 1   | 1   | 1   | 1   | 0    |
| 0   | 1   | 1   | 0   |      | 1   | 1   | 1   | 0   | 0   | 0   | 1   | 0    |
| 0   | 1   | 1   | 1   |      | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 0    |
| 1   | 0   | 0   | 0   |      | 1   | 1   | 1   | 0   | 0   | 1   | 1   | 0    |
| 1   | 0   | 0   | 1   |      | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 1    |
| 1   | 0   | 1   | 0   |      | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 1    |
| 1   | 0   | 1   | 1   |      | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 1    |
| 1   | 1   | 0   | 0   |      | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 1    |
| 1   | 1   | 0   | 1   |      | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 1    |
| 1   | 1   | 1   | 0   |      | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 1    |
| 1   | 1   | 1   | 1   |      | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 1    |
Esto resulta en las funciones:
$$f_a=\bar{x}\bar{y}\bar{z}w+\bar{x}\bar{y}z\bar{w}+\bar{x}y\bar{z}\bar{w}+\bar{x}zy\bar{w}+\bar{x}yzw+x\bar{y}\bar{z}\bar{w}$$
$$=$$