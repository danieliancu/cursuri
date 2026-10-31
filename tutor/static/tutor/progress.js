/* PyTutor — pagina „Progresul meu”: curriculum, lecții și dovezile de lucru ale elevului. */
(() => {
  "use strict";

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));
  const STATUS = {
    "de învățat": { cls: "todo", label: "De învățat" },
    "în lucru": { cls: "doing", label: "În lucru" },
    "învățat": { cls: "done", label: "Învățat" },
  };
  // Tolerant la statusuri necunoscute (ex. denumirea veche „stăpânit”), ca pagina să nu cadă.
  const statusOf = (s) => STATUS[s] || (s === "stăpânit" ? STATUS["învățat"] : STATUS["de învățat"]);
  const userKey = (k) => `${k}@${document.body.dataset.user || ""}`;
  const store = {
    get(k, d) { try { const v = localStorage.getItem(userKey(k)); return v === null ? d : v; } catch { return d; } },
    set(k, v) { try { localStorage.setItem(userKey(k), v); } catch { /* fără storage */ } },
  };

  // ------------------------------------------------------------------ API
  function csrf() {
    const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }
  async function api(path, opts = {}) {
    const res = await fetch(path, {
      method: opts.method || "GET",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
    });
    if (res.status === 401) location.href = "/login/?next=/progres/";
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Eroare ${res.status}`);
    return data;
  }

  // Tema: theme.js. Iconițele: icons.js.
  // Bara din stânga are lățimea aleasă în editor (app.js o salvează când tragi de margine).
  const chatW = store.get("pt-chat-w", "");
  if (chatW) document.documentElement.style.setProperty("--chat-w", chatW);

  // ------------------------------------------------------------------ Profil + curriculum
  let data = null;
  let current = null;

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function renderProfile() {
    PTProfile.render($("#profileCard"), data, {
      onReset: async () => {
        if (!confirm("Ștergi nivelul, profilul și tot progresul? Tutorele te va evalua de la zero. Nu se poate anula.")) return;
        await api("/api/profile", { method: "DELETE" });
        load();
      },
    });
  }

  function renderModules() {
    const box = $("#modules");
    box.innerHTML = "";
    const open = new Set(JSON.parse(store.get("pt-open-modules", "null") || "null") || []);
    data.modules.forEach((m, i) => {
      const done = m.topics.filter((t) => t.status === "învățat").length;
      const active = m.topics.some((t) => t.status !== "de învățat");
      const det = el("details", "module");
      det.open = open.size ? open.has(m.slug) : (i === 0 || active);
      det.addEventListener("toggle", () => {
        det.open ? open.add(m.slug) : open.delete(m.slug);
        store.set("pt-open-modules", JSON.stringify([...open]));
      });
      const sum = el("summary");
      sum.append(PTIcons.el("chevron-right", "m-caret"), PTIcons.module(m.slug), el("span", "m-title", m.title),
        el("span", "m-count" + (done === m.topics.length ? " complete" : ""), `${done}/${m.topics.length}`));
      det.append(sum);
      const list = el("ul", "topic-list");
      m.topics.forEach((t) => {
        const li = el("li");
        const a = el("a", "topic-row");
        a.href = "#" + t.slug;
        a.dataset.slug = t.slug;
        const dot = el("span", "dot " + statusOf(t.status).cls);
        if (statusOf(t.status).cls === "done") dot.append(PTIcons.el("check"));
        a.append(dot, el("span", "t-title", t.title));
        if (t.evidence) a.append(el("span", "t-ev", String(t.evidence)));
        a.title = statusOf(t.status).label + (t.evidence ? ` · ${t.evidence} lucrări` : "");
        li.append(a);
        list.append(li);
      });
      det.append(list);
      box.append(det);
    });
    highlight();
  }

  function highlight() {
    $$(".topic-row").forEach((a) => a.classList.toggle("active", a.dataset.slug === current));
  }

  // ------------------------------------------------------------------ Subiect
  let lessonAbort = null;

  // Lecțiile deschise măcar o dată: în editor, iconul „Citește lecția” nu mai clipește la ele (app.js).
  function markRead(slug) {
    const read = new Set(JSON.parse(store.get("pt-read-lessons", "[]")));
    if (read.has(slug)) return;
    read.add(slug);
    store.set("pt-read-lessons", JSON.stringify([...read]));
  }

  async function showTopic(slug) {
    current = slug;
    markRead(slug);
    highlight();
    $("#layout").dataset.view = "topic";
    $("#topicEmpty").hidden = true;
    $("#topic").hidden = false;
    if (lessonAbort) lessonAbort.abort();
    const t = await api(`/api/topics/${encodeURIComponent(slug)}`).catch((e) => { alert(e.message); return null; });
    if (!t || current !== slug) return;

    $("#topicModule").textContent = t.module;
    $("#topicTitle").textContent = t.title;
    const st = $("#topicStatus");
    st.className = "status-pill " + statusOf(t.status).cls;
    st.textContent = statusOf(t.status).label;
    if (statusOf(t.status).cls === "done") st.prepend(PTIcons.el("check"));
    $("#practiceBtn").href = "/?ask=" + encodeURIComponent(
      `Vreau să exersez subiectul „${t.title}”. Dă-mi un exercițiu potrivit nivelului meu.`
    );
    $("#workCount").textContent = t.evidence.length ? String(t.evidence.length) : "";
    renderWork(t);
    selectTab(t.evidence.length && location.hash.endsWith(":work") ? "work" : "lesson");
    document.querySelector(".topic-pane").scrollTop = 0;

    const panel = $("#lessonPanel");
    if (t.lesson) {
      PTMarkdown.render(panel, t.lesson, { lesson: true });
    } else {
      streamLesson(slug, panel);
    }
  }

  async function streamLesson(slug, panel) {
    panel.innerHTML = '<div class="lesson-loading"><span class="typing"><i></i><i></i><i></i></span> Tutorele scrie lecția (doar prima dată, durează puțin)…</div>';
    lessonAbort = new AbortController();
    let md = "";
    let raf = 0;
    try {
      const res = await fetch(`/api/topics/${encodeURIComponent(slug)}/lesson`, {
        method: "POST",
        headers: { "X-CSRFToken": csrf() },
        signal: lessonAbort.signal,
      });
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let i;
        while ((i = buf.indexOf("\n\n")) >= 0) {
          const line = buf.slice(0, i);
          buf = buf.slice(i + 2);
          if (!line.startsWith("data: ")) continue;
          const ev = JSON.parse(line.slice(6));
          if (ev.type === "text") {
            md += ev.text;
            if (!raf) raf = requestAnimationFrame(() => { raf = 0; if (current === slug) PTMarkdown.render(panel, md); });
          } else if (ev.type === "error") {
            panel.innerHTML = "";
            panel.append(el("div", "error-box", ev.message));
          }
        }
      }
      if (current === slug && md) PTMarkdown.render(panel, md, { lesson: true });
    } catch (e) {
      if (e.name !== "AbortError") { panel.innerHTML = ""; panel.append(el("div", "error-box", "Eroare: " + e.message)); }
    }
  }

  function renderWork(t) {
    const box = $("#workPanel");
    box.innerHTML = "";
    if (!t.evidence.length) {
      const empty = el("div", "work-empty");
      empty.append(
        el("p", "", "Încă n-ai lucrat la acest subiect cu tutorele."),
        el("p", "muted", "Când rezolvi un exercițiu și i-l dai la verificat, codul tău și părerea lui apar aici."),
      );
      box.append(empty);
      return;
    }
    t.evidence.forEach((e) => {
      const card = el("div", "work-card");
      const head = el("div", "work-head");
      const pill = el("span", "status-pill " + statusOf(e.status).cls, statusOf(e.status).label);
      if (statusOf(e.status).cls === "done") pill.prepend(PTIcons.el("check"));
      const when = new Date(e.created_at).toLocaleString("ro-RO", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
      const date = el("span", "work-date", when);
      date.prepend(PTIcons.el("calendar"));
      head.append(pill, date);
      if (e.path) {
        const file = el("span", "work-file", `${e.project} / ${e.path}`);
        file.prepend(PTIcons.el("file"));
        head.append(file);
      }
      const comment = el("div", "work-comment");
      const bot = el("span", "work-bot");
      bot.append(PTIcons.el("bot"));
      const text = el("div", "work-text");
      text.append(el("span", "work-who", "Tutorele"), document.createTextNode(" " + e.comment));
      comment.append(bot, text);
      card.append(head, comment);
      if (e.code) {
        const lang = /\.html?$/.test(e.path) ? "html" : /\.py$/.test(e.path) ? "python" : "";
        card.append(PTMarkdown.code(e.code, lang, { lineStart: e.start_line || 1 }));
      }
      box.append(card);
    });
  }

  function selectTab(name) {
    $$(".topic-tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
    $("#lessonPanel").hidden = name !== "lesson";
    $("#workPanel").hidden = name !== "work";
    $("#profilePanel").hidden = name !== "profile";
  }
  $$(".topic-tabs button").forEach((b) => b.addEventListener("click", () => selectTab(b.dataset.tab)));

  $("#topicBack").addEventListener("click", () => {
    history.pushState(null, "", location.pathname);
    $("#layout").dataset.view = "list";
    current = null;
    highlight();
  });

  function route() {
    const slug = location.hash.slice(1).split(":")[0];
    if (slug) showTopic(slug);
    else {
      $("#layout").dataset.view = "list";
      $("#topic").hidden = true;
      $("#topicEmpty").hidden = false;
    }
  }
  window.addEventListener("hashchange", route);

  async function load() {
    data = await api("/api/progress");
    renderProfile();
    renderModules();
    if (location.hash) route();
    else if (matchMedia("(min-width: 761px)").matches) {
      // Pe desktop deschidem direct lecția curentă (ultima deschisă de elev), altfel prima neînvățată.
      const all = data.modules.flatMap((m) => m.topics);
      const next = all.find((t) => t.slug === data.current) || all.find((t) => t.status === "de învățat") || all[0];
      if (next) history.replaceState(null, "", "#" + next.slug), route();
    }
  }

  load().catch((e) => alert("Nu pot încărca progresul: " + e.message));
})();
