import marimo

__generated_with = "0.11.12"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    calc = mo.ui.text("3+4").form()
    calc
    return calc, mo


@app.cell
def _(calc, mo):
    mo.stop(calc.value is None)
    res = eval(calc.value)
    mo.md(f"Result: {calc.value} = {res}!")
    return (res,)


if __name__ == "__main__":
    app.run()
