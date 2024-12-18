import time


TABLERO_FILAS = 5
TABLERO_COLUMNAS = 11

tablero = [[0 for _ in range(TABLERO_COLUMNAS)] for _ in range(TABLERO_FILAS)]

piezas = {
    "l": [(0, 0), (0, 1), (1, 0)],
    "z": [(1, 0), (1, 1), (0, 1), (0, 2)],
    "t": [(0, 0), (0, 1), (0, 2), (1, 1)],
    "ł": [(0, 0), (0, 1), (0, 2), (1, 0)],
    "P": [(0, 1), (1, 0), (1, 1), (0, 2), (1, 2)],
    "Z": [(1, 0), (1, 1), (1, 2), (0, 2), (0, 3)],
    "T": [(0, 0), (0, 1), (0, 2), (0, 3), (1, 1)],
    "M": [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
    "V": [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
    "U": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)],
    "L": [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0)],
    "Y": [(0, 0), (1, 0), (1, 1), (1, 2), (2, 1)],
}
huecos = [
    #  #
    # #.#
    #  #
    {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (-1, 0): 1,
        (0, -1): 1,
    },
    #  ##
    # #..#
    #  ##
    {
        (0, 0): 0,
        (0, 1): 0,
        (0, 2): 1,
        (1, 0): 1,
        (1, 1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
    },
    #  ###
    # #...#
    #  ###
    {
        (-1, 0): 1,
        (-1, 1): 1,
        (-1, 2): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (0, 2): 0,
        (0, 3): 1,
        (1, 0): 1,
        (1, 1): 1,
        (1, 2): 1,
    },
    #  #
    # #.#
    # #.#
    #  #
    {
        (-1, 0): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 1,
        (1, -1): 1,
        (1, 0): 0,
        (1, 1): 1,
        (2, 0): 1,
    },
    #  #
    # #.#
    # #.#
    # #.#
    #  #
    {
        (-1, 0): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 1,
        (1, -1): 1,
        (1, 0): 0,
        (1, 1): 1,
        (2, -1): 1,
        (2, 0): 0,
        (2, 1): 1,
        (3, 0): 1,
    },
]


def normalizar(pieza):
    """Normaliza las coordenadas de la pieza para que todas sean positivas."""
    min_row = min(r for r, _ in pieza)
    min_col = min(c for _, c in pieza)
    return [(r - min_row, c - min_col) for r, c in pieza]


def rotar_pieza(pieza):
    """Rota la pieza 90 grados en sentido horario y la normaliza."""
    return normalizar([(col, -row) for row, col in pieza])


def espejar_horizontal(pieza):
    """Genera el espejo horizontal de la pieza y la normaliza."""
    return normalizar([(row, -col) for row, col in pieza])


def espejar_vertical(pieza):
    """Genera el espejo vertical de la pieza y la normaliza."""
    return normalizar([(-row, col) for row, col in pieza])


def generar_variantes(pieza):
    """Genera todas las variantes de una pieza (rotaciones y espejos)."""
    variantes = set()
    actual = pieza
    for _ in range(4):
        actual = rotar_pieza(actual)
        variantes.add(tuple(sorted(actual)))
        variantes.add(tuple(sorted(espejar_horizontal(actual))))
        variantes.add(tuple(sorted(espejar_vertical(actual))))
    return [list(variante) for variante in variantes]


# Generar todas las variantes de las piezas
todas_piezas = {}
for nombre, pieza in piezas.items():
    todas_piezas[nombre] = generar_variantes(pieza)


def puede_colocar(tablero, pieza, fila, columna):
    for dr, dc in pieza:
        r, c = fila + dr, columna + dc
        if (
            r < 0
            or r >= TABLERO_FILAS
            or c < 0
            or c >= TABLERO_COLUMNAS
            or tablero[r][c] != 0
        ):
            return False
    return True


def hay_hueco(tablero, hueco, fila, columna):
    for (dr, dc), esperado in hueco.items():
        r, c = fila + dr, columna + dc
        if r < 0 or r >= TABLERO_FILAS or c < 0 or c >= TABLERO_COLUMNAS:
            valor = 1
        else:
            valor = 0 if tablero[r][c] == 0 else 1
        if valor != esperado:
            return False
    return True


def colocar_pieza(tablero, pieza, fila, columna, valor):
    for dr, dc in pieza:
        r, c = fila + dr, columna + dc
        tablero[r][c] = valor


def quitar_pieza(tablero, pieza, fila, columna):
    colocar_pieza(tablero, pieza, fila, columna, 0)


def resolver(tablero, todas_piezas):
    if not todas_piezas:
        yield tablero
    else:
        nombre_pieza, variantes = todas_piezas.popitem()
        for fila in range(TABLERO_FILAS):
            for columna in range(TABLERO_COLUMNAS):
                for variante in variantes:
                    if nombre_pieza == "Y":
                        print(f"probando una variante de Y en {fila} {columna}")
                    if puede_colocar(tablero, variante, fila, columna):
                        colocar_pieza(tablero, variante, fila, columna, nombre_pieza)
                        if not hay_huecos_imposibles(tablero):
                            yield from resolver(tablero, todas_piezas)
                        quitar_pieza(tablero, variante, fila, columna)
        todas_piezas[nombre_pieza] = variantes


def hay_huecos_imposibles(tablero):
    for f in range(TABLERO_FILAS):
        for c in range(TABLERO_COLUMNAS):
            if tablero[f][c] == 0:
                for hueco in huecos:
                    if hay_hueco(tablero, hueco, f, c):
                        return True
    return False


def imprimir_tablero(tablero):
    for fila in tablero:
        print(" ".join(str(c) for c in fila))
    print()


# Ejecutamos el algoritmo de resolución
start = time.time()
soluciones = set()
for solucion in resolver(tablero, todas_piezas):
    tablero_tuple = tuple(tuple(row) for row in tablero)
    assert tablero_tuple not in soluciones, tablero_tuple
    soluciones.add(tablero_tuple)
    if len(soluciones) % 1000 == 0:
        et = time.time() - start
        print(f"Elapsed time {et}")
        print(f"Solución {len(soluciones)}:")
        imprimir_tablero(tablero)
