Nuestro **sumador completo** es un circuito que suma dos números de tamaño **definido** y se tiene un **acarreo**

Tambien existen **1/2 sumador** como el siguiente:

| $z$ | $x$ | $\|$ | $f_c$ | $f_s$ |
| --- | --- | ---- | ----- | ----- |
| 0   | 0   |      | 0     | 0     |
| 0   | 1   |      | 0     | 1     |
| 1   | 0   |      | 1     | 0     |
| 1   | 1   |      | 1     | 1     |
este sumador tiene funciones tales que:
$$f_c(x,y)=\sum(m_2+m_3)$$
$$f_s(x,y)=\sum(m_1+m_3)$$
Esto es:
$$f_c=z\bar{x}+zx$$
$$f_s=\bar{z}x+zx$$
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

$$f_s=\bar{x}\bar{y}z+\bar{x}y\bar{z}+x\bar{y}\bar{z}+xyz=\bar{x}(\bar{y}z+y\bar{z})+x(\bar{yz}+yz)$$
