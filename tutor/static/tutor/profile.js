/* Cardul „Nivelul tău”: nivelul ca scară grafică, drumul prin curs pe module și ce știe tutorele despre elev.
   Folosit în fereastra din meniul contului (app.js) și în tab-ul „Nivelul tău” din pagina de progres (progress.js). */
window.PTProfile = (() => {
  "use strict";

  const LEVELS = ["Începător absolut", "Începător", "Intermediar", "Avansat", "Expert"];

  /** Treapta (0–4, cu jumătăți pentru „+”) din textul liber scris de tutore, ex. „începător+ (știe PHP)”. */
  function levelIndex(text) {
    const t = (text || "").toLowerCase();
    let i = null;
    if (/expert|profesionist|senior/.test(t)) i = 4;
    else if (/avansat/.test(t) && !/încep|incep|intermediar/.test(t)) i = 3;
    else if (/intermediar/.test(t)) i = 2;
    else if (/absolut|zero/.test(t)) i = 0;
    else if (/încep|incep/.test(t)) i = 1;
    if (i === null) return null;
    if (i < 4 && (/\+/.test(t) || (i < 3 && /avansat/.test(t)))) i += 0.5;  // „începător+”, „începător avansat”
    return i;
  }

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  // Scara: 5 trepte, fiecare cu iconița ei; cele atinse au bara plină, cea curentă e evidențiată
  // (pe jumătate plină la „începător+”).
  const LEVEL_ICONS = ["sprout", "chart-column", "book-open", "rocket", "trophy"];
  function ladder(level) {
    const idx = levelIndex(level);
    const box = el("div", "lvl");
    box.setAttribute("role", "img");
    box.setAttribute("aria-label", idx === null ? "Nivel necunoscut" : `Nivel: ${level}, treapta ${Math.floor(idx) + 1} din ${LEVELS.length}`);
    const steps = el("div", "lvl-steps");
    LEVELS.forEach((name, i) => {
      const s = el("div", "lvl-step");
      const tile = el("div", "lvl-tile");
      tile.append(PTIcons.el(LEVEL_ICONS[i], "lvl-icon"), el("span", "lvl-bar"));
      if (idx !== null && i <= idx) s.classList.add("reached");
      if (idx !== null && i === Math.floor(idx)) s.classList.add(idx % 1 ? "current half" : "current");
      s.append(tile, el("span", "lvl-name", name));
      steps.append(s);
    });
    box.append(steps);
    return box;
  }

  // Ce știe tutorele despre elev: câte un card cu iconiță și culoare.
  const FACTS = [
    ["summary", "Despre nivel", "target", "blue"],
    ["goals", "Obiective", "book-marked", "green"],
    ["strengths", "Puncte forte", "star", "yellow"],
    ["weaknesses", "De lucrat", "briefcase", "purple"],
  ];

  // Drumul prin curs: un segment pe modul, lat cât numărul de subiecte, umplut cât e învățat / în lucru.
  function track(modules) {
    const box = el("div", "pc-track");
    let current = null;
    modules.forEach((m) => {
      const n = m.topics.length;
      const done = m.topics.filter((t) => t.status === "învățat").length;
      const doing = m.topics.filter((t) => t.status === "în lucru").length;
      const seg = el("div", "pc-seg");
      seg.style.flexGrow = n;
      seg.title = `${m.title}: ${done}/${n} învățate${doing ? `, ${doing} în lucru` : ""}`;
      const fd = el("span", "done");
      fd.style.width = (done / n) * 100 + "%";
      const fg = el("span", "doing");
      fg.style.width = (doing / n) * 100 + "%";
      seg.append(fd, fg);
      if (doing || (done && done < n)) { seg.classList.add("active"); current = current || { m, done, n }; }
      box.append(seg);
    });
    return { box, current };
  }

  /** Construiește cardul în `card`. `data` = răspunsul de la /api/progress; `onReset` (opțional) primește butonul de resetare. */
  function render(card, data, { onReset } = {}) {
    const p = data.profile;
    const all = data.modules.flatMap((m) => m.topics);
    const done = all.filter((t) => t.status === "învățat").length;
    const doing = all.filter((t) => t.status === "în lucru").length;

    card.innerHTML = "";
    const level = p.level || "încă necunoscut";
    card.append(el("div", "pc-label", "Nivelul tău"), el("div", "pc-level", level[0].toUpperCase() + level.slice(1)));
    card.append(ladder(p.level));

    const { box, current } = track(data.modules);
    card.append(el("div", "pc-label pc-track-label", "Drumul prin curs"), box);
    const stats = el("div", "pc-stats");
    stats.append(el("span", "st-done", `${done} învățate`), " · ", el("span", "st-doing", `${doing} în lucru`),
      ` · ${all.length} subiecte`);
    if (current) stats.append(" · acum: ", el("strong", "", `${current.m.title} (${current.done}/${current.n})`));
    card.append(stats);

    const facts = FACTS.filter(([key]) => p[key]);
    if (facts.length) {
      const list = el("div", "pc-facts");
      facts.forEach(([key, label, icon, color]) => {
        const f = el("div", "pc-fact " + color);
        const tile = el("span", "pc-fact-icon");
        tile.append(PTIcons.el(icon));
        const text = el("div", "pc-fact-text");
        text.append(el("div", "pc-label", label), el("p", "", p[key]));
        f.append(tile, text);
        list.append(f);
      });
      card.append(list);
    }
    if (!p.level && !done && !doing) {
      card.append(el("p", "pc-summary muted", "Tutorele te cunoaște după primele mesaje din chat. Progresul apare aici pe măsură ce rezolvi exerciții."));
    }
    if (onReset) {
      const reset = el("button", "text-btn danger pc-reset", "Resetează progresul");
      reset.addEventListener("click", onReset);
      card.append(reset);
    }
  }

  return { render, levelIndex };
})();
