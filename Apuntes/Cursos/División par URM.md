**Recordar _[[Resta sesgada URM]]_**.

**Ejemplo.** Sea $f:\mathbb{N}\to\mathbb{N}$ función tal que: $$f(x) = \{\frac{x}{2},x\ es \ par \ | indefinida, \ si \ x \ impar\}$$
**Demostrar que f es computable**.
Ejemplos de entradas:
- $f(2)=2$
- $f(6)=3$
- $f(5) \ indefinido$
## Demostración
Se diseñara un programa $D$  que $$\forall x\in\mathbb{N}, \ D(x)\downarrow\frac{x}{2} \ si \ x \ es \ par$$$$D(x)\uparrow \ si \ x \ no \ es \ par$$
*Hagamos unos experimentos*:

|       | $R_1$ | $R_2$ | $R_3$ | $...$ | next      |
| ----- | ----- | ----- | ----- | ----- | --------- |
| Start | 4     | 0     | 0     |       | J(1,2, 6) |
|       | 4     | 0     | 1     |       | S(3)      |
|       | 4     | 1     | 1     |       | S(2)      |
|       | 4     | 2     | 1     |       | S(2)      |
|       | 4     | 2     | 1     |       | J(1,2,6)  |
|       | 4     | 2     | 2     |       | S(3)      |
|       | 4     | 3     | 2     |       | S(2)      |
|       | 4     | 4     | 2     |       | J(1,2,6)  |
|       | 4     | 4     | 2     |       | T(3,1)    |
|       | 2     | 4     | 2     |       | Stop      |
Lo cual sugiere que el programa es:
$D$: 1) $J(1,2,6)$
2) $S(3)$
3) $S(2)$
4) $S(2)$
5) $J(1,1,1)$
6) $T(3,1)$