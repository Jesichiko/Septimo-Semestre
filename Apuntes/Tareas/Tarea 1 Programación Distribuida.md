Tomando como referencia la [[Computación ubicua]]:
Pregunta: ¿Qué ventaja ofrece un **AM** frente a una app web en un hospital inteligente?
**Diseña un esquema básico de un AM para un sistema de domótica**

## Tarea 1
### Respuesta a la pregunta
Si tenemos un agente móvil que pueda hacer las mismas operaciones que una app web de un hospital inteligente (como hacer citas al doctor, revisar stock de medicamentos, ver recetas, etc) entonces este dispositivo tiene el beneficio de que ayuda a la gente **que no pueda acceder a una app web por cuestión de recursos o porque son muy complicadas de entender**. Con este enfoque tenemos dos grupos a los que se puede dirigir el AM:
2. Primer grupo: Gente con pocos recursos y marginada que no pueda acceder a internet o aparatos inteligentes
3. Segundo grupo: Personas mayores las cuales tenga una alta dificultad para poder acceder o entender una aplicación web, internet y dispositivos móviles en general.
Esto nos permite poder brindar ya sea un servicio gubernamental de manera efectiva y rápida para el primer grupo o bien crear un producto basado en una necesidad de salud para un grupo en especifico.
### Esquema de un AM
Nuestro AM propuesto será un _apagador de televisiones en una casa conectadas a través de internet_. Nuestro AM podrá navegar a través de la red y encontrará los dispositivos TV que están conectados a la red.

1. Publico meta: Familias de clase media alta que tengan más de 3 integrantes
2. Dominio de conocimiento: El AM solo tendrá el conocimiento de que TVs están conectadas a una red dada y como poder apagarlas a través de una request.
3. Arquitectura BDI: 
	1. Las _creencias_ que tenemos en nuestro AM es que sea usado por un publico familiar, donde las familias sean numerosas para así brindar muchísima más cobertura a más dispositivos TV. 
	2. Los _deseos_ de nuestro AM es que sea utilizado específicamente para niños y jóvenes que suelan dejar prendidos los televisores y se necesiten apagar desde un lugar remoto. 
	3. Las _intenciones_ es que sea util en la vida diaria de amas de casa o gente que cuide a una gran cantidad de personas que ven televisión simultáneamente y tiendan a dejarla prendida.