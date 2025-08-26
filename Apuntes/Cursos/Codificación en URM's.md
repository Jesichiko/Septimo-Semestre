**Obs**. Por definición, las *URM* solo funcionan con números naturales. Sin embargo, se puede obligar a trabajar con otros números vía **CODIFICACIÓN**.

**Def**:
1) Una **CODIFICACIÓN** de un conjunto D es una función inyectiva (SI $d\neq d\in D\to \alpha (d) \neq \alpha(d)$) $$\alpha: D\to\mathbb{N}$$Si $d\in D$, se dice que $d$ **ESTÁ CODIFICADO**, se dice que $d$ **ESTÁ CODIFICADO** por $\alpha(d)$.

2) Si $f:D\to D$ función, entonces $f$ se dice que **ESTÁ CODIFICADA** por $f^*$:$$f^*=\alpha*f*\alpha^{-1}:$$
3) Se dice que $f:D\to D$ es computable si $f^* :\mathbb{N}\to\mathbb{N}$ lo es.

**Ejemplo**. Sea $f:\mathbb{Z}\to\mathbb{Z}:f(x) = x-1$.
Ejemplos son $f(8) =8-1=7$, $f(0)=-1$, $f(-2)=-3$

**Demostrar que $f$ es computable**.
**Dem** Se tiene que diseñar un programa $R$ que calcule la codificación de $\mathbb{Z}$ que corresponda a codificar entoneros no negativos con números pares y los negativos con impares:$$\alpha :\mathbb{Z}\to\mathbb{N}$$
Ejemplos:
$0 \to 0$
$1 \to 2$
$2\to4$
$-1\to1$
$-2\to3$
$-3\to 5$

entonces $\alpha$ es:
$$\alpha(x) = \{2x \ si \ x>0: -2x-1 \ si \ x<0\}$$
