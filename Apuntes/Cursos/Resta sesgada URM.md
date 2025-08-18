**Recordar _[[Instrucciones de URMs]]_**
Demostrar que la resta sesgada $g: \mathbb{N} \to \mathbb{N}$ es computable, $$g(x)=x \ \dot{-} \ 1$$
**Dem.** Se diseña un programa $K$ que calcule la resta sesgada:$$\forall x \in\mathbb{N}:K(x)\downarrow x-1$$
Tal $K$ es:
$K$: 
1) $J(1,2,6)$
2) $S(2)$
3) $J(1,2,6)$
4) $S(3)$
5) $J(1,1,2)$
6) $T(3,1)$

**Hagamos un par de corridas**

|           | $R_1$ | $R_2$ | $R_3$ | $R_4$ | $...$ | Next       |
| --------- | ----- | ----- | ----- | ----- | ----- | ---------- |
| **Start** | 0     | 0     | 0     | 0     | $...$ | $J(1,2,6)$ |
|           | 0     | 0     | 0     | 0     | $...$ | $T(3,1)$   |
|           | 0     | 0     | 0     | 0     | $...$ | **Stop**   |
$1 \dot{-} 1 = 0$ funcionó

|           | $R_1$ | $R_2$ | $R_3$ | $R_4$ | $...$ | Next       |
| --------- | ----- | ----- | ----- | ----- | ----- | ---------- |
| **Start** | 3     | 0     | 0     | 0     | $...$ | $J(1,2,6)$ |
|           | 3     | 0     | 0     | 0     | $...$ | $S(2)$     |
|           | 3     | 1     | 0     | 0     | $...$ | $J(1,2,6)$ |
|           | 3     | 1     | 0     | 0     | $...$ | $S(3)$     |
|           | 3     | 1     | 1     | 0     | $...$ | $J(1,1,2)$ |
|           | 3     | 1     | 1     | 0     | $...$ | $S(2)$     |
|           | 3     | 2     | 1     | 0     | $...$ | $J(1,2,6)$ |
|           | 3     | 2     | 1     | 0     | $...$ | $S(3)$     |
|           | 3     | 2     | 2     | 0     | $...$ | $J(1,1,2)$ |
|           | 3     | 2     | 2     | 0     | $...$ | $S(2)$     |
|           | 3     | 3     | 2     | 0     | $...$ | $J(1,2,6)$ |
|           | 3     | 3     | 2     | 0     | $...$ | $T(3,1)$   |
|           | 2     | 3     | 2     | 0     | $...$ | **Stop**   |
$3\dot{-}1=2$ funcióno 

**Obs** Hemos visto que para demostrar una función $$f: \mathbb{N}^{n}\to\mathbb{N}$$
sea computable hay que **diseñar** un programa $P$ que la calcule. 
Recíprocamente, también es interesante dado un programa $P$ ¿qué calcula P?

Sea $n\geq1$ entero, se cumple lo siguiente:$$(y \ a_1,...,a_n \in\mathbb{N}):P(a_1,...,a_n)\downarrow b \ \ \ o \ \ \ P(a_1,...,a_n)\uparrow b$$
Tal b define una función **PARCIAL** que se denota $f^{(n)}:\mathbb{N}^n \to\mathbb{N}$

