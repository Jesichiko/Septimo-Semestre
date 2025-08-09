**Obs.** Con la idea de estudiar los fundamentos de matemáticas, **Alan Turing** creó las máquinas de Turing (MT)
- Hardware
	- Cinta dividida en celdas **infinita**
	- Cabeza lectora que pone atención **a una sola celda**. Esta cabeza tiene un estado interno
- Software
	- Escribir un solo símbolo sobre la celda actual o borrar el símbolo sobre la celda actual.
	- Mover la cabeza a izquierda o derecha

En cualquier momento la _MT_ tiene algún estado interno $\{q_1, q_2, ..., q_m\}$. 
Estos estados pueden cambiar dependiendo de lo que se lee, de la siguiente forma:
1. $q_i \ S_j \ S_k \ q_e$ : Estado interno, $q_i$  cambia a estado  $q_e$  al leer  $S_j$  y el símbolo  $S_j$  se reemplaza por  $S_k$
2. $q_i \ S_j \ R \ q_e$ : Estado interno, $q_i$  cambiar  $q_e$  al leer  $S_j$  y avanza a la celda derecha
3. $q_i \ S_j \ L \ q_e$ : Estado interno, $q_i$  cambiar  $q_e$  al leer  $S_j$  y avanza a la celda izquierda

Estos estados se representan gramaticalmente de la siguiente forma:
$$1. \ q_i \ S_j/S_k, \ q_l$$
$$2. \ q_i \ S_j/\ ,R \ q_l$$
$$3. \ q_i \ S_j/\ ,L \ q_l$$
**Obs.** Para comenzar un cálculo se debe de proveer a la MT:
1. Cinta
2. Posición de la cabeza
3. Estado interno inicial
En estas máquinas, el cálculo para cuando **no** se encuentra una especificación $q_i \ S_j \ S_k \ q_e$ que aplica:

**Ejem** Sea **M** la siguiente MT:
- Alfabeto (símbolos): $\{ 0,1\}$
- Cinta inicial: Blanco ($B$) (no hay nada en celdas)
- Estados: $\{ q_i, q_l\}$
(Ejemplo ilustrado en libreta)
