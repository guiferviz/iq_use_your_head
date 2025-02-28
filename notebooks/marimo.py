import marimo

__generated_with = "0.11.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from widgets.matrix import Matrix
    from random import randint
    from use_your_head.iq_use_your_head import TABLERO_FILAS, TABLERO_COLUMNAS, puede_colocar, todas_piezas
    import marimo as mo
    return (
        Matrix,
        TABLERO_COLUMNAS,
        TABLERO_FILAS,
        mo,
        puede_colocar,
        randint,
        todas_piezas,
    )


@app.cell
def _(
    Matrix,
    TABLERO_COLUMNAS,
    TABLERO_FILAS,
    mo,
    puede_colocar,
    randint,
    todas_piezas,
):
    def get_candidates_matrix():
        tablero_vacio = [[0 for _ in range(TABLERO_COLUMNAS)] for _ in range(TABLERO_FILAS)]
        tablero = [[0 for _ in range(TABLERO_COLUMNAS)] for _ in range(TABLERO_FILAS)]
        for fila in range(TABLERO_FILAS):
            for columna in range(TABLERO_COLUMNAS):
                for nombre_pieza, variantes in todas_piezas.items():
                    for variante in variantes:
                        if puede_colocar(tablero_vacio, variante, fila, columna):
                            tablero[fila][columna] += 1
        return tablero

    def get_random_matrix():
        return [[randint(1, 100) for _ in range(11)] for _ in range(5)]

    mo.ui.anywidget(Matrix(matrix=get_candidates_matrix()))#, colors=["red", "green"], coordinate_system="row,column")
    return get_candidates_matrix, get_random_matrix


@app.cell
def _():
    from ipymario import Widget

    Widget(size=200)._repr_mimebundle_()
    return (Widget,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
