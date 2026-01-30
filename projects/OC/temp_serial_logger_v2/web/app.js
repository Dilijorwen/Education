function nowMs() { return Date.now(); }

function fmtTs(ms) {
    try { return new Date(ms).toISOString(); } catch { return String(ms); }
}

async function getJson(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(await r.text());
    return await r.json();
}

function drawChart(svg, points) {
    svg.innerHTML = "";
    if (!points.length) return;

    let min = points[0].v, max = points[0].v;
    for (const p of points) { if (p.v < min) min = p.v; if (p.v > max) max = p.v; }
    if (max === min) { max += 1; min -= 1; }

    const w = 1000, h = 260;
    const xs = points.map(p => p.t);
    const x0 = xs[0], x1 = xs[xs.length - 1] || (x0 + 1);

    function X(t) { return (t - x0) / (x1 - x0) * w; }
    function Y(v) { return (1 - (v - min) / (max - min)) * (h - 10) + 5; }

    let d = "";
    for (let i = 0; i < points.length; i++) {
        const x = X(points[i].t);
        const y = Y(points[i].v);
        d += (i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
    }

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", d);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", "#6aa6ff");
    path.setAttribute("stroke-width", "2");
    svg.appendChild(path);

    const lbl = document.createElementNS("http://www.w3.org/2000/svg", "text");
    lbl.setAttribute("x", "10");
    lbl.setAttribute("y", "20");
    lbl.setAttribute("fill", "#cfe2ff");
    lbl.setAttribute("font-size", "12");
    lbl.textContent = `min=${min.toFixed(2)} max=${max.toFixed(2)} n=${points.length}`;
    svg.appendChild(lbl);
}

function fillTable(tbody, points) {
    tbody.innerHTML = "";
    const last = points.slice(-50);
    for (const p of last) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${p.t}</td><td>${p.v.toFixed(4)}</td><td>${p.n}</td>`;
        tbody.appendChild(tr);
    }
}

async function refresh() {
    const cur = await getJson("/api/current").catch(() => null);
    document.getElementById("current").textContent = cur ? `${cur.temp_c.toFixed(2)} °C` : "—";
    document.getElementById("current_ts").textContent = cur ? fmtTs(cur.ts_ms) : "—";

    const minutes = parseInt(document.getElementById("minutes").value || "180", 10);
    const bucket = document.getElementById("bucket").value;

    const to = nowMs();
    const from = to - minutes * 60 * 1000;

    const st = await getJson(`/api/stats?from=${from}&to=${to}&bucket=${bucket}`).catch(() => null);
    document.getElementById("stats").textContent = st
        ? `bucket=${st.bucket} count=${st.count} min=${st.min.toFixed(2)} max=${st.max.toFixed(2)} avg=${st.avg.toFixed(2)}`
        : "no data";

    const series = await getJson(`/api/series?from=${from}&to=${to}&bucket=${bucket}&limit=5000`).catch(() => null);
    const pts = series ? series.points : [];

    drawChart(document.getElementById("chart"), pts);
    fillTable(document.getElementById("tbl"), pts);
}

document.getElementById("refresh").addEventListener("click", refresh);
setInterval(refresh, 5000);
refresh();
