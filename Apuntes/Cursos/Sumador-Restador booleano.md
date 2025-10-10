Gracias a las [[Compuertas logicas]] podemos modelar un circuito que, dados dos números $n,k$ con 4 bits, **nos de su suma o su resta**. Para esto, el circuito tendrá como inputs/outputs:
- Entradas:
	- $n$ número con 4 bits
	- $k$ número con 4 bits
	- bit de operación para sumar o restar
- Salidas:
	- $f_{acarreo}$ si el resultado es mayor a 4 bits
	- $f_{salida}$ de 4 bits
	- $f_{signo} = \begin{cases} 0 \ si \ el \ resultado \ de \ la \ operacion \ es \ positivo \\ 1 \ si \ es \ negativo \end{cases}$	

Para poder hacer nuestro sumador-restador usaremos el enfoque de crearlo **por bloques**, ya que por tabla de combinaciones tendremos $2⁸ (256)$ combinaciones por lo cual no es efectivo.

