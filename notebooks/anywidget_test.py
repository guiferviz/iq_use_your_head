import marimo

__generated_with = "0.11.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""# Classic""")
    return


@app.cell
def _():
    import anywidget
    import traitlets
    return anywidget, traitlets


@app.cell
def _(anywidget, traitlets):
    class MinimalWidget(anywidget.AnyWidget):
        _esm = """
            function render({ model, el }) {
                el.textContent = `Value: ${model.get('value')}`;
                model.on('change:value', () => {
                    el.textContent = `Value: ${model.get('value')}`;
                });
            }
            export default { render };
        """
        value = traitlets.Int(0).tag(sync=True)

    MinimalWidget(value=3)
    return (MinimalWidget,)


@app.cell
def _(mo):
    mo.md(r"""# Experimental""")
    return


@app.cell
def _():
    import pydantic
    import psygnal
    from anywidget.experimental import widget
    return psygnal, pydantic, widget


@app.cell
def _(psygnal, pydantic, widget):
    @widget(
        esm="""
            function render({ model, el }) {
                el.textContent = `Value: ${model.get('value')}`;
                model.on('change:value', () => {
                    el.textContent = `Value: ${model.get('value')}`;
                });
            }
            export default { render };
        """
    )
    @psygnal.evented
    class MinimalWidgetExperimental(pydantic.BaseModel):
        value: int = 0

    MinimalWidgetExperimental(value=3)
    return (MinimalWidgetExperimental,)


@app.cell
def _(mo):
    mo.md(r"""# My Experiments""")
    return


@app.cell
def _(anywidget, pydantic, traitlets):
    from functools import wraps

    def my_decorator(esm: str):
        def class_wrapper(cls):
            attrs = {"_esm": esm, "__module__": cls.__module__}
            
            for field_name, field in cls.__annotations__.items():
                default_value = getattr(cls, field_name, None)
                trait_type = None
                if field == 'int':
                    trait_type = traitlets.Int(default_value).tag(sync=True)
                elif field is float:
                    trait_type = traitlets.Float(default_value).tag(sync=True)
                elif field is str:
                    trait_type = traitlets.Unicode(default_value).tag(sync=True)
                elif field is bool:
                    trait_type = traitlets.Bool(default_value).tag(sync=True)
                
                if trait_type is not None:
                    attrs[field_name] = trait_type
                    
            new_class = type(cls.__name__, (anywidget.AnyWidget,), attrs)
            return new_class
        return class_wrapper

    # Example Usage:
    @my_decorator(
        esm="""
            function render({ model, el }) {
                el.textContent = `Value: ${model.get('value')}`;
                model.on('change:value', () => {
                    el.textContent = `Value: ${model.get('value')}`;
                });
            }
            export default { render };
        """
    )
    class MinimalWidgetMyExperimental(pydantic.BaseModel):
        value: int = 0

    MinimalWidgetMyExperimental(value=4)
    return MinimalWidgetMyExperimental, my_decorator, wraps


@app.cell
def _(traitlets):
    dir(traitlets)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
