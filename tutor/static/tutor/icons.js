/* Iconițe: Lucide (icons.svg, pus în pagină de {% icon_sprite %}, un <symbol> pe iconiță) și siglele
   limbajelor din Devicon (img/). Folosit de app.js, md.js, profile.js și progress.js.
   Adresa imaginilor vine din <body data-static="...">. */
window.PTIcons = (() => {
  "use strict";

  const base = () => document.body.dataset.static || "/static/tutor/";

  /** `<svg>` cu iconița Lucide `name` (ex. "play"), ca text HTML. */
  function svg(name, cls = "") {
    return `<svg class="i ${cls}" aria-hidden="true"><use href="#${name}"/></svg>`;
  }
  /** Același lucru, ca element DOM. */
  function el(name, cls = "") {
    const t = document.createElement("template");
    t.innerHTML = svg(name, cls);
    return t.content.firstElementChild;
  }

  // Sigla limbajului după extensie; restul fișierelor primesc o iconiță Lucide.
  const LOGOS = { py: "python-original", html: "html5-original", htm: "html5-original", css: "css3-original", js: "javascript-original" };
  function file(name, { dir = false, open = false } = {}) {
    if (dir) return svg(open ? "folder-open" : "folder", "ficon dir");
    const logo = LOGOS[(name.split(".").pop() || "").toLowerCase()];
    if (logo) return `<img class="ficon logo" src="${base()}img/${logo}.svg" alt="" aria-hidden="true">`;
    return svg("file", "ficon other");
  }
  /** Sigla unui limbaj din blocurile de cod („python”, „html”...), sau null. */
  function lang(l) {
    const ext = { python: "py", py: "py", html: "html", css: "css", js: "js", javascript: "js" }[l];
    return ext ? `<img class="lang-logo" src="${base()}img/${LOGOS[ext]}.svg" alt="" aria-hidden="true">` : null;
  }

  // Iconița fiecărui modul al cursului (aceeași în sumarul din editor și în pagina de progres; culoarea e în CSS).
  const MODULES = {
    "bazele": "square-play",
    "control": "git-branch",
    "colectii": "layers",
    "functii": "square-function",
    "erori": "bug",
    "fisiere-module": "folder-open",
    "oop": "box",
    "intermediar": "trending-up",
    "calitate": "code-xml",
    "web": "globe",
    "django-baza": "file-text",
    "django-date": "database",
    "django-interactiv": "app-window",
    "django-avansat": "rocket",
  };
  const module = (slug) => el(MODULES[slug] || "book-open", "mod-icon");

  return { svg, el, file, lang, module };
})();
