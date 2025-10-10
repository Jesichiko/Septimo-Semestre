Podemos modelar las *puertas de un vocho* como dos **funciones booleanas** con los siguientes valores booleanos dadas las **4 puertas**:

| $x$ | $y$ | $z$ | $w$ | $\|$ | $f_1$ | $f_2$ |
| --- | --- | --- | --- | ---- | ----- | ----- |
| 0   | 0   | 0   | 0   |      | 0     | 0     |
| 0   | 0   | 0   | 1   |      | 1     | 1     |
| 0   | 0   | 1   | 0   |      | 1     | 1     |
| 0   | 0   | 1   | 1   |      | 1     | 1     |
| 0   | 1   | 0   | 0   |      | 1     | 1     |
| 0   | 1   | 0   | 1   |      | 1     | 1     |
| 0   | 1   | 1   | 0   |      | 1     | 1     |
| 0   | 1   | 1   | 1   |      | 1     | 1     |
| 1   | 0   | 0   | 0   |      | 1     | 1     |
| 1   | 0   | 0   | 1   |      | 1     | 1     |
| 1   | 0   | 1   | 0   |      | 1     | 1     |
| 1   | 0   | 1   | 1   |      | 1     | 1     |
| 1   | 1   | 0   | 0   |      | 1     | 1     |
| 1   | 1   | 0   | 1   |      | 1     | 1     |
| 1   | 1   | 1   | 0   |      | 1     | 1     |
| 1   | 1   | 1   | 1   |      | 1     | 1     |
Usando la **logica negativa** podemos ver $f_1$, $f_2$ como funciones de **un solo maxitermino**. Estas son:
					$f_1=x+y+z+w$
					$f_2=x+y+z+w$

## Implementación en Verilog
Modulo de las funciones:
```verilog
module funciones(
    input x,
    input y,
    input z,
    input w,
    output f1,
    output f2
);
    assign f1 = x | y | z | w;  // f1 = x + y + z + w
    assign f2 = x | y | z | w;  // f2 = x + y + z + w

endmodule
```

Testbench:
```verilog
`timescale 1ns/1ps

module tb_funciones;

    // Entradas como reg
    reg x, y, z, w;

    // Salidas como wire
    wire f1, f2;

    funciones uut (
        .x(x),
        .y(y),
        .z(z),
        .w(w),
        .f1(f1),
        .f2(f2)
    );

    integer i; // contador

    initial begin
        $display("x y z w | f1 f2");
        $display("----------------");

        // Recorre todas las combinaciones de 4 bits (0 a 15)
        for (i = 0; i < 16; i = i + 1) begin
            {x, y, z, w} = i;
            #1;
            $display("%b %b %b %b |  %b  %b", x, y, z, w, f1, f2);
        end
        $finish;
    end

endmodule

```