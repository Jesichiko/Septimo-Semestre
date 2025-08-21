En matemáticas un problema común es **DECIDIR** si un número tiene o no una propiedad dada. 

**Por ejemplo**:
1. Dado cualquier número entero $x>1| es \ primo?$$\{Si - 1|No- 0\}$
2. Dados dos enteros $x,y\in\mathbb{N} ¿$$x$ es multiplo de $y$? $\{Si - 1|No- 0\}$

Los algoritmos que resuelven estros problemas definen **FUNCIONES CARACTERÍSTICAS**:
Por ejemplo.
Para 1):$$C_p=\mathbb{N}\to \mathbb{N}$$
$$C_p(x) = \{ 1 \ si \ x \ es \ primo | 0 \ si \ no \ es \ primo\}$$
Para 2):$$C_m:\mathbb{N}^2\to\mathbb{N}$$
$$C_m(x,y)=\{1 \ si \ x\ es \ multiplo \ de \ y\ |\ 0 \ si \ x \ no \ es \ multiplo \ de \ y\}$$
Luego hay que mostrar que estas **funciones características** son computables. En tal caso, el predicado se llama **DECIDIBLE**

El punto 1) y 2) son **DECIDIBLES** *si solo si* existe un programa **computable** que resuelva su función característica