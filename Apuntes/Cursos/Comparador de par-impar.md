Para construir un comparador que identifique si un numero es par, impar o primo debemos identificar las **posibles combinaciones**:

| $x$ | $y$ | $z$ | $w$ | $\|$ | $p_{par}$ | $p_{impar}$ | $p_{prime}$ |
| --- | --- | --- | --- | ---- | --------- | ----------- | ----------- |
| 0   | 0   | 0   | 0   |      | 1         | 0           | 0           |
| 0   | 0   | 0   | 1   |      | 0         | 1           | 0           |
| 0   | 0   | 1   | 0   |      | 1         | 0           | 1           |
| 0   | 0   | 1   | 1   |      | 0         | 1           | 1           |
| 0   | 1   | 0   | 0   |      | 1         | 0           | 0           |
| 0   | 1   | 0   | 1   |      | 0         | 1           | 1           |
| 0   | 1   | 1   | 0   |      | 1         | 0           | 0           |
| 0   | 1   | 1   | 1   |      | 0         | 1           | 1           |
| 1   | 0   | 0   | 0   |      | 1         | 0           | 0           |
| 1   | 0   | 0   | 1   |      | 0         | 1           | 0           |
| 1   | 0   | 1   | 0   |      | 1         | 0           | 0           |
| 1   | 0   | 1   | 1   |      | 0         | 1           | 1           |
| 1   | 1   | 0   | 0   |      | 1         | 0           | 0           |
| 1   | 1   | 0   | 1   |      | 0         | 1           | 1           |
| 1   | 1   | 1   | 0   |      | 1         | 0           | 0           |
| 1   | 1   | 1   | 1   |      | 0         | 1           | 0           |
las funciones resultan son:
$$f_{par}=\bar{x}\bar{y}\bar{z}\bar{w}+\bar{x}\bar{y}z\bar{w}+\bar{x}y\bar{z}\bar{w}+\bar{x}yz\bar{w}+x\bar{y}\bar{z}\bar{w}+x\bar{y}z\bar{w}+xy\bar{z}\bar{w}+xyz\bar{w}$$
$$=\bar{x}\bar{y}(\bar{z}\bar{w}+z\bar{w})+\bar{x}y(\bar{z}\bar{w}+z\bar{w})+x\bar{y}(\bar{z}\bar{w}+z\bar{w})+xy(\bar{z}\bar{w}+z\bar{w})$$
$$=(\bar{z}\bar{w}+z\bar{w})(\bar{x}\bar{y}+\bar{x}y+x\bar{y}+xy)$$
$$=(\bar{z}\bar{w}+z\bar{w})(\bar{x}+x)$$
$$=\bar{z}\bar{w}+z\bar{w}$$
$$=\bar{w}$$
$$f_{impar}=\bar{f_{par}}=\bar{w}$$
$$=w$$
$$f_{prime}=\bar{x}\bar{y}z\bar{w}+\bar{x}\bar{y}zw+\bar{x}y\bar{z}w+\bar{x}yzw+x\bar{y}zw+xy\bar{z}w$$
$$=\bar{x}\bar{y}z+\bar{x}yw+x\bar{y}zw+xy\bar{z}w$$
