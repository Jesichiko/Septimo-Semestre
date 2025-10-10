A partir de los circuitos de [[Compuertas logicas]]

## Modulo AND
```verilog
module and_gate(
    input a,
    input b,
    output y
);
    assign y = a & b;
endmodule
```
## Modulo OR 
```verilog
module or_gate(
    input a,
    input b,
    output y
);
    assign y = a | b;
endmodule
```
## Modulo NOT
```verilog
module not_gate(
    input a,
    output y
);
    assign y = ~a;
endmodule

```
## Conjunto puertas
