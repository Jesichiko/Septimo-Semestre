**Obs** Las MT son modelos matemáticos de cómputo (i.e. algoritmos). Hay otros y todos éstos tratan de responder a la pregunta ¿Qué es calcular? ¿Que hace una computadora?

Otra maquinaria (teoría) son las maquinas de registros ilimitados (URM)
*Unlimited register machine, 1952*

Estas dos son equivalentes a las **MT** (POR Tesis de Turing-Church).
Las URM consisten de:
- Hardware
	- Cantidad finita de registros etiquetados con $R_1, R_2, R_3$
	- Cada $R_i$ contiene un número natural $N = \{0, 1, 2, 3, ...\}$ denotados como $r_i$
 Tales registros se representan como:

| $R_1$ | $R_2$ | $R_3$ | $R_4$ | $...$ |
| ----- | ----- | ----- | ----- | ----- |
| $r_1$ | $r_2$ | $r_3$ | $r_4$ | $...$ |
- Software: El contenido de los registros puede altearse con las siguientes instrucciones.

**Instrucción cero**: para cada $n = 1, 2, 3, ...$ existe una **instrucción cero**, denotada como $Z(m)$ que cuando se aplica el contenido de $R_n$ se cambia a 0 y los demás registros permanecen alterados:$$ 0^{ \ r_n \ := \ 0} \to R_n$$
**Ejemplo.** Sup. que la URM con la siguiente configuración:

| $R_1$ | $R_2$ | $R_3$ | $R_4$ | $R_5$ | $R_6$ | $R_7$ | $...$ |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| 0     | 6     | 5     | 24    | 7     | 0     | 0     | $...$ |
Si aplicamos $Z(3)$ y la configuración cambia a:

| $R_1$ | $R_2$ | $R_3$ | $R_4$ | $...$ |
| ----- | ----- | ----- | ----- | ----- |
| 9     | 6     | **0** | 7     | $...$ |
Esto se puede simbolizar como $r_3  \ := 0$

**Instrucción sucesor**: Sintaxis para cada $n = S(n)$, semántica $r_n := r_n +1, r_n+1 \to R_n$
**Ejemplo:** Sup. configuración inicial de URM y aplicamos $S(4)$: la configuración cambia a:

| $R_1$ | $R_2$ | $R_3$ | $R_4$  | $R_5$ | $R_6$ | $R_7$ | $...$ |
| ----- | ----- | ----- | ------ | ----- | ----- | ----- | ----- |
| 0     | 6     | 5     | **25** | 7     | 0     | 0     | $...$ |
