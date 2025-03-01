import marimo

__generated_with = "0.11.12"
app = marimo.App(width="medium")


@app.cell
def _():
    from ipymario import Widget

    Widget(size=200)
    return (Widget,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
