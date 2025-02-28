function render({ model, el }) {
    // Ensure our container allows absolute positioning.
    el.style.position = "relative";

    function create_html() {
        let matrix = model.get("matrix");
        let colors = model.get("colors");
        // Check if an origin is provided.
        let providedOrigin = model.get("origin");
        // If no origin is provided, default to [0,0] but do not show axis.
        let origin = providedOrigin || [0,0];
        let showAxis = (providedOrigin !== undefined && providedOrigin !== null);
        let coordinateSystem = model.get("coordinate_system");
        if (!["row,column", "x,y"].includes(coordinateSystem)) {
          throw new Error(`Unknown coordinate system provided: ${coordinateSystem}`);
        }
        el.innerHTML = ''; // Clear previous content

        let table = document.createElement("table");
        table.classList.add("heatmap-table");

        // --- Color Helpers ---
        function parseColor(color) {
            if (typeof color === "string") {
                return color;
            } else if (Array.isArray(color) && color.length === 3) {
                // Assume RGB tuple.
                return `rgba(${color[0]}, ${color[1]}, ${color[2]})`;
            } else if (Array.isArray(color) && color.length === 4) {
                // Assume RGBA tuple, converting alpha to 0-1.
                return `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${color[3] / 255})`;
            }
            return "black"; // Fallback.
        }

        function colorToRGBA(color) {
            if (color[0] === "#") {
                let hex = color.slice(1);
                if (hex.length === 3) {
                    let r = parseInt(hex[0] + hex[0], 16);
                    let g = parseInt(hex[1] + hex[1], 16);
                    let b = parseInt(hex[2] + hex[2], 16);
                    return [r, g, b, 255];
                } else if (hex.length === 6) {
                    let r = parseInt(hex.slice(0,2), 16);
                    let g = parseInt(hex.slice(2,4), 16);
                    let b = parseInt(hex.slice(4,6), 16);
                    return [r, g, b, 255];
                } else if (hex.length === 8) {
                    let r = parseInt(hex.slice(0,2), 16);
                    let g = parseInt(hex.slice(2,4), 16);
                    let b = parseInt(hex.slice(4,6), 16);
                    let a = parseInt(hex.slice(6,8), 16);
                    return [r, g, b, a];
                }
                return [0, 0, 0, 255];
            } else {
                let ctx = document.createElement("canvas").getContext("2d");
                ctx.fillStyle = color;
                let computed = ctx.fillStyle;
                if (computed[0] === "#") {
                    return colorToRGBA(computed);
                }
                let match = computed.match(/\\d+/g);
                if (!match) {
                    return [0, 0, 0, 255];
                }
                let rgba = match.map(Number);
                return rgba.length === 3 ? [...rgba, 255] : rgba;
            }
        }

        let parsedColors = colors.map(c => parseColor(c));
        let rgbaColors = parsedColors.map(c => colorToRGBA(c));

        // --- Color Interpolation ---
        function lerp(a, b, t) {
            return Math.round(a * (1 - t) + b * t);
        }

        function getInterpolatedColor(t) {
            if (rgbaColors.length === 0) {
                return [0, 0, 0, 255];
            }
            if (rgbaColors.length === 1) {
                return rgbaColors[0];
            }
            if (t <= 0) return rgbaColors[0];
            if (t >= 1) return rgbaColors[rgbaColors.length - 1];

            let nSegments = rgbaColors.length - 1;
            let segment = Math.floor(t * nSegments);
            let tLocal = (t - (segment / nSegments)) * nSegments;
            let c1 = rgbaColors[segment];
            let c2 = rgbaColors[segment + 1];
            return [
                lerp(c1[0], c2[0], tLocal),
                lerp(c1[1], c2[1], tLocal),
                lerp(c1[2], c2[2], tLocal),
                lerp(c1[3], c2[3], tLocal)
            ];
        }

        // --- Determine data range for normalization ---
        let flatMatrix = matrix.flat();
        let min = Math.min(...flatMatrix);
        let max = Math.max(...flatMatrix);

        // --- Build the grid ---
        matrix.forEach((row, rowIndex) => {
            let tr = document.createElement("tr");
            row.forEach((value, colIndex) => {
                let td = document.createElement("td");

                // Compute the axis coordinate for this cell.
                // x = (column index) - (origin column)
                // y = (row index) - (origin row)
                let x = colIndex - origin[1];
                let y = rowIndex - origin[0];

                if (showAxis) {
                    if (x === 0 && y === 0) {
                        td.classList.add("origin-cell");
                    }
                    if (y === 0) {
                        td.classList.add("x-axis");
                    }
                    if (x === 0) {
                        td.classList.add("y-axis");
                    }
                }

                let div = document.createElement("div");
                div.classList.add("cell-content");

                let coordSpan = document.createElement("span");
                coordSpan.classList.add("cell-coordinates");
                let coordText = coordinateSystem === "row,column" ? `(${y},${x})` : `(${x},${y})`;
                coordSpan.innerHTML = coordText;

                let valueSpan = document.createElement("span");
                valueSpan.classList.add("cell-value");
                valueSpan.innerHTML = value;

                div.appendChild(coordSpan);
                div.appendChild(valueSpan);
                td.appendChild(div);

                let normalizedValue = (max - min) ? (value - min) / (max - min) : 0;
                let [r, g, b, a] = getInterpolatedColor(normalizedValue);
                td.style.backgroundColor = `rgba(${r}, ${g}, ${b}, ${a / 255})`;

                let brightness = (r * 299 + g * 587 + b * 114) / 1000;
                let textColor = brightness < 128 ? "white" : "black";
                coordSpan.style.color = textColor;
                valueSpan.style.color = textColor;

                tr.appendChild(td);
            });
            table.appendChild(tr);
        });

        el.appendChild(table);

        // Draw axis arrows only if an origin is provided.
        if (showAxis) {
            drawArrows();
        }
    }

    // Draw an overlay SVG with two arrows starting at the TOP-LEFT corner of the origin cell.
    function drawArrows() {
        let originCell = el.querySelector('.origin-cell');
        if (!originCell) return;
        let cellRect = originCell.getBoundingClientRect();
        let containerRect = el.getBoundingClientRect();
        // Compute the TOP-LEFT corner of the origin cell.
        let startX = cellRect.left - containerRect.left;
        let startY = cellRect.top - containerRect.top;
        let arrowLength = cellRect.width; // assuming square cells

        let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("class", "arrow-overlay");
        svg.style.position = "absolute";
        svg.style.top = "0";
        svg.style.left = "0";
        svg.style.width = "100%";
        svg.style.height = "100%";
        svg.style.pointerEvents = "none";

        let defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");

        // Right arrow marker.
        let markerRight = document.createElementNS("http://www.w3.org/2000/svg", "marker");
        markerRight.setAttribute("id", "markerRight");
        markerRight.setAttribute("markerWidth", "10");
        markerRight.setAttribute("markerHeight", "10");
        markerRight.setAttribute("refX", "0");
        markerRight.setAttribute("refY", "3");
        markerRight.setAttribute("orient", "auto");
        let pathRight = document.createElementNS("http://www.w3.org/2000/svg", "path");
        pathRight.setAttribute("d", "M0,0 L0,6 L6,3 z");
        pathRight.setAttribute("fill", "black");
        markerRight.appendChild(pathRight);
        defs.appendChild(markerRight);

        // Down arrow marker.
        let markerDown = document.createElementNS("http://www.w3.org/2000/svg", "marker");
        markerDown.setAttribute("id", "markerDown");
        markerDown.setAttribute("markerWidth", "10");
        markerDown.setAttribute("markerHeight", "10");
        // Set the reference point so the tip touches the end of the line.
        markerDown.setAttribute("refX", "3");
        markerDown.setAttribute("refY", "0");
        markerDown.setAttribute("orient", "down");
        let pathDown = document.createElementNS("http://www.w3.org/2000/svg", "path");
        // Define a triangle that points down.
        pathDown.setAttribute("d", "M0,0 L6,0 L3,6 z");
        pathDown.setAttribute("fill", "black");
        markerDown.appendChild(pathDown);
        defs.appendChild(markerDown);

        svg.appendChild(defs);

        // Draw the horizontal arrow (pointing right) from the top-left corner.
        let lineX = document.createElementNS("http://www.w3.org/2000/svg", "line");
        lineX.setAttribute("x1", startX);
        lineX.setAttribute("y1", startY);
        lineX.setAttribute("x2", startX + arrowLength);
        lineX.setAttribute("y2", startY);
        lineX.setAttribute("stroke", "black");
        lineX.setAttribute("stroke-width", "2");
        lineX.setAttribute("marker-end", "url(#markerRight)");
        svg.appendChild(lineX);

        // Draw the vertical arrow (pointing down) from the top-left corner.
        let lineY = document.createElementNS("http://www.w3.org/2000/svg", "line");
        lineY.setAttribute("x1", startX);
        lineY.setAttribute("y1", startY);
        lineY.setAttribute("x2", startX);
        lineY.setAttribute("y2", startY + arrowLength);
        lineY.setAttribute("stroke", "black");
        lineY.setAttribute("stroke-width", "2");
        lineY.setAttribute("marker-end", "url(#markerDown)");
        svg.appendChild(lineY);

        el.appendChild(svg);
    }

    create_html();
    model.on("change:matrix", create_html);
    model.on("change:colors", create_html);
    model.on("change:origin", create_html);
    model.on("change:coordinate_system", create_html);
}
export default { render };
