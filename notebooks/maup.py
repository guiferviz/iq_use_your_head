import marimo

__generated_with = "0.11.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import anywidget
    import traitlets

    class MAUPWidget(anywidget.AnyWidget):
        _esm = r"""
        function render({ model, el }) {
          let canvasSize = model.get("canvas_size") || 500;
          let gridType = model.get("grid_type") || "square";
          let cellSize = parseFloat(model.get("cell_size") || "50");
          let orientation = parseFloat(model.get("orientation") || "0");
          let points = model.get("points") || [];
          let heatmapColors = model.get("heatmap_colors");
          let offsetX = parseFloat(model.get("grid_origin_x") || "0");
          let offsetY = parseFloat(model.get("grid_origin_y") || "0");

          const canvas = document.createElement("canvas");
          canvas.width = canvasSize;
          canvas.height = canvasSize;
          canvas.style.border = "1px solid #ccc";
          el.innerHTML = "";
          el.appendChild(canvas);
          const ctx = canvas.getContext("2d");

          let dragging = false;
          let dragStartX = 0, dragStartY = 0;
          let startOffsetX = offsetX, startOffsetY = offsetY;

          const sqrt3 = Math.sqrt(3);

          function parseHexColor(hex) {
            let r = parseInt(hex.slice(1,3), 16);
            let g = parseInt(hex.slice(3,5), 16);
            let b = parseInt(hex.slice(5,7), 16);
            let a = 1.0;
            if(hex.length === 9) {
              a = parseInt(hex.slice(7,9), 16) / 255;
            }
            return {r, g, b, a};
          }

          function interpolateBetween(color1, color2, factor) {
            factor = Math.min(Math.max(factor, 0), 1);
            const c1 = parseHexColor(color1);
            const c2 = parseHexColor(color2);
            const r = Math.round(c1.r + factor * (c2.r - c1.r));
            const g = Math.round(c1.g + factor * (c2.g - c1.g));
            const b = Math.round(c1.b + factor * (c2.b - c1.b));
            const a = c1.a + factor * (c2.a - c1.a);
            return `rgba(${r}, ${g}, ${b}, ${a})`;
          }

          function getHeatmapColor(intensity) {
            let n = heatmapColors.length;
            if (n === 0) return "rgba(0,0,0,1)";
            if (n === 1) return heatmapColors[0];
            let segment = intensity * (n - 1);
            let index = Math.floor(segment);
            let factor = segment - index;
            if (index >= n - 1) return heatmapColors[n - 1];
            return interpolateBetween(heatmapColors[index], heatmapColors[index + 1], factor);
          }

          function toGridCoords(x, y) {
            const rx = x - offsetX;
            const ry = y - offsetY;
            const theta = orientation * Math.PI / 180;
            const cosT = Math.cos(theta);
            const sinT = Math.sin(theta);
            return {
              x: rx * cosT + ry * sinT,
              y: -rx * sinT + ry * cosT
            };
          }

          function getSquareGridBounds() {
            const corners = [
              { x: 0, y: 0 },
              { x: canvas.width, y: 0 },
              { x: canvas.width, y: canvas.height },
              { x: 0, y: canvas.height }
            ];
            let xs = [], ys = [];
            for (const pt of corners) {
              const gridPt = toGridCoords(pt.x, pt.y);
              xs.push(gridPt.x);
              ys.push(gridPt.y);
            }
            const minX = Math.min(...xs);
            const maxX = Math.max(...xs);
            const minY = Math.min(...ys);
            const maxY = Math.max(...ys);
            const iMin = Math.floor(minX / cellSize);
            const iMax = Math.ceil(maxX / cellSize) - 1;
            const jMin = Math.floor(minY / cellSize);
            const jMax = Math.ceil(maxY / cellSize) - 1;
            return { iMin, iMax, jMin, jMax };
          }

          function getHexGridBounds() {
            const corners = [
              { x: 0, y: 0 },
              { x: canvas.width, y: 0 },
              { x: canvas.width, y: canvas.height },
              { x: 0, y: canvas.height }
            ];
            let qs = [], rs = [];
            const theta = orientation * Math.PI / 180;
            const cosT = Math.cos(theta);
            const sinT = Math.sin(theta);
            for (const pt of corners) {
              const rx = pt.x - offsetX;
              const ry = pt.y - offsetY;
              const gridX = rx * cosT + ry * sinT;
              const gridY = -rx * sinT + ry * cosT;
              const q = (gridX * (sqrt3/3) - gridY/3) / cellSize;
              const r = (gridY * (2/3)) / cellSize;
              qs.push(q);
              rs.push(r);
            }
            const minQ = Math.floor(Math.min(...qs));
            const maxQ = Math.ceil(Math.max(...qs));
            const minR = Math.floor(Math.min(...rs));
            const maxR = Math.ceil(Math.max(...rs));
            return { minQ, maxQ, minR, maxR };
          }

          // Cálculo de recuento de puntos para cuadrícula cuadrada
          function computeSquareCounts() {
            const counts = new Map();
            const theta = orientation * Math.PI / 180;
            const cosT = Math.cos(theta);
            const sinT = Math.sin(theta);
            for (const p of points) {
              const rx = p.x - offsetX;
              const ry = p.y - offsetY;
              const gridX = rx * cosT + ry * sinT;
              const gridY = -rx * sinT + ry * cosT;
              const i = Math.floor(gridX / cellSize);
              const j = Math.floor(gridY / cellSize);
              const key = `${i},${j}`;
              counts.set(key, (counts.get(key) || 0) + 1);
            }
            return counts;
          }

          function computeHexCounts() {
            const counts = new Map();
            const theta = orientation * Math.PI / 180;
            const cosT = Math.cos(theta);
            const sinT = Math.sin(theta);
            for (const p of points) {
              const rx = p.x - offsetX;
              const ry = p.y - offsetY;
              const gridX = rx * cosT + ry * sinT;
              const gridY = -rx * sinT + ry * cosT;
              const q_frac = (gridX * (sqrt3/3) - gridY/3) / cellSize;
              const r_frac = (gridY * (2/3)) / cellSize;
              let q = q_frac, r = r_frac, s = -q - r;
              let rq = Math.round(q);
              let rr = Math.round(r);
              let rs = Math.round(s);
              const q_diff = Math.abs(rq - q);
              const r_diff = Math.abs(rr - r);
              const s_diff = Math.abs(rs - s);
              if (q_diff > r_diff && q_diff > s_diff) {
                rq = -rr - rs;
              } else if (r_diff > s_diff) {
                rr = -rq - rs;
              } else {
                rs = -rq - rr;
              }
              const key = `${rq},${rr}`;
              counts.set(key, (counts.get(key) || 0) + 1);
            }
            return counts;
          }

          function drawSquareGrid() {
            const bounds = getSquareGridBounds();
            const counts = computeSquareCounts();
            let maxCount = 0;
            for (let i = bounds.iMin; i <= bounds.iMax; i++) {
              for (let j = bounds.jMin; j <= bounds.jMax; j++) {
                const key = `${i},${j}`;
                const count = counts.get(key) || 0;
                if (count > maxCount) maxCount = count;
              }
            }
            const theta = orientation * Math.PI / 180;
            const cosT = Math.cos(theta);
            const sinT = Math.sin(theta);

            for (let i = bounds.iMin; i <= bounds.iMax; i++) {
              for (let j = bounds.jMin; j <= bounds.jMax; j++) {
                const key = `${i},${j}`;
                const count = counts.get(key) || 0;
                const intensity = maxCount ? (count / maxCount) : 0;
                const color = getHeatmapColor(intensity);
                ctx.fillStyle = color;
                const corners = [
                  { x: i * cellSize,         y: j * cellSize },
                  { x: (i+1) * cellSize,       y: j * cellSize },
                  { x: (i+1) * cellSize,       y: (j+1) * cellSize },
                  { x: i * cellSize,         y: (j+1) * cellSize }
                ];
                ctx.beginPath();
                for (let k = 0; k < corners.length; k++) {
                  const gx = corners[k].x;
                  const gy = corners[k].y;
                  const globalX = offsetX + gx * cosT - gy * sinT;
                  const globalY = offsetY + gx * sinT + gy * cosT;
                  if (k === 0) ctx.moveTo(globalX, globalY);
                  else ctx.lineTo(globalX, globalY);
                }
                ctx.closePath();
                ctx.fill();
              }
            }
          }

          function drawHexGrid() {
            const bounds = getHexGridBounds();
            const counts = computeHexCounts();
            let maxCount = 0;
            for (let q = bounds.minQ - 1; q <= bounds.maxQ + 1; q++) {
              for (let r = bounds.minR - 1; r <= bounds.maxR + 1; r++) {
                const key = `${q},${r}`;
                const count = counts.get(key) || 0;
                if (count > maxCount) maxCount = count;
              }
            }
            const theta = orientation * Math.PI / 180;
            const cosT = Math.cos(theta);
            const sinT = Math.sin(theta);
            const R = cellSize;  // Usamos cellSize como radio
            const hexCorners = [
              { x: 0, y: -R },
              { x: (sqrt3/2) * R, y: -0.5 * R },
              { x: (sqrt3/2) * R, y: 0.5 * R },
              { x: 0, y: R },
              { x: - (sqrt3/2) * R, y: 0.5 * R },
              { x: - (sqrt3/2) * R, y: -0.5 * R }
            ];

            for (let q = bounds.minQ - 1; q <= bounds.maxQ + 1; q++) {
              for (let r = bounds.minR - 1; r <= bounds.maxR + 1; r++) {
                const key = `${q},${r}`;
                const count = counts.get(key) || 0;
                const intensity = maxCount ? (count / maxCount) : 0;
                const color = getHeatmapColor(intensity);
                ctx.fillStyle = color;
                const centerX = R * sqrt3 * (q + 0.5 * r);
                const centerY = R * 1.5 * r;
                ctx.beginPath();
                for (let i = 0; i < hexCorners.length; i++) {
                  const corner = hexCorners[i];
                  const gx = centerX + corner.x;
                  const gy = centerY + corner.y;
                  const globalX = offsetX + gx * cosT - gy * sinT;
                  const globalY = offsetY + gx * sinT + gy * cosT;
                  if (i === 0) ctx.moveTo(globalX, globalY);
                  else ctx.lineTo(globalX, globalY);
                }
                ctx.closePath();
                ctx.fill();
              }
            }
          }

          function drawPoints() {
            ctx.fillStyle = "black";
            for (const p of points) {
              ctx.fillRect(p.x - 1, p.y - 1, 3, 3);
            }
          }

          function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (gridType === "square") {
              drawSquareGrid();
            } else if (gridType === "hex") {
              drawHexGrid();
            }
            drawPoints();
          }

          // Eventos para arrastrar la cuadrícula
          console.log(model.get("interactive"));
          if (model.get("interactive")) {
              canvas.addEventListener("pointerdown", (e) => {
                dragging = true;
                dragStartX = e.clientX;
                dragStartY = e.clientY;
                startOffsetX = offsetX;
                startOffsetY = offsetY;
                canvas.setPointerCapture(e.pointerId);
              });
              canvas.addEventListener("pointermove", (e) => {
                if (!dragging) return;
                const dx = e.clientX - dragStartX;
                const dy = e.clientY - dragStartY;
                offsetX = startOffsetX + dx;
                offsetY = startOffsetY + dy;
                draw();
              });
              canvas.addEventListener("pointerup", () => {
                dragging = false;
                model.set("grid_origin_x", offsetX);
                model.set("grid_origin_y", offsetY);
                model.save_changes();
              });
          }

          // Listen for param changes from Python.
          model.on("change:canvas_size", () => {
            canvas.width = model.get("canvas_size");
            canvas.height = model.get("canvas_size");
            draw();
          });
          model.on("change:grid_type", () => {
            gridType = model.get("grid_type");
            draw();
          });
          model.on("change:cell_size", () => {
            cellSize = parseFloat(model.get("cell_size"));
            draw();
          });
          model.on("change:orientation", () => {
            orientation = parseFloat(model.get("orientation"));
            draw();
          });
          model.on("change:points", () => {
            points = model.get("points") || [];
            draw();
          });
          model.on("change:heatmap_colors", () => {
            heatmapColors = model.get("heatmap_colors");
            draw();
          });
          model.on("change:grid_origin_x", () => {
            offsetX = parseFloat(model.get("grid_origin_x")) || 0;
            draw();
          });
          model.on("change:grid_origin_y", () => {
            offsetY = parseFloat(model.get("grid_origin_y")) || 0;
            draw();
          });

          // Initial draw.
          draw();
        }
        export default { render };
        """

        canvas_size = traitlets.Int(500).tag(sync=True)
        grid_type = traitlets.Unicode("square").tag(sync=True)   # "square" or "hex"
        cell_size = traitlets.Float(50.0).tag(sync=True)
        orientation = traitlets.Float(0.0).tag(sync=True)          # degrees
        points = traitlets.List(trait=traitlets.Dict(), default_value=[]).tag(sync=True)
        heatmap_colors = traitlets.List(trait=traitlets.Unicode(), default_value=["#00990066", "#FFFF0066", "#ff000066"]).tag(sync=True)
        grid_origin_x = traitlets.Float(0.0).tag(sync=True)
        grid_origin_y = traitlets.Float(0.0).tag(sync=True)
        interactive = traitlets.Bool(True).tag(sync=True) # Cannot be changed later.
    return MAUPWidget, anywidget, traitlets


@app.cell
def _():
    import random


    def generate_points(n, canvas_size, seed=None):
        if seed:
            random.seed(seed)
        return [{"x": random.uniform(0, canvas_size), "y": random.uniform(0, canvas_size)} for _ in range(n)]
    return generate_points, random


@app.cell
def _(mo):
    mo.md(
        r"""
        Imagine this: you're planning your next getaway, and the last thing you want is to vacation in an area teeming with COVID infections. Being the data-driven person you are, you decide to download an open dataset of COVID infections across your country—each infected person marked as a latitude-longitude point (yeah, I know this dataset wouldn’t be GDPR compliant, but let’s roll with it for this example).

        When you plot all these points on a map, you end up with a chaotic scatter of dots:
        """
    )
    return


@app.cell
def _(MAUPWidget, generate_points, mo):
    mo.center(
        MAUPWidget(
            canvas_size = 300,
            grid_type = "square",
            cell_size = 300,
            points = generate_points(100, 300, seed=1),
            heatmap_colors=["#FFFFFF"],
            interactive=False,
        )
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        At first glance, it’s nearly impossible to spot any clusters or patterns among the noise. So, you think, “How can I make sense of this mess?” The smart move is to aggregate the data. You overlay a grid onto the map and break the country into larger zones. Then, using a choropleth with a well-chosen color scale, you paint areas with fewer infections in calming green and those with more infections in alarming red.

        Now, the heatmap below might simply be yelling, “Avoid the east-central region—COVID is going wild there!” With just one quick glance, you can easily pinpoint the spots with the lowest infection rates, making it look like the perfect place for a safe, relaxing holiday.
        """
    )
    return


@app.cell
def _(MAUPWidget, generate_points, mo):
    mo.center(
        MAUPWidget(
            canvas_size=300,
            grid_type="square",
            cell_size=50,
            points=generate_points(100, 300, seed=1),
            grid_origin_x=-127.9337158203125,
            grid_origin_y=-2.0025634765625,
            interactive=False,
        )
    )
    return


@app.cell
def _(mo):
    mo.md(r"""Well, here’s where things get tricky. Look at the grid, where a square starts where it starts and not a bit to the right? A selection was must be done and it was taking without any other consideration. Imagine we decided to draw the grid a bit more to the right:""")
    return


@app.cell
def _(MAUPWidget, generate_points, mo):
    view1 = MAUPWidget(
        canvas_size=300,
        grid_type="square",
        cell_size=50,
        points=generate_points(100, 300, seed=1),
        grid_origin_x=-127.9337158203125,
        grid_origin_y=-2.0025634765625,
        interactive=False,
    )
    view2 = MAUPWidget(
        canvas_size = 300,
        grid_type = "square",
        cell_size = 50,
        points = generate_points(100, 300, seed=1),
        grid_origin_x=54.2108154296875,
        grid_origin_y=123.05267333984375,
        interactive=False,
    )
    mo.hstack([view1, mo.md("$\\to$"), view2], justify="center", align="center")
    return view1, view2


@app.cell
def _(mo):
    mo.md(
        r"""
        The underlaying data is exactly the same, dots have not been modified. However, the center-east of the map no longer looks dangerous. In general all areas are pretty much safe except for one redish square on the right. Different result that lead us to take completly different decisions.

        That is what the Modifiable Areal Unit Problem (MAUP) is all about. It is a fancy name for something that boils down to: the way you group your data can massively affect the results you get.

        # Why Does This Happen?

        It all comes down to aggregation. When the map’s dots (each representing an infected individual) are grouped into zones, the size, shape, and position of those zones can change the numbers you see. A tiny shift in the grid could lump a few extra dots into one cell, making it look like a hotspot. Conversely, a different configuration might spread out those dots more evenly, making the area appear safer than it really is.

        * **Arbitrary Boundaries**: Whether you're using squares, hexagons, or even administrative regions, the lines that divide the map are, in many cases, arbitrary. A small nudge of these boundaries might push a few infection dots from one cell into another, altering the average infection rate.

        * **Scale/Resolution**: The cell size matters too. Large cells smooth out the data, potentially hiding small clusters of infections. On the other hand, smaller cells can highlight micro-clusters that may not be significant when viewed in a broader context.

        * **Shape Differences**: Different shapes capture data differently. A hexagon might cover an area in a way that minimizes boundary issues compared to a square. But again, that doesn’t mean one shape is inherently “better”—it just means your conclusions might vary depending on your choice.
        """
    )
    return


@app.cell
def _(mo):
    canvas_size = mo.ui.slider(100, 800, value=500, show_value=True)
    orientation = mo.ui.slider(0, 360, value=0, show_value=True)
    grid_type = mo.ui.dropdown(options=["square", "hex"], value="square")
    cell_size = mo.ui.slider(10, 150, value=50, show_value=True)
    num_points = mo.ui.slider(50, 500, value=200, show_value=True)
    seed_slider = mo.ui.slider(0, 1000, value=0, show_value=True)

    params = mo.md(f"""
    | Parameter       | Value         |
    |-----------------|---------------|
    | Canvas Size     | {canvas_size} |
    | Orientation     | {orientation} |
    | Grid Type       | {grid_type}   |
    | Cell Size       | {cell_size}   |
    | Nº Dots         | {num_points}  |
    | Seed            | {seed_slider}        |
    """)

    regenerate = mo.ui.button(label="Regenerate")
    return (
        canvas_size,
        cell_size,
        grid_type,
        num_points,
        orientation,
        params,
        regenerate,
        seed_slider,
    )


@app.cell
def _(
    MAUPWidget,
    canvas_size,
    cell_size,
    generate_points,
    grid_type,
    mo,
    num_points,
    orientation,
    params,
    regenerate,
    seed_slider,
):
    widget = MAUPWidget(
        canvas_size=canvas_size.value,
        grid_type = grid_type.value,
        cell_size = cell_size.value,
        orientation = orientation.value,
        points=generate_points(num_points.value, canvas_size.value, seed=seed_slider.value if seed_slider.value else None),
    )
    mo.vstack(
        [
            mo.md("# Play With It\nDo not just take my word for it, try it yourself! Use the sliders to tweak the settings, then click and drag the grid on the canvas to see how different configurations completely transform the visualization.\n\nNote: Setting the seed to 0 means that no fixed seed is used—each generation will be completely random. Simply click the 'Regenerate' button to redraw a new set of points and see different outcomes."),
            mo.hstack([mo.vstack([params, mo.center(regenerate)]), widget], justify="start", gap=2),
        ],
        gap=2,
    )
    return (widget,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Solutions to MAUP

        That's content for a different note!
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        # Conclusion

        In the end, MAUP reminds us that there's no one “correct” way to see the world—just different perspectives. A slight tweak in your grid can change the story entirely, so never settle for just one view. Explore multiple configurations, question the boundaries, and let curiosity guide you to truly informed insights.
        """
    )
    return


if __name__ == "__main__":
    app.run()
