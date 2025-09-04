Nuestro **sumador completo** es un circuito que suma dos números de tamaño **definido** y se tiene un **acarreo**

Tambien existen **1/2 sumador** como el siguiente:

| $z$  | $x$ |     | $f_c$ | $f_s$ |
| ---- | --- | --- | ----- | ----- |
|      |     |     |       |       |
| <br> |     |     |       |       |
Un **sumador completo** es de la forma:

| $x$ | $y$ | $z$ | $\|$ | $f_c$ | $f_s$ |
| --- | --- | --- | ---- | ----- | ----- |
| 0   | 0   | 0   |      | 0     | 0     |
| 0   | 0   | 1   |      | 0     | 1     |
| 0   | 1   | 0   |      | 0     | 1     |
| 0   | 1   | 1   |      | 1     | 0     |
| 1   | 0   | 0   |      | 0     | 1     |
| 1   | 0   | 1   |      | 1     | 0     |
| 1   | 1   | 0   |      | 1     | 0     |
| 1   | 1   | 1   |      | 1     | 1     |
$$f_c=\sum(m_3+m_5+m_6+m_7)$$
$$f_s=\sum(m_1+m_2+m_4+m_7)$$

Esto es:
$$f_c=\bar{x}yz+x\bar{y}z+xy\bar{z}+xyz = z(\bar{x}y+x\bar{y})+xy(\bar{z}+z)=z+xy$$

$$f_s=\bar{y}z+y\bar{z}+\bar{y}\bar{z}+yz=$$