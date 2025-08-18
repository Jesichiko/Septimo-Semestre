**Recordar: _[[Instrucciones de URMs]]_**.

1) Un **programa** (_URM_) $P$ es una sucesión finita de instrucciones _URM_, escrita, generalmente de forma vertical:
	$P: \ \  \ I_1$
	    $I_2$
	    $I_3$
		$I_4$
		$...$
		$I_s$
2) Una configuración de una _URM_ es una sucesión infinita de números naturales:

| $R_1$ | $R_2$ | $R_3$ | $R_4$ | $...$ |
| ----- | ----- | ----- | ----- | ----- |
| $a_1$ | $a_2$ | $a_3$ | $a_4$ | $...$ |
	que corresponde al contenido de los registros $R_1, R_2, R_3, ...$ etc, respectivamente.

**Obs**. Para hacer un cálculo, en una URM se requiere de:
1. Configuración inicial
2. Un programa $P: \ \ \ \ \ I_1$
					$I_2$
					$I_3$
					$I_4$
					$...$
					$I_s$
La ejecución del programa comienza obedeciendo $I_1$, luego $I_2$, excepto si se encuentra con una instrucción de **salto**.

La ejecución **termina únicamente ** cuando no se encuentra una instrucción siguiente.
Ejemplo**. 
Programa inicial:
$P: \ \ \ \ J(1,2,6)$
	$S(2)$
	$S(3)$
	$J(1, 2, 6)$
	$J(1,1,2)$
	$T(3,1)$
Configuración inicial:

| $R_1$ | $R_2$ | $R_3$ | $R_4$ | $R_5$ | $R_6$ | $R_7$ | $...$ |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| 9     | 7     | 0     | 0     | 0     | 0     | 0     | $...$ |
Si ejecutamos el programa y  observemos el cambio de configuraciones, en una tabla:

|       | $R_1$ | $R_2$ | $R_3$ | $R_4$ | $R_5$ | $...$ | next         |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ------------ |
| start | 9     | 7     | 0     | 0     | 0     | $...$ | $J(1, 2, 6)$ |
|       | 9     | 7     | 0     | 0     | 0     | $...$ | $S(2)$       |
|       | 9     | 8     | 0     | 0     | 0     | $...$ | $S(3)$       |
|       | 9     | 8     | 1     | 0     | 0     | $...$ | $J(1,2,6)$   |
|       | 9     | 8     | 1     | 0     | 0     | $...$ | $J(1,1,2)$   |
|       | 9     | 8     | 1     | 0     | 0     | $...$ | $S(2)$       |
|       | 9     | 9     | 1     | 0     | 0     | $...$ | $S(3)$       |
|       | 9     | 9     | 2     | 0     | 0     | $...$ | $J(1,2,6)$   |
|       | 9     | 9     | 2     | 0     | 0     | $...$ | $T(3,1)$     |
|       | 2     | 9     | 2     | 0     | 0     | ...   | stop         |
Instrucciones del tipo $J(1,1,2)$ se les llama **saltos incondicionales** y **siempre son verdad**.

**Obs**. Hay programas que nunca terminan, ejemplo:
$P: J(1,1,1)$

**Notación**. Sean $r_1,r_2,r_3,...$, sucesión infinita de números reales y un prograam *URM*. Con $P(r_1, r_2, r_3, ...)$ se indica el calculo de $P$ con la configuración inicial:

| $R_1$ | $R_2$ | $R_3$ | $R_4$ | $R_5$ | $...$ |
| ----- | ----- | ----- | ----- | ----- | ----- |
| $r_1$ | $r_2$ | $r_3$ | $r_4$ | $r_5$ | $...$ |

Con $P(r_1, r_2, r_3, ...) \uparrow$ que la máquina nunca para. En tal caso se dice que **el cálculo diverge.**
Con $P(r_1, r_2, r_3, ...) \downarrow$ que la máquina para con la configuración dada y programa $P$ dado. En tal caso se dice que **el cálculo converge**.

**Obs**. En las configuraciones iniciales eventualmente todos los registros  serán cero:

| $R_1$ | $R_2$ | $...$ | $R_n$ | $R_{n+1}$ | $R_{n+2}$ | $...$ |
| ----- | ----- | ----- | ----- | --------- | --------- | ----- |
| $r_1$ | $r_2$ | $...$ | $r_n$ | $r_{n+1}$ | $0$       | $...$ |
se define como $P(r_1, r_2, ..., r_n, r_{n+1})$.

**Obs**. Recordemos funciones: **Parciales y totales**
Las *URM* calculan **funciones parciales**
