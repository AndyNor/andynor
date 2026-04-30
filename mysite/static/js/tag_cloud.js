/* Tag cloud interactions (CSP-safe: no inline styles). */
(function () {
  function qs(root, sel) {
    return root.querySelector(sel);
  }
  function qsa(root, sel) {
    return Array.prototype.slice.call(root.querySelectorAll(sel));
  }

  function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = arr[i];
      arr[i] = arr[j];
      arr[j] = tmp;
    }
    return arr;
  }

  function initTagCloud(cloud) {
    const tags = qsa(cloud, "a.tag-cloud__tag");
    if (!tags.length) return;

    // Optional "orbit" visual (SVG) for fun layout.
    const visualWrap = cloud.parentNode && cloud.parentNode.querySelector("[data-tag-cloud-visual]");
    const visualStage = visualWrap ? qs(visualWrap, ".tag-cloud-visual__stage") : null;

    // Precompute metadata without touching inline styles.
    const meta = tags.map((a) => {
      const text = (a.textContent || "").trim().toLowerCase();
      const s = /tag-cloud__tag--s(\d)/.exec(a.className);
      const size = s ? parseInt(s[1], 10) : 3;
      const w = parseFloat(a.getAttribute("data-weight") || "");
      const weight = isFinite(w) ? Math.max(0, Math.min(1, w)) : (size - 1) / 4;
      a.dataset.tcText = text;
      a.dataset.tcSize = String(size);
      a.dataset.tcWeight = String(weight);
      return a;
    });

    function renderOrbitVisual() {
      if (!visualStage) return;
      // Only render if SVG is supported and we have room.
      visualStage.textContent = "";

      // Sort by weight desc so biggest is centered.
      const sorted = meta.slice().sort((a, b) => parseFloat(b.dataset.tcWeight) - parseFloat(a.dataset.tcWeight));
      if (!sorted.length) return;

      const svgNS = "http://www.w3.org/2000/svg";
      const xlinkNS = "http://www.w3.org/1999/xlink";
      const svg = document.createElementNS(svgNS, "svg");
      svg.setAttribute("class", "tag-cloud-orbit");
      svg.setAttribute("role", "img");
      svg.setAttribute("aria-label", "Tag cloud");
      visualStage.appendChild(svg);

      const w = visualStage.clientWidth || 640;
      // Wider look: keep height relatively smaller vs width.
      const h = Math.max(220, Math.min(360, Math.round(w * 0.40)));
      svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
      svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

      const cx = w / 2;
      const cy = h / 2;
      // Use an ellipse so the cloud can fill a rectangular stage.
      const maxRx = w * 0.48;
      const maxRy = h * 0.42;

      // Helper: create a tag node.
      function makeTagNode(a) {
        const label = (a.textContent || "").trim();
        const href = a.getAttribute("href") || "#";
        const weight = parseFloat(a.dataset.tcWeight || "0.5");
        // Map weight to a 12px..36px range (~3x).
        const fontSize = 12 + Math.round(weight * 24);

        const link = document.createElementNS(svgNS, "a");
        link.setAttributeNS(xlinkNS, "xlink:href", href);
        link.setAttribute("href", href);
        link.setAttribute("class", "tag-cloud-orbit__link");

        const text = document.createElementNS(svgNS, "text");
        text.textContent = label;
        text.setAttribute("class", `tag-cloud-orbit__text tag-cloud-orbit__text--s${a.dataset.tcSize || "3"}`);
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("dominant-baseline", "middle");
        text.setAttribute("font-size", String(fontSize));

        link.appendChild(text);
        return { link, text, fontSize, weight };
      }

      // Spiral placement with simple collision avoidance.
      const placed = [];
      const golden = Math.PI * (3 - Math.sqrt(5));

      for (let i = 0; i < sorted.length && i < 250; i++) {
        const a = sorted[i];
        const node = makeTagNode(a);
        svg.appendChild(node.link);

        // Radius: more frequent => closer to center.
        const base = (1 - node.weight);
        let angle = i * golden;
        let r = Math.max(0, base * 0.15);

        // Try a few positions expanding outward.
        let ok = false;
        for (let attempt = 0; attempt < 60; attempt++) {
          const t = Math.min(1, r + (attempt * 6) / Math.max(1, Math.min(maxRx, maxRy)));
          const rrX = t * maxRx;
          const rrY = t * maxRy;
          const a = angle + attempt * 0.15;
          const x = cx + Math.cos(a) * rrX;
          const y = cy + Math.sin(a) * rrY;
          node.text.setAttribute("x", String(x));
          node.text.setAttribute("y", String(y));

          const bb = node.text.getBBox();
          // Bounds check
          if (bb.x < 4 || bb.y < 4 || bb.x + bb.width > w - 4 || bb.y + bb.height > h - 4) {
            continue;
          }
          // Collision check
          let collides = false;
          for (const p of placed) {
            if (
              bb.x < p.x + p.w + 6 &&
              bb.x + bb.width + 6 > p.x &&
              bb.y < p.y + p.h + 6 &&
              bb.y + bb.height + 6 > p.y
            ) {
              collides = true;
              break;
            }
          }
          if (!collides) {
            placed.push({ x: bb.x, y: bb.y, w: bb.width, h: bb.height });
            ok = true;
            break;
          }
        }

        if (!ok) {
          // If we can't place cleanly, hide in the visual (still available below).
          node.link.setAttribute("display", "none");
        }
      }
    }

    // Initial state
    renderOrbitVisual();

    // Keep it responsive.
    window.addEventListener("resize", function () {
      renderOrbitVisual();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".tag-cloud").forEach(initTagCloud);
  });
})();

