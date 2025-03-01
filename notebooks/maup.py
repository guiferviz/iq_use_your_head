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
          // Dimensiones del canvas
          const width = 500;
          const height = 500;
          const sqrt3 = Math.sqrt(3);

          // Crear elementos de control (tipo de cuadrícula, tamaño, orientación)
          const controlsDiv = document.createElement("div");
          controlsDiv.style.marginBottom = "8px";

          // Selector de tipo de cuadrícula
          const typeLabel = document.createElement("label");
          typeLabel.textContent = "Tipo de cuadrícula: ";
          const selectGrid = document.createElement("select");
          const optSquare = document.createElement("option");
          optSquare.value = "square";
          optSquare.text = "Cuadrada";
          const optHex = document.createElement("option");
          optHex.value = "hex";
          optHex.text = "Hexagonal";
          selectGrid.append(optSquare, optHex);
          typeLabel.appendChild(selectGrid);
          controlsDiv.appendChild(typeLabel);

          // Control de tamaño de celda
          const sizeLabel = document.createElement("label");
          sizeLabel.textContent = " Tamaño: ";
          const sizeValue = document.createElement("span");  // mostrará el valor numérico
          const sizeInput = document.createElement("input");
          sizeInput.type = "range";
          sizeInput.min = "10";
          sizeInput.max = "100";
          sizeInput.value = "50";
          sizeInput.style.verticalAlign = "middle";
          sizeValue.textContent = sizeInput.value;
          sizeLabel.appendChild(sizeInput);
          sizeLabel.appendChild(sizeValue);
          controlsDiv.appendChild(sizeLabel);

          // Control de orientación (ángulo de rotación)
          const angleLabel = document.createElement("label");
          angleLabel.textContent = " Orientación: ";
          const angleValue = document.createElement("span");
          const angleInput = document.createElement("input");
          angleInput.type = "range";
          angleInput.min = "0";
          angleInput.max = "180";
          angleInput.value = "0";
          angleInput.style.verticalAlign = "middle";
          angleValue.textContent = angleInput.value;
          angleLabel.appendChild(angleInput);
          angleLabel.appendChild(angleValue);
          controlsDiv.appendChild(angleLabel);

          // Añadir el panel de controles al elemento principal del widget
          el.appendChild(controlsDiv);

          // Crear el canvas donde se dibujarán puntos y rejilla
          const canvas = document.createElement("canvas");
          canvas.width = width;
          canvas.height = height;
          canvas.style.border = "1px solid #ccc";  // borde para visualizar límites
          el.appendChild(canvas);
          const ctx = canvas.getContext("2d");

          // Generar puntos aleatorios uniformes sobre el canvas
          const numPoints = 200;
          const points = [];
          for (let i = 0; i < numPoints; i++) {
            points.push({ 
              x: Math.random() * width, 
              y: Math.random() * height 
            });
          }

          // Estado inicial de la cuadrícula
          let gridType = selectGrid.value;    // "square" o "hex"
          let cellSize = parseFloat(sizeInput.value);
          let angleDeg = parseFloat(angleInput.value);
          let offsetX = 0, offsetY = 0;       // desplazamiento de la cuadrícula
          let dragging = false;
          let dragStartX = 0, dragStartY = 0;
          let startOffsetX = 0, startOffsetY = 0;

          // Función para dibujar puntos y cuadrícula (heatmap)
          function drawGrid() {
            ctx.clearRect(0, 0, width, height);
            // Dibujar puntos (pequeños cuadrados negros de 2x2 píxeles)
            ctx.fillStyle = "black";
            for (const p of points) {
              ctx.fillRect(p.x, p.y, 2, 2);
            }
            // Calcular conteos de puntos por celda
            const cellCounts = new Map();
            let maxCount = 0;
            const theta = angleDeg * Math.PI / 180;  // convertir ángulo a radianes
            const cosT = Math.cos(theta);
            const sinT = Math.sin(theta);

            if (gridType === "square") {
              // Recorrer puntos y asignar a celdas cuadradas
              for (const p of points) {
                // Coordenadas del punto relativas al origen de la cuadrícula (offset)
                const relX = p.x - offsetX;
                const relY = p.y - offsetY;
                // Rotar inversamente el punto para alinear con la grilla sin rotación
                const gridX = relX * cosT + relY * sinT;
                const gridY = -relX * sinT + relY * cosT;
                // Índices de celda (i, j) usando división entera (floor)
                const i = Math.floor(gridX / cellSize);
                const j = Math.floor(gridY / cellSize);
                const key = `${i},${j}`;
                const count = cellCounts.get(key) ?? 0;
                cellCounts.set(key, count + 1);
                if (count + 1 > maxCount) {
                  maxCount = count + 1;
                }
              }
              // Determinar el rango de celdas a dibujar (incluye celdas vacías adyacentes)
              let minI = Infinity, maxI = -Infinity;
              let minJ = Infinity, maxJ = -Infinity;
              for (let key of cellCounts.keys()) {
                const [i, j] = key.split(",").map(Number);
                if (i < minI) minI = i;
                if (i > maxI) maxI = i;
                if (j < minJ) minJ = j;
                if (j > maxJ) maxJ = j;
              }
              // Agregar un borde de una celda alrededor del rango ocupado
              minI--; minJ--;
              maxI++; maxJ++;
              // Añadir celdas vacías dentro del rango para visualizarlas en negro
              for (let i = minI; i <= maxI; i++) {
                for (let j = minJ; j <= maxJ; j++) {
                  const key = `${i},${j}`;
                  if (!cellCounts.has(key)) {
                    cellCounts.set(key, 0);
                  }
                }
              }
              // Dibujar cada celda cuadrada con color según densidad
              cellCounts.forEach((count, key) => {
                const [i, j] = key.split(",").map(Number);
                // Calcular intensidad de color (0 = negro, 1 = rojo)
                const intensity = maxCount ? (count / maxCount) : 0;
                const red = Math.round(255 * intensity);
                ctx.fillStyle = `rgba(${red}, 0, 0, 0.5)`;  // color con transparencia
                // Coordenadas de las esquinas de la celda en espacio de la grilla (no rotado)
                const x0 = i * cellSize;
                const y0 = j * cellSize;
                const corners = [
                  { x: x0,            y: y0 },
                  { x: x0 + cellSize, y: y0 },
                  { x: x0 + cellSize, y: y0 + cellSize },
                  { x: x0,            y: y0 + cellSize }
                ];
                // Dibujar polígono de la celda cuadrada aplicando rotación y offset
                ctx.beginPath();
                corners.forEach((c, index) => {
                  // Transformar cada esquina de la celda a coordenadas globales (rotar + desplazar)
                  const globalX = offsetX + c.x * cosT - c.y * sinT;
                  const globalY = offsetY + c.x * sinT + c.y * cosT;
                  if (index === 0) ctx.moveTo(globalX, globalY);
                  else ctx.lineTo(globalX, globalY);
                });
                ctx.closePath();
                ctx.fill();
              });

            } else if (gridType === "hex") {
              const R = cellSize;  // tomamos cellSize como "radio" (centro a vértice)
              // Recorrer puntos y asignar a celdas hexagonales
              for (const p of points) {
                const relX = p.x - offsetX;
                const relY = p.y - offsetY;
                // Rotar inversamente punto a la alineación base de la grilla hex
                const gridX = relX * cosT + relY * sinT;
                const gridY = -relX * sinT + relY * cosT;
                // Calcular coordenadas axiales fraccionarias (q, r) del hexágono correspondiente
                const q_frac = (gridX * (sqrt3/3) - gridY * (1/3)) / R;
                const r_frac = (gridY * (2/3)) / R;
                // Convertir a coordenadas "cube" para redondeo
                let q = q_frac;
                let r = r_frac;
                let s = -q - r;
                let rq = Math.round(q);
                let rr = Math.round(r);
                let rs = Math.round(s);
                // Ajustar el componente con mayor error para asegurar q+r+s=0
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
                // Ahora (rq, rr) son coordenadas axiales enteras del hexágono
                const key = `${rq},${rr}`;
                const count = cellCounts.get(key) ?? 0;
                cellCounts.set(key, count + 1);
                if (count + 1 > maxCount) {
                  maxCount = count + 1;
                }
              }
              // Agregar celdas hexagonales adyacentes vacías para completar huecos en la visualización
              const existingCells = Array.from(cellCounts.keys()).map(k => k.split(",").map(Number));
              for (const [q, r] of existingCells) {
                const neighbors = [
                  [q+1, r], [q-1, r], [q, r+1], [q, r-1], [q+1, r-1], [q-1, r+1]
                ];
                for (const [nq, nr] of neighbors) {
                  const nKey = `${nq},${nr}`;
                  if (!cellCounts.has(nKey)) {
                    cellCounts.set(nKey, 0);
                  }
                }
              }
              // Precalcular offsets de los 6 vértices de un hexágono centrado en (0,0) en coords de grilla
              const hexCornerOffsets = [
                { x: 0,       y: -R },
                { x:  sqrt3/2 * R, y: -0.5 * R },
                { x:  sqrt3/2 * R, y:  0.5 * R },
                { x: 0,       y:  R },
                { x: -sqrt3/2 * R, y:  0.5 * R },
                { x: -sqrt3/2 * R, y: -0.5 * R }
              ];
              // Dibujar cada celda hexagonal
              cellCounts.forEach((count, key) => {
                const [q, r] = key.split(",").map(Number);
                const intensity = maxCount ? (count / maxCount) : 0;
                const red = Math.round(255 * intensity);
                ctx.fillStyle = `rgba(${red}, 0, 0, 0.5)`;
                // Calcular centro del hexágono (q,r) en coordenadas de la grilla sin rotar
                const centerX = R * sqrt3 * (q + 0.5 * r);
                const centerY = R * 1.5 * r;
                // Traazar polígono hexagonal rotando y trasladando cada vértice desde el centro
                ctx.beginPath();
                hexCornerOffsets.forEach((offset, index) => {
                  const cornerX = centerX + offset.x;
                  const cornerY = centerY + offset.y;
                  // Transformar a coordenadas globales (aplicar rotación y offset de la cuadrícula)
                  const globalX = offsetX + cornerX * cosT - cornerY * sinT;
                  const globalY = offsetY + cornerX * sinT + cornerY * cosT;
                  if (index === 0) ctx.moveTo(globalX, globalY);
                  else ctx.lineTo(globalX, globalY);
                });
                ctx.closePath();
                ctx.fill();
              });
            }
          }

          // Eventos de interacción de los controles
          selectGrid.addEventListener("change", () => {
            gridType = selectGrid.value;
            drawGrid();
          });
          sizeInput.addEventListener("input", () => {
            cellSize = parseFloat(sizeInput.value);
            sizeValue.textContent = sizeInput.value;
            drawGrid();
          });
          angleInput.addEventListener("input", () => {
            angleDeg = parseFloat(angleInput.value);
            angleValue.textContent = angleInput.value;
            drawGrid();
          });

          // Eventos para arrastrar la cuadrícula con el mouse (pointer events para incluir mouse/touch)
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
            // Calcular desplazamiento desde el inicio del arrastre
            const dx = e.clientX - dragStartX;
            const dy = e.clientY - dragStartY;
            offsetX = startOffsetX + dx;
            offsetY = startOffsetY + dy;
            drawGrid();
          });
          canvas.addEventListener("pointerup", () => {
            dragging = false;
          });

          // Dibujo inicial
          drawGrid();
        }
        export default { render };
        """
    return MAUPWidget, anywidget, traitlets


@app.cell
def _():
    import marimo as mo
    mo.md(f"""
    -----------------
    | Parametro | Valor |
    |--------|------------------------|
    | Tamaño | {mo.ui.slider(1, 500, show_value=True)} |
    | Orientación | {mo.ui.slider(0, 360, show_value=True)} |
    """)
    return (mo,)


@app.cell
def _(MAUPWidget):
    w2 = MAUPWidget()
    w2
    return (w2,)


@app.cell
def _(anywidget, traitlets):
    class MAUPWidget2(anywidget.AnyWidget):
        _esm = r"""
        function render({ model, el }) {
          // Recuperar parámetros iniciales enviados desde Python
          let canvasSize = model.get("canvas_size") || 500;
          let gridType = model.get("grid_type") || "square";
          let cellSize = parseFloat(model.get("cell_size") || "50");
          let orientation = parseFloat(model.get("orientation") || "0");
          let numPoints = model.get("num_points") || 200;
          // regen_points es un contador: cada cambio (incremento) regenera los puntos.
          let regenPoints = model.get("regen_points") || 0;
          
          // Crear el canvas con dimensiones definidas por canvasSize
          const canvas = document.createElement("canvas");
          canvas.width = canvasSize;
          canvas.height = canvasSize;
          canvas.style.border = "1px solid #ccc";
          el.appendChild(canvas);
          const ctx = canvas.getContext("2d");
          
          // Variables para los puntos y para el arrastre de la cuadrícula
          let points = [];
          
          // Función para generar puntos aleatorios uniformes en el canvas
          function generatePoints() {
            points = [];
            for (let i = 0; i < numPoints; i++) {
              points.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height
              });
            }
          }
          generatePoints();
          
          // Variables para el offset de la cuadrícula y arrastre
          let offsetX = 0, offsetY = 0;
          let dragging = false;
          let dragStartX = 0, dragStartY = 0;
          let startOffsetX = 0, startOffsetY = 0;
          
          // Función para dibujar el mapa (puntos y cuadrícula con heatmap)
          function drawGrid() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            // Dibujar los puntos (como pequeños cuadrados negros)
            ctx.fillStyle = "black";
            for (const p of points) {
              ctx.fillRect(p.x, p.y, 2, 2);
            }
            // Calcular los conteos de puntos por celda
            const cellCounts = new Map();
            let maxCount = 0;
            const theta = orientation * Math.PI / 180;
            const cosT = Math.cos(theta);
            const sinT = Math.sin(theta);
            const sqrt3 = Math.sqrt(3);
            
            if (gridType === "square") {
              // Asignar cada punto a una celda cuadrada
              for (const p of points) {
                const relX = p.x - offsetX;
                const relY = p.y - offsetY;
                const gridX = relX * cosT + relY * sinT;
                const gridY = -relX * sinT + relY * cosT;
                const i = Math.floor(gridX / cellSize);
                const j = Math.floor(gridY / cellSize);
                const key = `${i},${j}`;
                const count = cellCounts.get(key) || 0;
                cellCounts.set(key, count + 1);
                if (count + 1 > maxCount) { maxCount = count + 1; }
              }
              // Determinar el rango de celdas a dibujar
              let minI = Infinity, maxI = -Infinity, minJ = Infinity, maxJ = -Infinity;
              for (let key of cellCounts.keys()) {
                const [i, j] = key.split(",").map(Number);
                if (i < minI) minI = i;
                if (i > maxI) maxI = i;
                if (j < minJ) minJ = j;
                if (j > maxJ) maxJ = j;
              }
              // Ampliar el rango para mostrar borde completo
              minI--; minJ--;
              maxI++; maxJ++;
              for (let i = minI; i <= maxI; i++) {
                for (let j = minJ; j <= maxJ; j++) {
                  const key = `${i},${j}`;
                  if (!cellCounts.has(key)) {
                    cellCounts.set(key, 0);
                  }
                }
              }
              // Dibujar cada celda con color basado en la densidad de puntos
              cellCounts.forEach((count, key) => {
                const [i, j] = key.split(",").map(Number);
                const intensity = maxCount ? (count / maxCount) : 0;
                const red = Math.round(255 * intensity);
                ctx.fillStyle = `rgba(${red}, 0, 0, 0.5)`;
                const x0 = i * cellSize;
                const y0 = j * cellSize;
                const corners = [
                  { x: x0, y: y0 },
                  { x: x0 + cellSize, y: y0 },
                  { x: x0 + cellSize, y: y0 + cellSize },
                  { x: x0, y: y0 + cellSize }
                ];
                ctx.beginPath();
                corners.forEach((corner, index) => {
                  const globalX = offsetX + corner.x * cosT - corner.y * sinT;
                  const globalY = offsetY + corner.x * sinT + corner.y * cosT;
                  if (index === 0) ctx.moveTo(globalX, globalY);
                  else ctx.lineTo(globalX, globalY);
                });
                ctx.closePath();
                ctx.fill();
              });
            } else if (gridType === "hex") {
              // Asignar puntos a celdas hexagonales
              for (const p of points) {
                const relX = p.x - offsetX;
                const relY = p.y - offsetY;
                const gridX = relX * cosT + relY * sinT;
                const gridY = -relX * sinT + relY * cosT;
                const q_frac = (gridX * (sqrt3/3) - gridY / 3) / cellSize;
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
                const count = cellCounts.get(key) || 0;
                cellCounts.set(key, count + 1);
                if (count + 1 > maxCount) { maxCount = count + 1; }
              }
              // Asegurar que se dibujen celdas adyacentes vacías
              const existingCells = Array.from(cellCounts.keys()).map(k => k.split(",").map(Number));
              for (const [q, r] of existingCells) {
                const neighbors = [
                  [q+1, r], [q-1, r], [q, r+1], [q, r-1], [q+1, r-1], [q-1, r+1]
                ];
                for (const [nq, nr] of neighbors) {
                  const nKey = `${nq},${nr}`;
                  if (!cellCounts.has(nKey)) {
                    cellCounts.set(nKey, 0);
                  }
                }
              }
              // Dibujar celdas hexagonales
              const R = cellSize;  // usar cellSize como "radio"
              const hexCornerOffsets = [
                { x: 0, y: -R },
                { x: (sqrt3/2) * R, y: -0.5 * R },
                { x: (sqrt3/2) * R, y: 0.5 * R },
                { x: 0, y: R },
                { x: - (sqrt3/2) * R, y: 0.5 * R },
                { x: - (sqrt3/2) * R, y: -0.5 * R }
              ];
              cellCounts.forEach((count, key) => {
                const [q, r] = key.split(",").map(Number);
                const intensity = maxCount ? (count / maxCount) : 0;
                const red = Math.round(255 * intensity);
                ctx.fillStyle = `rgba(${red}, 0, 0, 0.5)`;
                // Centro del hexágono en coordenadas de la grilla
                const centerX = R * sqrt3 * (q + 0.5 * r);
                const centerY = R * 1.5 * r;
                ctx.beginPath();
                hexCornerOffsets.forEach((offset, index) => {
                  const cornerX = centerX + offset.x;
                  const cornerY = centerY + offset.y;
                  const globalX = offsetX + cornerX * cosT - cornerY * sinT;
                  const globalY = offsetY + cornerX * sinT + cornerY * cosT;
                  if (index === 0) ctx.moveTo(globalX, globalY);
                  else ctx.lineTo(globalX, globalY);
                });
                ctx.closePath();
                ctx.fill();
              });
            }
          }
          
          // Manejo de eventos para arrastrar la cuadrícula
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
            let dx = e.clientX - dragStartX;
            let dy = e.clientY - dragStartY;
            offsetX = startOffsetX + dx;
            offsetY = startOffsetY + dy;
            drawGrid();
          });
          canvas.addEventListener("pointerup", () => {
            dragging = false;
          });
          
          // Observar cambios en los parámetros desde Python
          model.on("change:canvas_size", () => {
            canvas.width = model.get("canvas_size");
            canvas.height = model.get("canvas_size");
            drawGrid();
          });
          model.on("change:grid_type", () => {
            gridType = model.get("grid_type");
            drawGrid();
          });
          model.on("change:cell_size", () => {
            cellSize = parseFloat(model.get("cell_size"));
            drawGrid();
          });
          model.on("change:orientation", () => {
            orientation = parseFloat(model.get("orientation"));
            drawGrid();
          });
          model.on("change:num_points", () => {
            numPoints = model.get("num_points");
            generatePoints();
            drawGrid();
          });
          model.on("change:regen_points", () => {
            // Cada vez que se modifique regen_points se generan nuevos puntos
            generatePoints();
            drawGrid();
          });
          
          // Dibujo inicial
          drawGrid();
          model.set("ready", true);
          model.save_changes();
        }
        
        export default { render };
        """
        
        # Parámetros expuestos a Python, sincronizados con la parte JS.
        canvas_size = traitlets.Int(500).tag(sync=True)
        grid_type = traitlets.Unicode("square").tag(sync=True)   # "square" o "hex"
        cell_size = traitlets.Float(50.0).tag(sync=True)
        orientation = traitlets.Float(0.0).tag(sync=True)          # En grados
        num_points = traitlets.Int(200).tag(sync=True)
        regen_points = traitlets.Int(0).tag(sync=True)             # Al incrementar, se regeneran los puntos
        ready = traitlets.Bool(False).tag(sync=True)
    return (MAUPWidget2,)


@app.cell
def _(mo):
    # Crear controles de marimo (estos controles se mostrarán en la celda y se pueden usar para actualizar el widget)
    tamanio = mo.ui.slider(100, 800, value=500, show_value=True)
    orientacion = mo.ui.slider(0, 360, value=0, show_value=True)
    tipo_grid = mo.ui.dropdown(options=["square", "hex"], value="square")
    tam_celda = mo.ui.slider(10, 150, value=50, show_value=True)
    num_pts = mo.ui.slider(50, 500, value=200, show_value=True)

    table = mo.md(f"""
    -----------------
    | Parámetro      | Valor           |
    |----------------|-----------------|
    | Tamaño         | {tamanio}       |
    | Orientación    | {orientacion}   |
    | Tipo de Grid   | {tipo_grid}     |
    | Tamaño de Celda| {tam_celda}     |
    | Nº de Puntos   | {num_pts}       |
    """)
    return num_pts, orientacion, table, tam_celda, tamanio, tipo_grid


@app.cell
def _(
    MAUPWidget2,
    mo,
    num_pts,
    orientacion,
    table,
    tam_celda,
    tamanio,
    tipo_grid,
):
    # Instanciar el widget con los parámetros iniciales
    widget2 = MAUPWidget2(
        canvas_size=tamanio.value,
        grid_type=tipo_grid.value,
        cell_size=tam_celda.value,
        orientation=orientacion.value,
        num_points=num_pts.value
    )
    mo.hstack([table, mo.md("# $\\to$"), widget2], justify="start", align="start", wrap=True)
    return (widget2,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
