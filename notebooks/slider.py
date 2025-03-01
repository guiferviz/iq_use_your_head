import marimo

__generated_with = "0.11.12"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    x = mo.ui.slider(1, 100, label="super value")
    x
    return mo, x


@app.cell
def _(mo, x):
    mo.md(f"The value is {x.value}")
    return


if __name__ == "__main__":
    app.run()
