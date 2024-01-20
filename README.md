![plot](./original.svg)
# Fondo de pantalla actualizable

## Cómo funciona?

1. Se parte de una imagen SVG diseñada por mí en Inkscape con cada auto como un grupo. Además, no visibles pero debajo, hay una sombra para cada posición.
2. El programa en Python se configura para correr al inicio del sistema (usando systemd por ejemplo) o en su defecto de forma manual.
3. Cada vez que se ejecuta, se consulta una API que devuelve el resultado de la última carrera de F1. Con esta información se mueve cada auto tanto horizontalmente por su posición, como verticalmente para reflejar a qué distancia quedó del primero. En caso que el piloto haya tenido un DNF o similar, la sombra de su posición se mueve ahora sí para ser visible.
4. Se determina a *modificado.svg* como fondo de pantalla del sistema operativo.