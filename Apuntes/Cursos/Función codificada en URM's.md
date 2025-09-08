**Recordar _[[Codificación en URM's]]_**.
**Ejemplo.** Demostrar que la función:$$f:\mathbb{Z}\to\mathbb{Z}, \ f(x)=x-1$$
es computable.

**Dem**. Se tiene que diseñar un programa **R** que calcule la codificación:$$f^\alpha=\mathbb{N}\to\mathbb{N}$$
dado $f^* =\alpha*f*\alpha^{-1}$ y $\alpha$ función $$\alpha: \mathbb{Z}\to\mathbb{N}$$$$\alpha(x) = \{2x \ si \ x>0: -2x-1 \ si \ x<0\}$$
y la decodificación: $$\alpha^{-1}(y)=\{\frac{y}{2} \ si \ x \ es \ par: \frac{y+1}{2} \ si \ y \ es \ impar\}$$
Calculamos $f^*:\alpha*f*\alpha^{-1}$ que por definición de composicion es:
$$f^*(x)=\alpha(f(\alpha^{-1}(x)))$$
debido a que **x puede ser par o impar se tienen dos casos**:
$$x\in\mathbb{N},f^*(x)=\alpha(f(\alpha^-1(x)))=$$
$$\{$$
