import marimo

__generated_with = "0.11.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import anywidget
    import traitlets

    class MAUPWidget(anywidget.AnyWidget):
        _esm = r"""
        function render({ model, el }) {
          // Recuperar parámetros desde Python (los puntos vienen generados en Python)
          let canvasSize = model.get("canvas_size") || 500;
          let gridType = model.get("grid_type") || "square";
          let cellSize = parseFloat(model.get("cell_size") || "50");
          let orientation = parseFloat(model.get("orientation") || "0");
          // Los puntos son generados en Python usando el seed y número de puntos deseados
          let points = model.get("points") || [];
          
          // Crear canvas y configurar dimensiones
          const canvas = document.createElement("canvas");
          canvas.width = canvasSize;
          canvas.height = canvasSize;
          canvas.style.border = "1px solid #ccc";
          el.innerHTML = "";
          el.appendChild(canvas);
          const ctx = canvas.getContext("2d");
          
          // Variables para mover la cuadrícula
          let offsetX = 0, offsetY = 0;
          let dragging = false;
          let dragStartX = 0, dragStartY = 0;
          let startOffsetX = 0, startOffsetY = 0;
          
          const sqrt3 = Math.sqrt(3);
          
          // Función para transformar coordenadas globales a las coordenadas de la grilla (sin traslación)
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
          
          // Para la cuadrícula cuadrada: calcular los límites de celdas que cubren el canvas.
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
          
          // Para la cuadrícula hexagonal: calcular un rango aproximado de celdas en coordenadas axiales
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
              // Conversión a coordenadas axiales fraccionarias
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
          
          // Cálculo de recuento de puntos para cuadrícula hexagonal
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
          
          // Función para dibujar la cuadrícula cuadrada y su heatmap
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
                const red = Math.round(255 * intensity);
                ctx.fillStyle = `rgba(${red}, 0, 0, 0.5)`;
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
          
          // Función para dibujar la cuadrícula hexagonal y su heatmap
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
                const red = Math.round(255 * intensity);
                ctx.fillStyle = `rgba(${red}, 0, 0, 0.5)`;
                // Calcular centro del hexágono en coordenadas de grilla
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
          
          // Dibujar los puntos
          function drawPoints() {
            ctx.fillStyle = "black";
            for (const p of points) {
              ctx.fillRect(p.x - 1, p.y - 1, 3, 3);
            }
          }
          
          // Función principal de dibujo
          function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawPoints();
            if (gridType === "square") {
              drawSquareGrid();
            } else if (gridType === "hex") {
              drawHexGrid();
            }
          }
          
          // Eventos para mover la cuadrícula
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
          });
          
          // Actualizar parámetros al recibir cambios desde Python
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
          // Cuando cambie la lista de puntos, se redibuja
          model.on("change:points", () => {
            points = model.get("points") || [];
            draw();
          });
          
          // Dibujo inicial
          draw();
          model.set("ready", true);
          model.save_changes();
        }
        
        export default { render };
        """
        
        # Parámetros expuestos a Python (sincronizados)
        canvas_size = traitlets.Int(500).tag(sync=True)
        grid_type = traitlets.Unicode("square").tag(sync=True)   # "square" o "hex"
        cell_size = traitlets.Float(50.0).tag(sync=True)
        orientation = traitlets.Float(0.0).tag(sync=True)          # en grados
        # La lista de puntos se genera en Python y se asigna a este parámetro
        points = traitlets.List(trait=traitlets.Dict(), default_value=[]).tag(sync=True)
        # El seed se usa en Python para generar los puntos (el widget solo lo recibe para referencia)
        seed = traitlets.Int(0).tag(sync=True)
        ready = traitlets.Bool(False).tag(sync=True)
    return MAUPWidget, anywidget, traitlets


@app.cell
def _():
    import random
    import marimo as mo

    # Función para generar puntos reproducibles dado un seed, tamaño de canvas y número de puntos
    def generate_points(n, canvas_size, seed):
        random.seed(seed)
        return [{"x": random.uniform(0, canvas_size), "y": random.uniform(0, canvas_size)} for _ in range(n)]

    # Crear controles de Marimo
    tamanio = mo.ui.slider(100, 800, value=500, show_value=True)
    orientacion = mo.ui.slider(0, 360, value=0, show_value=True)
    tipo_grid = mo.ui.dropdown(options=["square", "hex"], value="square")
    tam_celda = mo.ui.slider(10, 150, value=50, show_value=True)
    num_pts = mo.ui.slider(50, 500, value=200, show_value=True)
    seed_val = mo.ui.slider(0, 1000, value=0, show_value=True)

    params = mo.md(f"""
    -------------------------------
    | Parámetro       | Valor     |
    |-----------------|-----------|
    | Tamaño          | {tamanio} |
    | Orientación     | {orientacion} |
    | Tipo de Grid    | {tipo_grid} |
    | Tamaño de Celda | {tam_celda} |
    | Nº de Puntos    | {num_pts} |
    | Seed            | {seed_val} |
    """)
    return (
        generate_points,
        mo,
        num_pts,
        orientacion,
        params,
        random,
        seed_val,
        tam_celda,
        tamanio,
        tipo_grid,
    )


@app.cell
def _(
    MAUPWidget,
    generate_points,
    mo,
    num_pts,
    orientacion,
    params,
    seed_val,
    tam_celda,
    tamanio,
    tipo_grid,
):
    # Generar puntos iniciales en Python usando el seed
    points = generate_points(num_pts.value, tamanio.value, seed_val.value)

    # Instanciar el widget con los parámetros iniciales (incluyendo los puntos ya generados)
    widget = MAUPWidget(
        canvas_size = tamanio.value,
        grid_type = tipo_grid.value,
        cell_size = tam_celda.value,
        orientation = orientacion.value,
        points = points,
        seed = seed_val.value
    )
    mo.hstack([params, widget], justify="start")
    return points, widget


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
