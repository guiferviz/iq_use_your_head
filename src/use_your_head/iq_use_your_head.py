import yaml

import time


TABLERO_FILAS = 5
TABLERO_COLUMNAS = 11

tablero = [[0 for _ in range(TABLERO_COLUMNAS)] for _ in range(TABLERO_FILAS)]

piezas = {
    # "#": [
    #    (0, 0), (0, 1), (0, 2), (0, 3), (0, 8), (1, 0), (1, 1), (1, 2), (1, 3),
    #    (2, 0), (2, 1), (3, 0), (3, 1), (5, 7), (5, 8), (6, 7), (6, 8), (7, 5),
    #    (7, 6), (7, 7), (7, 8), (8, 0), (8, 5), (8, 6), (8, 7), (8, 8),
    #    # letras
    #    # (0, 6), (0, 7),
    #    # (1, 7), (1, 8),
    #    (2, 8), (3, 8), (4, 3), (4, 6), (4, 7), (4, 8), (5, 3), (5, 4), (5, 5),
    #    (5, 6), (6, 4), (6, 5), (6, 6),
    # ],
    "Y": [(0, 0), (1, 0), (1, 1), (1, 2), (2, 1)],
    "M": [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
    "L": [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0)],
    "Z": [(0, 0), (0, 1), (1, 1), (1, 2), (1, 3)],
    "T": [(0, 0), (0, 1), (0, 2), (0, 3), (1, 1)],
    "V": [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
    "U": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)],
    "P": [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
    "z": [(0, 0), (0, 1), (1, 1), (1, 2)],
    "t": [(0, 0), (0, 1), (0, 2), (1, 1)],
    "ł": [(0, 0), (0, 1), (0, 2), (1, 0)],
    "l": [(0, 0), (0, 1), (1, 0)],
}


def print_pieza(pieza):
    min_row = min(r for r, _ in pieza)
    min_col = min(c for _, c in pieza)
    max_row = max(r for r, _ in pieza)
    max_col = max(c for _, c in pieza)
    pieza_set = set(pieza)
    for r in range(min_row, max_row + 1):
        for c in range(min_col, max_col + 1):
            value = " "
            if (r, c) in pieza_set:
                value = "#"
            if r == 0 and c == 0:
                if (r, c) in pieza_set:
                    value = "O"
                else:
                    value = "."
            print(value, end="")
        print()


def normalizar(pieza):
    """Normaliza las coordenadas de la pieza para que la 0,0 sea la primera celda que se encuentre iterando filas y columnas por ese orden."""
    min_row, min_col = sorted(pieza)[0]
    # min_row = min(r for r, _ in pieza)
    # min_col = min(c for _, c in pieza)
    return normalizar_respecto_a(pieza, min_row, min_col)


def normalizar_respecto_a(pieza, row, col):
    return [(r - row, c - col) for r, c in pieza]


def rotar_pieza(pieza):
    """Rota la pieza 90 grados en sentido horario y la normaliza."""
    return normalizar([(col, -row) for row, col in pieza])


def espejar_horizontal(pieza):
    """Genera el espejo horizontal de la pieza y la normaliza."""
    return normalizar([(row, -col) for row, col in pieza])


def generar_variantes(pieza):
    """Genera todas las variantes de una pieza (rotaciones y espejos)."""
    variantes = set()
    actual = pieza
    for _ in range(4):
        variantes.add(tuple(sorted(actual)))
        variantes.add(tuple(sorted(espejar_horizontal(actual))))
        actual = rotar_pieza(actual)
    return list(variantes)


# Generar todas las variantes de las piezas
todas_piezas = {}
for nombre, pieza in piezas.items():
    todas_piezas[nombre] = generar_variantes(pieza) if nombre != "#" else [pieza]


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


def colocar_pieza(tablero, pieza, fila, columna, valor):
    for dr, dc in pieza:
        r, c = fila + dr, columna + dc
        tablero[r][c] = valor


def quitar_pieza(tablero, pieza, fila, columna):
    colocar_pieza(tablero, pieza, fila, columna, 0)


def encontrar_primera(pieza):
    return pieza[0]


def resolver(tablero, todas_piezas, fila, columna):
    if columna == TABLERO_COLUMNAS:
        fila += 1
        columna = 0

    if fila == TABLERO_FILAS:
        # solucion encontrada, asumimos que las piezas proporcionadas pueden
        # cubrir el tablero
        yield tablero
        return

    if tablero[fila][columna] == 0:
        for nombre_pieza in list(todas_piezas.keys()):
            variantes = todas_piezas[nombre_pieza]
            for variante in variantes:
                if puede_colocar(tablero, variante, fila, columna):
                    colocar_pieza(
                        tablero,
                        variante,
                        fila,
                        columna,
                        nombre_pieza,
                    )
                    del todas_piezas[nombre_pieza]
                    yield from resolver(tablero, todas_piezas, fila, columna + 1)
                    todas_piezas[nombre_pieza] = variantes
                    quitar_pieza(tablero, variante, fila, columna)
        if tablero[fila][columna] == 0:
            # no ha sido posible poner ninguna pieza
            return
    yield from resolver(tablero, todas_piezas, fila, columna + 1)


def imprimir_tablero(tablero):
    for fila in tablero:
        print(" ".join(str(c) for c in fila))
    print()


# for name, shapes in todas_piezas.items():
#    print(name, len(shapes))
# l 4
# z 4
# t 4
# ł 8
# P 8
# Z 8
# T 8
# M 4
# V 4
# U 4
# L 8
# Y 8

# for i, pieza in enumerate(todas_piezas["z"]):
#    print("Pieza", i)
#    print_pieza(pieza)


# Ejecutamos el algoritmo de resolución
def main_solve():
    start = time.time()
    soluciones = set()
    for solucion in resolver(tablero, todas_piezas, 0, 0):
        tablero_tuple = tuple(tuple(row) for row in tablero)
        assert tablero_tuple not in soluciones, tablero_tuple
        soluciones.add(tablero_tuple)
        if len(soluciones) % 1000 == 0:
            et = time.time() - start
            print(f"Elapsed time {et}")
            print(f"Solución {len(soluciones)}:")
            imprimir_tablero(tablero)
    if not soluciones:
        print("Sin soluciones :(")


def obtener_celdas_con_uno(matriz):
    celdas_con_uno = []
    for i in range(TABLERO_FILAS):
        for j in range(TABLERO_COLUMNAS):
            if matriz[i][j] == 1:
                indice_celda = i * TABLERO_COLUMNAS + j
                celdas_con_uno.append(f"C{indice_celda}")

    return celdas_con_uno


"""
main_solve()
# Cuenta posibles celdas para poner piezas.
candidates = {}
for fila in range(TABLERO_FILAS):
    for columna in range(TABLERO_COLUMNAS):
        for nombre_pieza in list(todas_piezas.keys()):
            variantes = todas_piezas[nombre_pieza]
            for variante in variantes:
                if puede_colocar(tablero, variante, fila, columna):
                    colocar_pieza(
                        tablero,
                        variante,
                        fila,
                        columna,
                        1,
                    )
                    candidates[
                        " ".join(obtener_celdas_con_uno(tablero) + [nombre_pieza])
                    ] = f"Piece {nombre_pieza} in {fila},{columna}"
                    quitar_pieza(tablero, variante, fila, columna)
constraints = {
    element: "Cell" for sublist in candidates.keys() for element in sublist.split()
}
for nombre_pieza in list(todas_piezas.keys()):
    constraints[nombre_pieza] = "Piece"
# Create dictionary for YAML
data = {"constraints": constraints, "candidates": candidates}

# Convert to YAML
yaml_data = yaml.dump(data, sort_keys=False, allow_unicode=True)
print(yaml_data)
"""
"""
La solución número 1000 debe ser:
Y Y M M T T T T t t t
L Y Y M M T z z U t U
L Y P P M z z V U U U
L P P P Z Z l V ł ł ł
L L Z Z Z l l V V V ł
"""
