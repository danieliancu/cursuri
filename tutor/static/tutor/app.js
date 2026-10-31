/* PyTutor — interfața: chat cu tutorele, explorer, editor, terminal. */
(() => {
  "use strict";

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));
  // Preferințele de UI sunt per utilizator (pe același dispozitiv pot lucra mai mulți elevi).
  const userKey = (k) => (k === "pt-theme" ? k : `${k}@${document.body.dataset.user || ""}`);
  const store = {
    get(k, d) { try { const v = localStorage.getItem(userKey(k)); return v === null ? d : v; } catch { return d; } },
    set(k, v) { try { localStorage.setItem(userKey(k), v); } catch { /* fără storage */ } },
  };

  const state = {
    project: null,
    tabs: [],            // {path, doc, dirty, binary, saveTimer}
    active: null,        // path
    expanded: new Set(JSON.parse(store.get("pt-expanded", "[]"))),
    termSince: 0,
    termPolling: false,
    termRunning: false,
    termHistory: [],
    termHistIdx: -1,
    chatBusy: false,
    ctx: { file: true, selection: "", terminal: "" },
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
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    });
    if (res.status === 401) toLogin();
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Eroare ${res.status}`);
    return data;
  }
  function toLogin() {
    location.href = "/login/?next=/";
    throw new Error("Sesiunea a expirat.");
  }
  const P = (suffix) => `/api/projects/${encodeURIComponent(state.project)}/${suffix}`;

  function toast(msg, ms = 2600) {
    const t = $("#toast");
    t.textContent = msg;
    t.hidden = false;
    clearTimeout(toast._t);
    toast._t = setTimeout(() => (t.hidden = true), ms);
  }

  // Tema: theme.js. Iconițele: icons.js.
  const icon = PTIcons.svg;

  // ------------------------------------------------------------------ Modal
  function modal({ title, body, actions }) {
    return new Promise((resolve) => {
      const m = $("#modal");
      $("#modalTitle").textContent = title;
      const bodyEl = $("#modalBody");
      bodyEl.innerHTML = "";
      if (typeof body === "string") bodyEl.innerHTML = body; else if (body) bodyEl.appendChild(body);
      const act = $("#modalActions");
      act.innerHTML = "";
      const close = (v) => { m.hidden = true; document.removeEventListener("keydown", onKey); resolve(v); };
      actions.forEach((a) => {
        const b = document.createElement("button");
        b.textContent = a.label;
        if (a.cls) b.className = a.cls;
        b.addEventListener("click", () => close(a.value()));
        act.appendChild(b);
      });
      const onKey = (e) => {
        if (e.key === "Escape") close(null);
        if (e.key === "Enter" && e.target.tagName === "INPUT") { e.preventDefault(); act.lastChild.click(); }
      };
      document.addEventListener("keydown", onKey);
      m.onclick = (e) => { if (e.target === m) close(null); };
      m.hidden = false;
      const inp = bodyEl.querySelector("input");
      (inp || act.lastChild).focus();
      if (inp) inp.select();
    });
  }
  function promptModal(title, value = "", placeholder = "") {
    const inp = document.createElement("input");
    inp.type = "text"; inp.value = value; inp.placeholder = placeholder;
    return modal({
      title, body: inp,
      actions: [
        { label: "Anulează", value: () => null },
        { label: "OK", cls: "primary-btn", value: () => inp.value.trim() || null },
      ],
    });
  }
  function confirmModal(title, text, okLabel = "Confirmă") {
    const p = document.createElement("p");
    p.textContent = text; p.style.margin = "0";
    return modal({
      title, body: p,
      actions: [
        { label: "Anulează", value: () => false },
        { label: okLabel, cls: "danger-btn", value: () => true },
      ],
    });
  }

  // ------------------------------------------------------------------ Layout: panouri, redimensionare, mobil
  const layout = $("#layout");
  const isMobile = () => matchMedia("(max-width: 760px)").matches;
  const isTablet = () => matchMedia("(max-width: 1100px)").matches;

  function showPane(name) {
    layout.dataset.pane = name;
    $$("#mobileNav button").forEach((b) => b.classList.toggle("active", b.dataset.pane === name));
    if (name === "code" && editor) setTimeout(() => editor.refresh(), 0);
    if (name === "code") scrollChat(true);
  }
  $$("#mobileNav button").forEach((b) => b.addEventListener("click", () => showPane(b.dataset.pane)));

  const root = document.documentElement;
  const savedChatW = store.get("pt-chat-w", "");
  if (savedChatW) root.style.setProperty("--chat-w", savedChatW);
  const savedTermH = store.get("pt-term-h", "");
  if (savedTermH) root.style.setProperty("--term-h", savedTermH);

  function drag(handle, onMove, onEnd) {
    handle.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      handle.classList.add("dragging");
      handle.setPointerCapture(e.pointerId);
      const move = (ev) => onMove(ev);
      const up = () => {
        handle.classList.remove("dragging");
        handle.removeEventListener("pointermove", move);
        handle.removeEventListener("pointerup", up);
        onEnd && onEnd();
        editor && editor.refresh();
      };
      handle.addEventListener("pointermove", move);
      handle.addEventListener("pointerup", up);
    });
  }
  drag($("#vResizer"), (e) => {
    const w = Math.min(Math.max(e.clientX, 280), window.innerWidth - 360);
    root.style.setProperty("--chat-w", w + "px");
  }, () => store.set("pt-chat-w", root.style.getPropertyValue("--chat-w")));
  drag($("#hResizer"), (e) => {
    const rect = $("#editorArea").getBoundingClientRect();
    const h = Math.min(Math.max(rect.bottom - e.clientY, 80), rect.height - 120);
    root.style.setProperty("--term-h", h + "px");
    $("#terminal").classList.remove("collapsed");
  }, () => store.set("pt-term-h", root.style.getPropertyValue("--term-h")));

  const workPane = $("#workPane");
  $("#explorerToggle").addEventListener("click", () => workPane.classList.toggle("explorer-open"));
  $("#explorerScrim").addEventListener("click", () => workPane.classList.remove("explorer-open"));

  // ------------------------------------------------------------------ Editor
  const editor = CodeMirror($("#editorHost"), {
    value: "",
    lineNumbers: true,
    gutters: ["pt-notes", "CodeMirror-linenumbers"],
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    autoCloseBrackets: true,
    matchBrackets: true,
    styleActiveLine: true,
    lineWrapping: false,
    extraKeys: {
      Tab: (cm) => cm.somethingSelected() ? cm.indentSelection("add") : cm.replaceSelection("    ", "end"),
      "Shift-Tab": (cm) => cm.indentSelection("subtract"),
      "Ctrl-S": () => saveActive(), "Cmd-S": () => saveActive(),
      "Ctrl-/": "toggleComment", "Cmd-/": "toggleComment",
      "Ctrl-Enter": () => runActive(), "Cmd-Enter": () => runActive(),
    },
  });
  editor.getWrapperElement().style.display = "none";

  function modeFor(path) {
    const ext = (path.split(".").pop() || "").toLowerCase();
    return {
      py: "python", html: "django", htm: "django", js: "javascript", json: { name: "javascript", json: true },
      css: "css", xml: "xml", sh: "shell", txt: null, md: null, cfg: null, toml: null, ini: null,
    }[ext] ?? null;
  }

  editor.on("cursorActivity", () => {
    const sel = editor.getSelection();
    $("#askSelectionBtn").classList.toggle("show", sel.trim().length > 0);
  });

  function activeTab() { return state.tabs.find((t) => t.path === state.active); }

  async function openFile(path, { focus = true } = {}) {
    let tab = state.tabs.find((t) => t.path === path);
    if (!tab) {
      const f = await api(P("file") + "?path=" + encodeURIComponent(path));
      tab = { path: f.path, binary: f.binary, dirty: false, doc: f.binary ? null : CodeMirror.Doc(f.content, modeFor(f.path)) };
      if (tab.doc) tab.doc.on("change", () => {
        markDirty(tab);
        if (/\.py$/i.test(tab.path)) nudge($("#runBtn"));  // cod modificat → pasul firesc e să-l rulezi
      });
      state.tabs.push(tab);
      anchorNotes(tab);
    }
    activate(tab.path);
    if (isTablet()) workPane.classList.remove("explorer-open");
    if (isMobile()) showPane("code");
    if (focus && !isMobile()) editor.focus();
  }

  function activate(path) {
    closeNote();
    state.active = path;
    const tab = activeTab();
    const host = $("#editorHost");
    host.querySelector(".binary-note")?.remove();
    const wrap = editor.getWrapperElement();
    if (!tab) {
      wrap.style.display = "none";
      $("#emptyEditor").hidden = false;
    } else if (tab.binary) {
      wrap.style.display = "none";
      $("#emptyEditor").hidden = true;
      const n = document.createElement("div");
      n.className = "binary-note";
      n.textContent = "Fișier binar — nu poate fi editat aici.";
      host.appendChild(n);
    } else {
      $("#emptyEditor").hidden = true;
      wrap.style.display = "";
      editor.swapDoc(tab.doc);
      editor.refresh();
    }
    renderNoteMarkers();
    $("#runBtn").disabled = !(tab && /\.py$/i.test(tab.path));
    store.set("pt-active-" + state.project, path || "");
    renderTabs();
    highlightTree();
    renderCtxChips();
  }

  function renderTabs() {
    const box = $("#tabs");
    box.innerHTML = "";
    state.tabs.forEach((t) => {
      const el = document.createElement("div");
      el.className = "tab" + (t.path === state.active ? " active" : "") + (t.dirty ? " dirty" : "");
      el.title = t.path;
      const name = document.createElement("span");
      // Mai multe tab-uri cu același nume (ex. main.py din capitole diferite): arătăm și folderul.
      const base = t.path.split("/").pop();
      const twin = state.tabs.some((o) => o !== t && o.path.split("/").pop() === base);
      name.textContent = twin && t.path.includes("/") ? t.path.split("/").slice(-2).join("/") : base;
      const close = document.createElement("button");
      close.className = "close";
      close.setAttribute("aria-label", "Închide");
      close.innerHTML = `<span>${icon("x")}</span>`;
      close.addEventListener("click", (e) => { e.stopPropagation(); closeTab(t.path); });
      el.insertAdjacentHTML("afterbegin", PTIcons.file(base));
      el.append(name, close);
      el.addEventListener("click", () => activate(t.path));
      el.addEventListener("auxclick", (e) => { if (e.button === 1) closeTab(t.path); });
      box.appendChild(el);
    });
    box.querySelector(".tab.active")?.scrollIntoView({ block: "nearest", inline: "nearest" });
    // Salvăm automat la scurt timp după fiecare modificare; indicatorul arată dacă mai e ceva de salvat.
    const saving = state.tabs.some((t) => t.dirty);
    const ss = $("#saveState");
    ss.hidden = !state.tabs.some((t) => t.doc);
    ss.classList.toggle("saving", saving);
    ss.innerHTML = saving ? icon("refresh-cw") + "Se salvează…" : icon("check") + "Salvat automat";
  }

  async function closeTab(path) {
    const tab = state.tabs.find((t) => t.path === path);
    if (tab && tab.dirty) await saveTab(tab);
    const i = state.tabs.findIndex((t) => t.path === path);
    state.tabs.splice(i, 1);
    if (state.active === path) {
      const next = state.tabs[i] || state.tabs[i - 1];
      activate(next ? next.path : null);
    } else renderTabs();
  }

  function markDirty(tab) {
    tab.dirty = true;
    renderTabs();
    clearTimeout(tab.saveTimer);
    tab.saveTimer = setTimeout(() => saveTab(tab), 900);
  }
  async function saveTab(tab) {
    clearTimeout(tab.saveTimer);
    if (!tab.doc || !tab.dirty) return;
    const content = tab.doc.getValue();
    try {
      await api(P("file"), { method: "PUT", body: { path: tab.path, content } });
      if (tab.doc.getValue() === content) tab.dirty = false;
      renderTabs();
    } catch (e) { toast("Nu am putut salva: " + e.message); }
  }
  const saveActive = () => { const t = activeTab(); if (t) saveTab(t); };
  async function saveAll() { await Promise.all(state.tabs.filter((t) => t.dirty).map(saveTab)); }

  async function reloadChangedFiles(paths) {
    for (const p of paths) {
      const tab = state.tabs.find((t) => t.path === p);
      if (tab && !tab.dirty && tab.doc) {
        const f = await api(P("file") + "?path=" + encodeURIComponent(p)).catch(() => null);
        if (f && !f.binary && f.content !== tab.doc.getValue()) {
          const cursor = tab.doc.getCursor();
          if (state.openNote?.path === p) closeNote();
          tab.doc.setValue(f.content);
          tab.doc.setCursor(cursor);
          tab.dirty = false;
          anchorNotes(tab);  // setValue șterge ancorele vechi
        }
      }
    }
    renderTabs();
    renderNoteMarkers();
  }

  // ------------------------------------------------------------------ Baloane de explicații ale tutorelui
  // Tutorele pune note numerotate pe linii; elevul le deschide pe rând, câte una (un tur ghidat).
  // Fiecare notă e ancorată cu bookmark-uri CodeMirror, ca să urmeze linia chiar dacă elevul editează mai sus.
  state.notes = {};        // path -> [{line, end_line, title, text}] (linii de la 1)
  state.openNote = null;   // {path, idx, widget, handles}

  function anchorNotes(tab) {
    if (!tab?.doc) return;
    (tab.noteAnchors || []).forEach((a) => { a.start.clear(); a.end.clear(); });
    const notes = state.notes[tab.path] || [];
    const last = tab.doc.lastLine();
    tab.noteAnchors = notes.map((n) => ({
      start: tab.doc.setBookmark({ line: Math.min(n.line - 1, last), ch: 0 }),
      end: tab.doc.setBookmark({ line: Math.min((n.end_line || n.line) - 1, last), ch: 0 }),
    }));
    tab.notesSeen = new Set();
  }

  function noteRange(tab, i) {
    const a = tab.noteAnchors?.[i];
    const n = state.notes[tab.path][i];
    const start = a?.start.find()?.line ?? n.line - 1;
    const end = Math.max(start, a?.end.find()?.line ?? (n.end_line || n.line) - 1);
    return { start, end };
  }

  function renderNoteMarkers() {
    editor.clearGutter("pt-notes");
    const tab = activeTab();
    const notes = tab?.doc ? state.notes[tab.path] || [] : [];
    notes.forEach((n, i) => {
      const b = document.createElement("button");
      b.className = "note-marker";
      if (tab.notesSeen?.has(i)) b.classList.add("seen");
      if (state.openNote?.path === tab.path && state.openNote.idx === i) b.classList.add("active");
      if (tab.pulseFirst && i === 0) b.classList.add("pulse");
      b.textContent = i + 1;
      b.title = n.title;
      b.setAttribute("aria-label", `Explicația ${i + 1}: ${n.title}`);
      b.addEventListener("mousedown", (e) => e.preventDefault());
      b.addEventListener("click", () => {
        const isOpen = state.openNote?.path === tab.path && state.openNote.idx === i;
        isOpen ? closeNote() : openNote(tab.path, i);
      });
      editor.setGutterMarker(noteRange(tab, i).start, "pt-notes", b);
    });
    updateNotesBar();
  }

  function updateNotesBar() {
    const tab = activeTab();
    const notes = tab?.doc ? state.notes[tab.path] || [] : [];
    const bar = $("#notesBar");
    bar.hidden = !notes.length;
    if (!notes.length) return;
    const seen = tab.notesSeen?.size || 0;
    $("#notesBarText").textContent =
      `Tutorele a pus ${notes.length === 1 ? "o explicație" : `${notes.length} explicații`} în cod` +
      (seen ? ` · ai văzut ${seen}/${notes.length}` : " · apasă pe numerele de pe margine, pe rând");
    $("#notesStartBtn").textContent = seen === 0 ? "Începe de la 1" : seen < notes.length ? "Continuă" : "Ia-o de la capăt";
  }

  function closeNote() {
    const o = state.openNote;
    if (!o) return;
    o.widget.clear();
    o.handles.forEach((h) => o.doc.removeLineClass(h, "background", "pt-note-line"));
    state.openNote = null;
    renderNoteMarkers();
  }

  async function openNote(path, idx) {
    if (state.active !== path) await openFile(path, { focus: false });
    const tab = activeTab();
    const notes = state.notes[path] || [];
    if (!tab?.doc || !notes[idx]) return;
    closeNote();
    tab.pulseFirst = false;
    const n = notes[idx];
    const { start, end } = noteRange(tab, idx);
    const handles = [];
    for (let l = start; l <= end; l++) handles.push(tab.doc.addLineClass(l, "background", "pt-note-line"));

    const el = document.createElement("div");
    el.className = "note-balloon";
    el.innerHTML = `
      <div class="note-head">
        <span class="note-badge">${idx + 1}/${notes.length}</span>
        <span class="note-title"></span>
        <button class="icon-btn sm note-close" aria-label="Închide">${icon("x")}</button>
      </div>
      <div class="note-body bubble"></div>
      <div class="note-foot">
        <button class="text-btn note-prev">‹ Anterior</button>
        <span class="lines"></span>
        <div class="spacer"></div>
        <button class="text-btn note-next"></button>
      </div>`;
    el.querySelector(".note-title").innerHTML = DOMPurify.sanitize(marked.parseInline(n.title));
    renderMarkdown(el.querySelector(".note-body"), n.text);
    el.querySelector(".lines").textContent = start === end ? `linia ${start + 1}` : `liniile ${start + 1}–${end + 1}`;
    const prev = el.querySelector(".note-prev");
    const next = el.querySelector(".note-next");
    prev.disabled = idx === 0;
    next.textContent = idx < notes.length - 1 ? "Următorul ›" : "Am terminat ✓";
    prev.addEventListener("click", () => openNote(path, idx - 1));
    next.addEventListener("click", () => (idx < notes.length - 1 ? openNote(path, idx + 1) : closeNote()));
    el.querySelector(".note-close").addEventListener("click", closeNote);
    // Clicurile în balon nu trebuie să mute cursorul din editor.
    el.addEventListener("mousedown", (e) => { if (!e.target.closest("button, a")) e.stopPropagation(); });

    const widget = editor.addLineWidget(end, el, { coverGutter: false, noHScroll: true });
    state.openNote = { path, idx, widget, handles, doc: tab.doc };
    tab.notesSeen.add(idx);
    renderNoteMarkers();
    editor.scrollIntoView({ line: start, ch: 0 }, 60);
    requestAnimationFrame(() => el.scrollIntoView({ block: "nearest", behavior: "smooth" }));
  }

  async function showNotes(path, { open = true } = {}) {
    if (isMobile()) showPane("code");
    await openFile(path, { focus: false });
    const tab = activeTab();
    if (open && tab?.notesSeen) {
      const n = state.notes[path]?.length || 0;
      const firstUnseen = [...Array(n).keys()].find((i) => !tab.notesSeen.has(i));
      openNote(path, firstUnseen ?? 0);
    }
  }

  // Plasa de siguranță din balonul exercițiului fix: elevul lucra la altceva în fișierul capitolului.
  // Fișierul nu mai e verificat cu testele lecției, iar tutorele (modelul mic) îl verifică după sarcina elevului.
  document.addEventListener("click", async (e) => {
    const link = e.target.closest('a[href="#nu-e-exercitiul"]');
    if (!link) return;
    e.preventDefault();
    const path = state.openNote?.path || state.active;
    if (!path || state.chatBusy) return;
    try {
      await api(P("exercitiu/sari"), { method: "POST", body: { path } });
    } catch (err) { return toast(err.message); }
    await receiveNotes(path, []);
    toast("Bine: fișierul nu mai e verificat cu testele lecției. „Exercițiu nou” îți dă înapoi exercițiul lecției.", 5000);
    sendMessage("Nu lucrez la exercițiul lecției, ci la altceva. Verifică programul meu după ce am vrut să fac.", { mode: "check" });
  });

  // Tutorele a pus (sau a șters) baloane: le arătăm fără să deschidem vreunul.
  async function receiveNotes(path, notes) {
    if (state.openNote?.path === path) closeNote();
    if (notes.length) state.notes[path] = notes; else delete state.notes[path];
    const tab = state.tabs.find((t) => t.path === path);
    if (tab) anchorNotes(tab);
    if (notes.length && !isMobile()) {
      await openFile(path, { focus: false }).catch(() => {});
      const t = activeTab();
      if (t) t.pulseFirst = true;
    }
    renderNoteMarkers();
  }

  async function loadNotes() {
    state.notes = (await api(P("notes"))).notes || {};
    state.tabs.forEach(anchorNotes);
    renderNoteMarkers();
  }

  $("#notesStartBtn").addEventListener("click", () => { if (state.active) showNotes(state.active); });
  $("#notesClearBtn").addEventListener("click", async () => {
    const path = state.active;
    if (!path) return;
    await api(P("notes") + "?path=" + encodeURIComponent(path), { method: "DELETE" }).catch(() => {});
    receiveNotes(path, []);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || !state.openNote || document.querySelector(".modal:not([hidden])")) return;
    closeNote();
  });

  // ------------------------------------------------------------------ Explorer
  let treeData = [];
  async function loadTree() {
    const d = await api(P("tree"));
    treeData = d.tree;
    renderTree();
  }


  function renderTree() {
    const box = $("#tree");
    box.innerHTML = "";
    const walk = (nodes, depth, parent) => {
      nodes.forEach((n) => {
        const row = document.createElement("div");
        const isDir = n.type === "dir";
        const open = isDir && state.expanded.has(n.path);
        row.className = "node" + (open ? " open" : "");
        row.dataset.path = n.path;
        row.dataset.type = n.type;
        row.setAttribute("role", "treeitem");
        row.style.paddingLeft = 8 + depth * 14 + "px";
        row.innerHTML = (isDir ? icon("chevron-right", "caret") : '<span class="caret-space"></span>') + PTIcons.file(n.name, { dir: isDir, open });
        const name = document.createElement("span");
        name.className = "name";
        name.textContent = n.name;
        const more = document.createElement("button");
        more.className = "more";
        more.textContent = "⋯";
        more.setAttribute("aria-label", "Acțiuni");
        more.addEventListener("click", (e) => { e.stopPropagation(); openMenu(e, n); });
        row.append(name, more);
        row.addEventListener("click", () => {
          if (isDir) {
            state.expanded.has(n.path) ? state.expanded.delete(n.path) : state.expanded.add(n.path);
            store.set("pt-expanded", JSON.stringify([...state.expanded]));
            renderTree();
          } else openFile(n.path).catch((e) => toast(e.message));
        });
        row.addEventListener("contextmenu", (e) => { e.preventDefault(); openMenu(e, n); });
        parent.appendChild(row);
        if (open) walk(n.children, depth + 1, parent);
      });
    };
    walk(treeData, 0, box);
    if (!treeData.length) box.innerHTML = '<p class="muted" style="padding:8px 12px;margin:0">Proiect gol.</p>';
    highlightTree();
  }
  function highlightTree() {
    $$("#tree .node").forEach((r) => r.classList.toggle("active", r.dataset.path === state.active));
  }

  function openMenu(e, node) {
    const m = $("#ctxMenu");
    m.innerHTML = "";
    const dir = node.type === "dir" ? node.path : node.path.split("/").slice(0, -1).join("/");
    const items = [
      ["Fișier nou aici", () => newEntry("file", dir)],
      ["Folder nou aici", () => newEntry("dir", dir)],
      ["Redenumește / mută", () => renameEntry(node)],
      ["Șterge", () => deleteEntry(node), "danger"],
    ];
    if (node.type === "file" && /\.py$/.test(node.path)) items.unshift(["Rulează", () => runCommand(`python ${quote(node.path)}`)]);
    items.forEach(([label, fn, cls]) => {
      const b = document.createElement("button");
      b.textContent = label;
      if (cls) b.className = cls;
      b.addEventListener("click", () => { m.hidden = true; fn(); });
      m.appendChild(b);
    });
    m.hidden = false;
    const r = m.getBoundingClientRect();
    m.style.left = Math.min(e.clientX, innerWidth - r.width - 8) + "px";
    m.style.top = Math.min(e.clientY, innerHeight - r.height - 8) + "px";
  }
  document.addEventListener("pointerdown", (e) => { if (!e.target.closest("#ctxMenu")) $("#ctxMenu").hidden = true; });

  async function newEntry(type, dir = "") {
    const label = type === "dir" ? "Folder nou" : "Fișier nou";
    const ph = type === "dir" ? "ex: blog/templates" : "ex: utils.py sau app/models.py";
    const name = await promptModal(label + (dir ? ` în ${dir}/` : ""), "", ph);
    if (!name) return;
    const path = (dir ? dir + "/" : "") + name;
    try {
      const r = await api(P("file"), { method: "POST", body: { path, type } });
      path.split("/").slice(0, -1).reduce((acc, part) => { const p = acc ? acc + "/" + part : part; state.expanded.add(p); return p; }, "");
      if (type === "dir") state.expanded.add(r.path);
      await loadTree();
      if (type === "file") openFile(r.path);
    } catch (e) { toast(e.message); }
  }
  async function renameEntry(node) {
    const to = await promptModal("Redenumește / mută", node.path);
    if (!to || to === node.path) return;
    try {
      await saveAll();
      const r = await api(P("rename"), { method: "POST", body: { from: node.path, to } });
      state.tabs.forEach((t) => {
        if (t.path === node.path) t.path = r.path;
        else if (t.path.startsWith(node.path + "/")) t.path = r.path + t.path.slice(node.path.length);
      });
      if (state.active === node.path) state.active = r.path;
      await loadTree();
      renderTabs();
    } catch (e) { toast(e.message); }
  }
  async function deleteEntry(node) {
    const ok = await confirmModal("Șterge", `Sigur ștergi „${node.path}”${node.type === "dir" ? " și tot conținutul lui" : ""}? Nu se poate anula.`, "Șterge");
    if (!ok) return;
    try {
      await api(P("file") + "?path=" + encodeURIComponent(node.path), { method: "DELETE" });
      const gone = state.tabs.filter((t) => t.path === node.path || t.path.startsWith(node.path + "/"));
      gone.forEach((t) => { t.dirty = false; });
      for (const t of gone) await closeTab(t.path);
      await loadTree();
    } catch (e) { toast(e.message); }
  }

  $("#newFileBtn").addEventListener("click", () => newEntry("file"));
  $("#newFolderBtn").addEventListener("click", () => newEntry("dir"));
  $("#refreshTreeBtn").addEventListener("click", () => loadTree().catch((e) => toast(e.message)));

  // ------------------------------------------------------------------ Terminal
  const termOut = $("#termOut");
  const termInput = $("#termInput");
  const stripAnsi = (s) => s.replace(/\x1b\[[0-9;?]*[ -/]*[@-~]/g, "");
  const quote = (p) => (/\s/.test(p) ? `"${p}"` : p);

  function setTermRunning(running, command, code) {
    state.termRunning = running;
    $("#termStopBtn").hidden = !running;
    const st = $("#termStatus");
    st.classList.toggle("running", running);
    st.textContent = running ? `● ${command}` : (command ? `ultima: ${command} (cod ${code ?? "-"})` : "");
    const pr = $("#termPrompt");
    pr.textContent = running ? ">" : "$";
    pr.classList.toggle("stdin", running);
    termInput.placeholder = running ? "input pentru program (Enter trimite)" : "python main.py";
  }

  async function pollTerm() {
    if (state.termPolling || !state.project) return;
    state.termPolling = true;
    const project = state.project;
    try {
      while (project === state.project) {
        const d = await api(P("term/output") + "?since=" + state.termSince);
        if (d.reset) termOut.textContent = "";
        if (d.text) {
          const atBottom = termOut.scrollHeight - termOut.scrollTop - termOut.clientHeight < 40;
          termOut.textContent += stripAnsi(d.text);
          if (atBottom) termOut.scrollTop = termOut.scrollHeight;
        }
        state.termSince = d.next;
        setTermRunning(d.running, d.command, d.returncode);
        if (!d.running) {
          // o comandă (startproject, startapp, makemigrations...) poate crea fișiere: le arătăm în Explorer
          if (state.treeStale) { state.treeStale = false; loadTree().catch(() => {}); }
          if (state.runStart != null) {
            await errorNote(d);
            if (state.checkAfterRun) checkAfterRun(d);
            else if (!d.eroare) suggestAfterRun(d.returncode, termOut.textContent.slice(state.runStart));
          }
          state.runStart = null;
          state.checkAfterRun = false;
          break;
        }
        await new Promise((r) => setTimeout(r, 350));
      }
    } catch { /* ignorăm erorile de rețea temporare */ }
    state.termPolling = false;
  }

  // `check`: la final, tutorele primește rezultatul și îl comentează („Rulează și verifică”).
  async function runCommand(cmd, { check = false } = {}) {
    await saveAll();
    $("#terminal").classList.remove("collapsed");
    if (isMobile()) showPane("terminal");
    clearNudge();
    // doar rularea unui fișier .py duce la verificare / „Verifică-mi codul” (nu pip, runserver etc.)
    state.runStart = /^python3?\s.*\.py\b/.test(cmd.trim()) ? termOut.textContent.length : null;
    state.checkAfterRun = check && state.runStart != null;
    try {
      await api(P("term/run"), { method: "POST", body: { command: cmd } });
      termOut.scrollTop = termOut.scrollHeight;
      state.treeStale = true;
      // comenzile care rămân pornite (runserver creează db.sqlite3) nu se termină: reîncărcăm și puțin după start
      const project = state.project;
      setTimeout(() => { if (project === state.project) loadTree().catch(() => {}); }, 2500);
      pollTerm();
    } catch (e) { toast(e.message); }
  }
  function runActive() {
    const t = activeTab();
    if (!t || !/\.py$/i.test(t.path)) return;
    state.runPath = t.path;
    runCommand(`python ${quote(t.path)}`, { check: true });
  }
  // După „Rulează și verifică”, în ordinea costului:
  // 1. fișierul capitolului are exercițiu fix → verdictul îl dă codul (testele lecției), AI-ul mic doar îl formulează;
  // 2. programul a crăpat cu o eroare cunoscută → balonul de pe rândul ei o explică, fără AI;
  // 3. altfel tutorele (modelul mic, cu context redus) se uită la rezultat. Vede ultima rulare în context,
  //    deci ajunge un mesaj scurt; elevul nu trebuie să copieze nimic.
  async function checkAfterRun(d) {
    if (state.chatBusy) return nudge(step("check"));  // tutorele încă răspunde: lăsăm butonul la îndemână
    if (state.runPath?.startsWith("capitole/") && await checkExercise(state.runPath)) return;
    if (d.eroare) return;  // explicația e deja în balonul de pe rând
    sendMessage("Am rulat codul. Uită-te la rezultat și spune-mi dacă e bine și ce urmează.", { mode: "check" });
  }
  $("#runBtn").addEventListener("click", runActive);

  // ------------------------------------------------------------------ Erori explicate (fără AI), în balon
  // Eroarea cunoscută (tutor/erori.py) devine un balon pe rândul ei, în fișierul din traceback. Balonul nu se
  // salvează pe server: la următoarea rulare fără eroare dispare, iar un balon al tutorelui îl înlocuiește.
  async function errorNote(d) {
    const e = d.eroare;
    const own = state.errorNote;  // balonul de eroare pus la rularea anterioară
    if (!e) {
      if (own && state.notes[own]?.some((n) => n.local)) await receiveNotes(own, []);
      state.errorNote = null;
      return;
    }
    // fișierul din traceback, relativ la proiect (în container: /work/<proiect>/..., local: .../<proiect>/...)
    const fromTrace = e.fisier ? e.fisier.replace(/\\/g, "/").split(`/${state.project}/`).pop() : null;
    const ran = (d.command.match(/^\s*python3?\s+"?([^"\s]+\.py)/) || [])[1];
    const path = fromTrace && treeHas(fromTrace) ? fromTrace : ran;
    if (!path) return;
    if (own && own !== path && state.notes[own]?.some((n) => n.local)) await receiveNotes(own, []);
    const parts = [e.explicatie];
    if (e.lectie) {
      const where = e.lectie.sectiune ? ` — „${e.lectie.sectiune}”` : ` (${e.lectie.titlu})`;
      parts.push(`[Recitește: lecția ${e.lectie.numar}${where}](/progres/#${e.lectie.slug})`);
    }
    parts.push("[Tot nu e clar? Întreabă AI](#intreaba-ai)");
    state.errorNote = path;
    await receiveNotes(path, [{ line: e.rand || 1, end_line: e.rand || 1, title: e.titlu, text: parts.join("\n\n"), local: true }]);
  }
  const treeHas = (path) => {
    const walk = (nodes) => nodes.some((n) => n.path === path || (n.children && walk(n.children)));
    return walk(treeData);
  };
  document.addEventListener("click", (e) => {
    if (!e.target.closest('a[href="#intreaba-ai"]')) return;
    e.preventDefault();
    step("error").click();  // „Explică eroarea”, cu output-ul din terminal atașat
  });

  // ------------------------------------------------------------------ Exercițiul fix al lecției
  // Fișierul capitolului e verificat de cod cât timp exercițiul fix e de rezolvat (decide serverul);
  // altfel îl verifică modelul mic.
  // Întoarce false dacă fișierul n-are exercițiu fix (atunci verifică tutorele AI).
  async function checkExercise(path) {
    setBusy(true);
    let r;
    try {
      r = await api(P("exercitiu/verifica"), { method: "POST", body: { path } });
    } catch (e) {
      setBusy(false);
      toast(e.message);
      return true;
    }
    setBusy(false);
    if (!r.exercitiu) return false;
    state.errorNote = null;  // balonul verificării îl înlocuiește pe cel de eroare (e salvat pe server)
    openComposer();
    addMsg("user", "Am rulat programul. Verifică exercițiul.");
    // detaliile (testul, ce trebuia, output-ul, indiciul) sunt în balonul de pe rând; aici doar fraza tutorelui
    addMsg("assistant", r.mesaj);
    scrollChat(true);
    let learned = false;
    for (const ev of r.events || []) {
      if (ev.type === "annotations") await receiveNotes(ev.path, ev.notes);
      else if (ev.type === "progress") {
        learned ||= ev.status === "învățat";
        toast(`Progres salvat: ${ev.topic} · ${ev.status}`);
        loadCourse().catch(() => {});
      }
    }
    if (r.verdict.rezultat === "corect") nudge(step("next"));
    else nudge($("#runBtn"));
    return true;
  }


  termInput.addEventListener("keydown", async (e) => {
    if (e.key === "ArrowUp" && !state.termRunning && state.termHistory.length) {
      e.preventDefault();
      state.termHistIdx = Math.max(0, (state.termHistIdx < 0 ? state.termHistory.length : state.termHistIdx) - 1);
      termInput.value = state.termHistory[state.termHistIdx];
    } else if (e.key === "ArrowDown" && !state.termRunning && state.termHistIdx >= 0) {
      e.preventDefault();
      state.termHistIdx = Math.min(state.termHistory.length, state.termHistIdx + 1);
      termInput.value = state.termHistory[state.termHistIdx] || "";
    } else if (e.key === "Enter") {
      e.preventDefault();
      const v = termInput.value;
      termInput.value = "";
      if (state.termRunning) {
        try { await api(P("term/input"), { method: "POST", body: { text: v } }); pollTerm(); } catch (err) { toast(err.message); }
      } else if (v.trim()) {
        if (v.trim() === "clear" || v.trim() === "cls") { $("#termClearBtn").click(); return; }
        state.termHistory.push(v);
        state.termHistIdx = -1;
        runCommand(v);
      }
    } else if (e.key === "c" && e.ctrlKey && state.termRunning) {
      e.preventDefault();
      $("#termStopBtn").click();
    }
  });
  termOut.addEventListener("click", () => { if (!getSelection().toString()) termInput.focus(); });
  $("#termStopBtn").addEventListener("click", async () => { await api(P("term/stop"), { method: "POST" }).catch(() => {}); pollTerm(); });
  $("#termClearBtn").addEventListener("click", async () => {
    await api(P("term/clear"), { method: "POST" }).catch(() => {});
    termOut.textContent = "";
  });
  $("#termCollapseBtn").addEventListener("click", () => { $("#terminal").classList.toggle("collapsed"); editor.refresh(); });
  $("#termAskBtn").addEventListener("click", () => {
    state.ctx.terminal = termOut.textContent.slice(-6000);
    renderCtxChips();
    openComposer();
    const inp = $("#chatInput");
    if (!inp.value) inp.value = "Ce înseamnă output-ul ăsta din terminal?";
    inp.focus();
    autoGrow();
  });

  // ------------------------------------------------------------------ Chat
  const messagesEl = $("#messages");
  const chatInput = $("#chatInput");

  const renderMarkdown = (el, md) => PTMarkdown.render(el, md);

  // Panoul tutorelui: coloană fixă în dreapta zonei de lucru, pe toată înălțimea; conversația se derulează în el.
  const tfloat = $("#tutorFloat");
  const tpill = $("#tutorPill");
  let floatOpen = store.get("pt-float-open", "1") === "1";
  function setFloatOpen(open) {
    floatOpen = open;
    tfloat.hidden = !open;
    tpill.classList.toggle("active", open);
    tpill.setAttribute("aria-pressed", String(open));
    workPane.classList.toggle("tutor-hidden", !open);
    store.set("pt-float-open", open ? "1" : "0");
    editor.refresh();
    if (open) scrollChat(true);
  }
  // Câmpul de scris e în panoul tutorelui: îl arătăm (și pe telefon trecem pe tab-ul „Cod”).
  function openComposer() {
    if (isMobile()) showPane("code");
    if (!floatOpen) setFloatOpen(true);
  }
  $("#tfMinBtn").addEventListener("click", () => setFloatOpen(false));
  // „Ultima sarcină”: derulează la ultimul titlu de sarcină/exercițiu din răspunsurile tutorelui.
  $("#lastTaskBtn").addEventListener("click", () => {
    const isTask = (el) => el.textContent.trim().length < 80 && /sarcin|exerci[țţt]i/i.test(el.textContent);
    const bubbles = $$("#messages .msg.assistant .bubble");
    for (let i = bubbles.length - 1; i >= 0; i--) {
      const marks = [...bubbles[i].querySelectorAll("h1, h2, h3, h4, p > strong:first-child")].filter(isTask);
      const target = marks.pop();
      if (target) {
        const block = target.tagName === "STRONG" ? target.parentElement : target;
        block.scrollIntoView({ block: "start", behavior: "smooth" });
        block.classList.remove("task-flash");
        void block.offsetWidth;  // repornește animația la clicuri repetate
        block.classList.add("task-flash");
        return;
      }
    }
    toast("Tutorele nu ți-a dat încă nicio sarcină în conversația asta.");
  });
  // Butonul „Tutor” din bara de sus arată / ascunde panoul.
  tpill.addEventListener("click", () => {
    if (isMobile()) return openComposer();  // pe telefon tutorele stă peste cod: trecem pe tab-ul „Cod”
    setFloatOpen(!floatOpen);
    if (floatOpen) chatInput.focus();
  });

  function scrollChat(force) {
    const near = messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 120;
    if (messagesEl.querySelector(".welcome")) messagesEl.scrollTop = 0;
    else if (force || near) messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addMsg(role, text, tools = []) {
    messagesEl.querySelector(".welcome")?.remove();
    const m = document.createElement("div");
    m.className = "msg " + role;
    const toolsBox = document.createElement("div");
    toolsBox.className = "tools";
    tools.forEach((t) => addToolLine(toolsBox, t));
    const b = document.createElement("div");
    b.className = "bubble";
    if (role === "user") b.textContent = text; else renderMarkdown(b, text);
    m.append(toolsBox, b);
    messagesEl.appendChild(m);
    return { el: m, bubble: b, tools: toolsBox };
  }
  function addToolLine(box, entry) {
    const { label, notes_path: notesPath } = typeof entry === "string" ? { label: entry } : entry;
    const d = document.createElement("div");
    d.className = "tool-line";
    if (notesPath) {
      const b = document.createElement("button");
      b.className = "tool-link";
      b.textContent = `${label} — vezi bulele din cod`;
      b.addEventListener("click", () => {
        if (state.notes[notesPath]?.length) showNotes(notesPath).catch((e) => toast(e.message));
        else toast("Problemele marcate aici au fost rezolvate sau înlocuite.");
      });
      d.appendChild(b);
    } else {
      d.textContent = label;
    }
    box.appendChild(d);
  }

  function renderWelcome() {
    messagesEl.innerHTML = `
      <div class="welcome">
        <h2>Salut! Sunt tutorele tău de Python.</h2>
        <p>Te învăț Python și Django scriind aplicații reale. Încep prin a afla ce știi deja, apoi construim pas cu pas.</p>
        <button class="primary-btn" id="startBtn">Începe</button>
      </div>`;
    $("#startBtn").addEventListener("click", () => sendMessage("Salut! Sunt gata să învăț. De unde începem?"));
  }

  async function loadChat() {
    const d = await api(P("chat"));
    messagesEl.innerHTML = "";
    if (!d.messages.length) renderWelcome();
    d.messages.forEach((m) => addMsg(m.role, m.text, m.tools || []));
    scrollChat(true);
  }

  function renderCtxChips() {
    const box = $("#ctxChips");
    box.innerHTML = "";
    const chip = (label, onRemove, off) => {
      const c = document.createElement("span");
      c.className = "chip" + (off ? " off" : "");
      const s = document.createElement("span");
      s.textContent = label;
      const x = document.createElement("button");
      x.textContent = off ? "+" : "×";
      x.setAttribute("aria-label", off ? "Atașează" : "Elimină");
      x.addEventListener("click", onRemove);
      c.append(s, x);
      box.appendChild(c);
    };
    if (state.active) chip(state.active, () => { state.ctx.file = !state.ctx.file; renderCtxChips(); }, !state.ctx.file);
    if (state.ctx.selection) chip(`selecție (${state.ctx.selection.split("\n").length} rânduri)`, () => { state.ctx.selection = ""; renderCtxChips(); });
    if (state.ctx.terminal) chip("output terminal", () => { state.ctx.terminal = ""; renderCtxChips(); });
  }

  function autoGrow() {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 180) + "px";
  }
  chatInput.addEventListener("input", autoGrow);
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing && !isMobile()) {
      e.preventDefault();
      sendMessage();
    }
  });
  $("#sendBtn").addEventListener("click", () => sendMessage());
  // Săgeți pe rândul de butoane rapide când nu încap: arată în ce parte mai sunt butoane.
  const quick = $("#quick");
  function updateQuickArrows() {
    const max = quick.scrollWidth - quick.clientWidth;
    $("#quickLeft").hidden = quick.scrollLeft <= 2;
    $("#quickRight").hidden = quick.scrollLeft >= max - 2;
  }
  quick.addEventListener("scroll", updateQuickArrows, { passive: true });
  new ResizeObserver(updateQuickArrows).observe(quick);
  $("#quickLeft").addEventListener("click", () => quick.scrollBy({ left: -quick.clientWidth * 0.7, behavior: "smooth" }));
  $("#quickRight").addEventListener("click", () => quick.scrollBy({ left: quick.clientWidth * 0.7, behavior: "smooth" }));
  $$("#quick button").forEach((b) => b.addEventListener("click", async () => {
    if (b.dataset.step === "check") {  // verificare de rutină: exercițiul fix sau modelul mic, ca după rulare
      if (state.chatBusy) return;
      await saveAll();
      if (state.active?.startsWith("capitole/") && await checkExercise(state.active)) return;
      return sendMessage(b.dataset.quick, { mode: "check" });
    }
    if (b.dataset.step === "next" || b.dataset.step === "exercise") {
      if (state.chatBusy) return;
      if (await localStep(b.dataset.step === "next" ? "urmator" : "exercitiu", b.dataset.quick)) return;
    }
    if (b.dataset.attachTerminal && termOut.textContent.trim()) state.ctx.terminal = termOut.textContent.slice(-6000);
    sendMessage(b.dataset.quick);
  }));

  // „Următorul pas” și „Exercițiu nou” fără AI, când răspunsul se știe din curriculum și din exercițiile fixe
  // (serverul răspunde `ai: true` când nu se poate, iar atunci întreabă tutorele, ca înainte).
  async function localStep(tip, text) {
    let r;
    try {
      r = await api(P("pas"), { method: "POST", body: { tip, text, path: state.active } });
    } catch { return false; }
    if (r.ai) return false;
    clearNudge();
    openComposer();
    addMsg("user", text);
    addMsg("assistant", r.mesaj);
    scrollChat(true);
    if (r.path) await openChapter(r.path, r.topic);
    loadCourse().catch(() => {});
    if (r.path?.endsWith(".py")) nudge($("#runBtn"));
    return true;
  }

  // ------------------------------------------------------------------ Pasul următor
  // Un singur element luminează discret ca să-i arate elevului ce urmează: cod modificat → „Rulează”,
  // după rulare → „Verifică-mi codul” (sau „Explică eroarea”), sarcină nouă → „Rulează”, întrebarea
  // „trecem mai departe?” sau un subiect învățat → „Următorul pas”, altă întrebare → câmpul de scris.
  // Dispare la click pe el, la orice mesaj trimis sau când apare alt pas.
  let nudged = null;
  const step = (name) => $(`#quick [data-step="${name}"]`);
  function clearNudge() {
    $$(".nudge").forEach((el) => el.classList.remove("nudge"));
    nudged = null;
  }
  function nudge(el) {
    if (!el || el === nudged) return;
    clearNudge();
    nudged = el;
    el.classList.add("nudge");
    if (quick.contains(el)) {
      if (!floatOpen) tpill.classList.add("nudge");  // panoul e ascuns: luminează butonul care îl deschide
      const q = quick.getBoundingClientRect(), r = el.getBoundingClientRect();
      if (r.left < q.left || r.right > q.right) quick.scrollBy({ left: r.left - q.left - 24, behavior: "smooth" });
    }
  }
  document.addEventListener("click", (e) => {
    if (tpill.contains(e.target)) tpill.classList.remove("nudge");
    else if (nudged && nudged.contains(e.target)) clearNudge();
  }, true);

  function suggestAfterRun(code, output) {
    if (code === 0 && !/Traceback|Error:/.test(output)) nudge(step("check"));
    else if (/Traceback|Error:/.test(output)) nudge(step("error"));
    else clearNudge();  // oprit de elev (Oprește / Ctrl+C) sau alt cod de ieșire: nu sugerăm nimic
  }

  // „Vrei să trecem mai departe la …?”, „Continuăm cu următorul subiect?”
  // (fără \b după diacritice: în JS, \b cunoaște doar literele ASCII)
  const MOVE_ON = /\b(trecem|treci|treceți|mergem|continuăm|continui|avansăm)\b|mai departe|următo(rul|area|r)\s+(pas|subiect|capitol|lecți|tem|exerci)/i;
  function suggestAfterReply({ text, failed, learned, task, notes }) {
    if (failed) return clearNudge();
    const tail = text.trim().slice(-500);
    const questions = tail.match(/[^.!?\n]*\?/g) || [];
    const lastQ = questions.length ? questions[questions.length - 1] : "";
    // întrebarea contează doar dacă e spre final (nu una retorică din mijlocul explicației)
    const asks = lastQ && tail.length - (tail.lastIndexOf(lastQ) + lastQ.length) < 150;
    const runnable = /\.py$/i.test(state.active || "");
    if (learned || (asks && MOVE_ON.test(lastQ))) nudge(step("next"));
    else if (notes) clearNudge();  // are de citit baloanele și de corectat; editarea codului aprinde „Rulează”
    else if (runnable && (task || /\brul(ează|eaza|ezi|ați|ati)/i.test(tail))) nudge($("#runBtn"));
    else if (asks) nudge($(".input-row"));
    else clearNudge();
  }
  $("#askSelectionBtn").addEventListener("click", () => {
    state.ctx.selection = editor.getSelection();
    renderCtxChips();
    openComposer();
    if (!chatInput.value) chatInput.value = "Explică-mi codul ăsta.";
    chatInput.focus();
    autoGrow();
  });

  function setBusy(busy) {
    state.chatBusy = busy;
    $("#sendBtn").disabled = busy;
    $$("#aiStatus, #tutorPill .status-dot").forEach((d) => d.classList.toggle("busy", busy));
  }

  // `mode: "check"`: verificarea de rutină după rulare (modelul mic, context redus).
  async function sendMessage(text, { mode = "chat" } = {}) {
    text = (text ?? chatInput.value).trim();
    if (!text || state.chatBusy) return;
    await saveAll();
    clearNudge();
    chatInput.value = "";
    autoGrow();
    const context = {
      open_file: state.ctx.file ? state.active : null,
      selection: state.ctx.selection || null,
      terminal: state.ctx.terminal || null,
    };
    state.ctx.selection = "";
    state.ctx.terminal = "";
    renderCtxChips();

    addMsg("user", text);
    const a = addMsg("assistant", "");
    openComposer();
    const typing = document.createElement("div");
    typing.innerHTML = '<span class="typing"><i></i><i></i><i></i></span><span class="typing-label"></span>';
    a.el.appendChild(typing);
    scrollChat(true);
    setBusy(true);

    let md = "";
    let raf = 0;
    const flush = () => { raf = 0; renderMarkdown(a.bubble, md); scrollChat(); };
    const changed = new Set();
    const pendingNotes = [];  // aplicate la final, după ce fișierele modificate s-au reîncărcat
    let chapter = null;       // capitolul nou început: îi deschidem fișierul la final
    let failed = false;       // pentru pasul următor sugerat la final
    let learned = false;

    try {
      const res = await fetch(P("chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
        body: JSON.stringify({ message: text, context, mode }),
      });
      if (res.status === 401) toLogin();
      if (!res.ok || !res.body) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.error || `Eroare ${res.status}`);
      }
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let idx;
        while ((idx = buf.indexOf("\n\n")) >= 0) {
          const line = buf.slice(0, idx);
          buf = buf.slice(idx + 2);
          if (!line.startsWith("data: ")) continue;
          const ev = JSON.parse(line.slice(6));
          switch (ev.type) {
            case "text":
              typing.hidden = true;
              md += ev.text;
              if (!raf) raf = requestAnimationFrame(flush);
              break;
            case "thinking":
              typing.hidden = false;
              typing.querySelector(".typing-label").textContent = "se gândește…";
              break;
            case "tool_start":
              typing.hidden = false;
              typing.querySelector(".typing-label").textContent = "lucrează…";
              break;
            case "tool":
              addToolLine(a.tools, ev);
              scrollChat();
              break;
            case "round":
              if (md && !md.endsWith("\n\n")) md += "\n\n";
              typing.hidden = false;
              typing.querySelector(".typing-label").textContent = "";
              break;
            case "annotations":
              pendingNotes.push(ev);
              break;
            case "files_changed":
              ev.paths.forEach((p) => changed.add(p));
              break;
            case "profile":
              setProfile();
              break;
            case "chapter":
              chapter = ev;
              break;
            case "progress":
              if (ev.status === "învățat") learned = true;
              toast(`Progres salvat: ${ev.topic} · ${ev.status}`);
              loadCourse().catch(() => {});
              break;
            case "error": {
              failed = true;
              const err = document.createElement("div");
              err.className = "error-box";
              err.textContent = ev.message;
              a.el.appendChild(err);
              break;
            }
          }
        }
      }
    } catch (e) {
      failed = true;
      const err = document.createElement("div");
      err.className = "error-box";
      err.textContent = "Eroare: " + e.message;
      a.el.appendChild(err);
    } finally {
      if (raf) cancelAnimationFrame(raf);
      flush();
      typing.remove();
      setBusy(false);
      if (changed.size) {
        await loadTree().catch(() => {});
        await reloadChangedFiles([...changed]);
        toast("Tutorele a creat/modificat: " + [...changed].join(", "));
      }
      // Tutorele a început altă lecție: n-o deschidem singuri, elevul trece la ea când vrea, cu „Următorul pas”.
      if (chapter) toast(`Tutorele propune: ${chapter.topic}. Apasă „Următorul pas” când vrei să treci la ea.`, 6000);
      for (const ev of pendingNotes) await receiveNotes(ev.path, ev.notes);
      // la final, ca reîncărcarea fișierelor modificate de tutore să nu-l suprascrie
      suggestAfterReply({
        text: md, failed, learned: learned || Boolean(chapter),
        task: Boolean(chapter || changed.size),
        notes: pendingNotes.some((ev) => ev.notes.length),
      });
    }
  }

  // Fiecare capitol are folderul lui de cod (capitole/NN-slug/); îl arătăm în Explorer și îl deschidem.
  async function openChapter(path, title) {
    path.split("/").slice(0, -1).reduce((acc, part) => {
      const p = acc ? acc + "/" + part : part;
      state.expanded.add(p);
      return p;
    }, "");
    store.set("pt-expanded", JSON.stringify([...state.expanded]));
    await loadTree().catch(() => {});
    if (state.active === path) return;
    await openFile(path, { focus: false }).catch(() => {});
    if (title) toast(`Capitol: ${title} — codul lui e în ${path}`, 4000);
  }

  $("#resetChatBtn").addEventListener("click", async () => {
    const ok = await confirmModal("Conversație nouă", "Ștergi istoricul conversației pentru acest proiect? Profilul tău (nivel, progres) rămâne.", "Șterge istoricul");
    if (!ok) return;
    await api(P("chat"), { method: "DELETE" });
    loadChat();
  });

  // ------------------------------------------------------------------ Profil („Nivelul tău”, din meniul contului)
  const profileModal = $("#profileModal");
  async function openProfile() {
    userDropdown.hidden = true;
    try {
      PTProfile.render($("#profileCard"), await api("/api/progress"));
      profileModal.hidden = false;
      $("#profileClose").focus();
    } catch (e) { toast(e.message); }
  }
  const closeProfile = () => { profileModal.hidden = true; };
  // tutorele a actualizat profilul în timp ce fereastra e deschisă: o reîmprospătăm
  function setProfile() { if (!profileModal.hidden) openProfile(); }
  $("#levelMenuBtn").addEventListener("click", openProfile);
  $("#profileClose").addEventListener("click", closeProfile);
  profileModal.addEventListener("click", (e) => { if (e.target === profileModal) closeProfile(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !profileModal.hidden) closeProfile(); });

  // Venit din pagina de progres cu „Exersează cu tutorele”: precompletăm mesajul (nu-l trimitem singuri).
  const askParam = new URLSearchParams(location.search).get("ask");
  if (askParam) {
    chatInput.value = askParam;
    autoGrow();
    floatOpen = true;
    history.replaceState(null, "", location.pathname);
  }

  // ------------------------------------------------------------------ Sumarul lecțiilor (stânga)
  const STATUS_CLS = { "în lucru": "doing", "învățat": "done" };
  let prevStatus = null;  // slug -> status la randarea anterioară, ca să evidențiem ce s-a schimbat
  let shownLesson = null;  // lecția al cărei cod l-am deschis ultima dată în editor

  // Elevul alege o lecție: editorul trece pe codul ei, iar lecția devine cea activă (și pentru tutore).
  async function selectLesson(t) {
    if (isMobile()) showPane("code");
    try {
      const r = await api(P("chapter"), { method: "POST", body: { topic: t.slug } });
      shownLesson = t.slug;
      // o lecție deja învățată nu devine „pasul activ”: modulul ei rămâne deschis și editorul rămâne pe codul ei
      openModules.add(t.module.slug);
      justPicked = true;
      // Lecțiile Django n-au fișier de capitol: se lucrează în proiectul Django al elevului (are manage.py;
      // lecțiile îl numesc „blog”, dar numele poate fi oricare).
      if (r.path) await openChapter(r.path, t.title);
      else if (treeData.some((n) => n.path === "manage.py")) await openFile("manage.py", { focus: false }).catch(() => {});
      else toast(`„${t.title}” e o lecție Django: lucrezi în proiectul tău Django (în lecții se numește blog). Treci în el sau creează-l cu +.`, 6000);
      loadCourse().catch(() => {});
    } catch (e) { toast(e.message); }
  }
  async function loadCourse() {
    const d = await api("/api/progress" + (state.project ? "?project=" + encodeURIComponent(state.project) : ""));
    renderCourse(d.modules, d.current);
  }

  // Căutarea în lecții: după titlu și descriere, fără să conteze diacriticele și literele mari.
  const fold = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const courseSearch = document.createElement("label");
  courseSearch.className = "course-search";
  courseSearch.innerHTML = `${icon("search")}<input type="search" placeholder="Caută lecții…" aria-label="Caută lecții">`;
  courseSearch.querySelector("input").addEventListener("input", filterCourse);
  function filterCourse() {
    const q = fold(courseSearch.querySelector("input").value.trim());
    $$("#course .course-module").forEach((det) => {
      let any = false;
      det.querySelectorAll(".course-topic").forEach((row) => {
        const hit = !q || row.dataset.search.includes(q);
        row.hidden = !hit;
        any ||= hit;
      });
      det.hidden = !any;
      det.open = q ? any : Boolean(det.dataset.open);
    });
  }
  const openModules = new Set();  // modulele deschise în sumar (slug)
  let justPicked = false;         // elevul a ales o lecție: următoarea randare nu-i mută editorul
  const readLessons = () => {
    try { return new Set(JSON.parse(store.get("pt-read-lessons", "[]"))); } catch { return new Set(); }
  };
  function renderCourse(modules, currentSlug) {
    const box = $("#course");
    box.innerHTML = "";
    const all = modules.flatMap((m) => m.topics.map((t) => ({ ...t, module: m })));
    const num = new Map(all.map((t, i) => [t.slug, i + 1]));  // numărul lecției în curriculum
    const done = all.filter((t) => t.status === "învățat").length;
    const doing = all.filter((t) => t.status === "în lucru").length;
    $("#courseCount").textContent = `${done}/${all.length}`;
    // Pasul activ: ultimul subiect trecut „în lucru” de tutore, altfel primul neînvățat.
    const doingTopics = all.filter((t) => t.status === "în lucru").sort((a, b) => (b.updated_at || "").localeCompare(a.updated_at || ""));
    // Lecția curentă: ultima deschisă de elev (serverul o ține minte), altfel pasul următor din curriculum.
    const current = all.find((t) => t.slug === currentSlug) || doingTopics[0] || all.find((t) => t.status !== "învățat");
    const changed = new Set(prevStatus ? all.filter((t) => prevStatus[t.slug] !== t.status).map((t) => t.slug) : []);
    prevStatus = Object.fromEntries(all.map((t) => [t.slug, t.status]));

    const head = document.createElement("div");
    head.className = "course-head";
    head.innerHTML = '<div class="course-bar"><span class="done"></span><span class="doing"></span></div>';
    head.querySelector(".done").style.width = (100 * done / (all.length || 1)) + "%";
    head.querySelector(".doing").style.width = (100 * doing / (all.length || 1)) + "%";
    const hadFocus = document.activeElement === courseSearch.querySelector("input");
    head.appendChild(courseSearch);
    box.appendChild(head);

    modules.forEach((m) => {
      const det = document.createElement("details");
      det.className = "course-module";
      det.open = openModules.has(m.slug) || (!!current && current.module === m) || m.topics.some((t) => changed.has(t.slug));
      if (det.open) openModules.add(m.slug);
      det.dataset.open = det.open ? "1" : "";  // starea de dinaintea căutării
      // ce deschide sau închide elevul rămâne așa și după ce sumarul se redesenează
      det.addEventListener("toggle", () => {
        if (courseSearch.querySelector("input").value.trim()) return;  // căutarea deschide temporar
        if (det.open) openModules.add(m.slug); else openModules.delete(m.slug);
      });
      const n = m.topics.filter((t) => t.status === "învățat").length;
      const sum = document.createElement("summary");
      const st = document.createElement("span");
      st.className = "cm-title";
      st.textContent = m.title;
      const cnt = document.createElement("span");
      cnt.className = "cm-count" + (n === m.topics.length ? " complete" : "");
      cnt.textContent = `${n}/${m.topics.length}`;
      sum.insertAdjacentHTML("afterbegin", icon("chevron-right", "cm-caret"));
      sum.append(PTIcons.module(m.slug), st, cnt);
      det.appendChild(sum);
      const list = document.createElement("div");
      list.className = "cm-topics";
      m.topics.forEach((t) => {
        const row = document.createElement("div");
        row.className = "course-topic" + (current && t.slug === current.slug ? " current" : "") + (changed.has(t.slug) ? " just-changed" : "");
        row.dataset.search = fold(`${num.get(t.slug)} ${t.title} ${t.summary || ""}`);
        const a = document.createElement("button");
        a.className = "course-link";
        a.title = (t.summary || t.title) + " — lucrează la lecția asta (îi deschide codul)";
        a.addEventListener("click", () => selectLesson({ ...t, module: m }));
        const dot = document.createElement("span");
        dot.className = "course-dot " + (STATUS_CLS[t.status] || "");
        if (t.status === "învățat") dot.innerHTML = icon("check");
        const tt = document.createElement("span");
        tt.textContent = `${num.get(t.slug)}. ${t.title}`;  // același număr ca în capitole/NN-... și „lecția N”
        a.append(dot, tt);
        row.appendChild(a);
        const book = document.createElement("a");
        book.className = "course-code";
        book.href = "/progres/#" + encodeURIComponent(t.slug);
        book.title = "Citește lecția";
        book.setAttribute("aria-label", "Lecția: " + t.title);
        book.innerHTML = icon("book-open");
        // Prima dată la un capitol: iconul clipește până deschizi lecția (progress.js o notează ca citită).
        if (current && t.slug === current.slug && !readLessons().has(t.slug)) book.classList.add("read-flash");
        book.addEventListener("click", () => book.classList.remove("read-flash"));
        row.appendChild(book);
        list.appendChild(row);
      });
      det.appendChild(list);
      box.appendChild(det);
    });
    filterCourse();
    if (hadFocus) courseSearch.querySelector("input").focus();
    else box.querySelector(".course-topic.current")?.scrollIntoView({ block: "nearest" });

    // Doar la pornire editorul deschide codul lecției active. După aceea nu se mută singur (nici când tutorele
    // bifează sau începe o lecție): elevul decide, din sumar sau cu „Următorul pas”.
    if (current?.code_path && shownLesson === null) {
      shownLesson = current.slug;
      const folder = current.code_path.split("/").slice(0, -1).join("/") + "/";
      if (!justPicked && !(state.active || "").startsWith(folder)) openChapter(current.code_path);
    }
    justPicked = false;
  }

  // ------------------------------------------------------------------ Proiecte
  async function loadProjects(select) {
    let { projects } = await api("/api/projects");
    if (!projects.length) {
      ({ projects } = await api("/api/projects", { method: "POST", body: { name: "primul-proiect" } }));
    }
    const sel = $("#projectSelect");
    sel.innerHTML = "";
    projects.forEach((p) => { const o = document.createElement("option"); o.value = o.textContent = p; sel.appendChild(o); });
    const want = select || store.get("pt-project", projects[0]);
    await switchProject(projects.includes(want) ? want : projects[0]);
  }

  async function switchProject(name) {
    await saveAll();
    state.project = name;
    store.set("pt-project", name);
    $("#projectSelect").value = name;
    shownLesson = null;  // în proiectul nou, editorul deschide codul lecției active
    state.tabs = [];
    state.active = null;
    state.termSince = 0;
    termOut.textContent = "";
    setTermRunning(false, "", null);
    activate(null);
    state.notes = {};
    await Promise.all([loadTree(), loadChat(), loadNotes().catch(() => {})]);
    const last = store.get("pt-active-" + name, "");
    if (last) await openFile(last, { focus: false }).catch(() => {});
    else if (treeData.some((n) => n.path === "main.py")) await openFile("main.py", { focus: false }).catch(() => {});
    shownLesson = null;
    // După fișierul de data trecută: dacă lecția activă are alt folder, editorul trece pe codul ei.
    await loadCourse().catch(() => { $("#course").innerHTML = '<p class="muted course-loading">Nu pot încărca lecțiile.</p>'; });
    if (isMobile()) showPane("chat");
    setFloatOpen(floatOpen);
    pollTerm();
  }

  $("#projectSelect").addEventListener("change", (e) => switchProject(e.target.value));
  $("#newProjectBtn").addEventListener("click", async () => {
    const name = await promptModal("Proiect nou", "", "ex: calculator, blog-django");
    if (!name) return;
    try {
      await api("/api/projects", { method: "POST", body: { name } });
      await loadProjects(name);
    } catch (e) { toast(e.message); }
  });

  window.addEventListener("beforeunload", () => {
    state.tabs.filter((t) => t.dirty && t.doc).forEach((t) => {
      fetch(P("file"), {
        method: "PUT", keepalive: true,
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
        body: JSON.stringify({ path: t.path, content: t.doc.getValue() }),
      });
    });
  });

  // ------------------------------------------------------------------ Cont
  const userDropdown = $("#userDropdown");
  $("#userBtn").addEventListener("click", (e) => { e.stopPropagation(); userDropdown.hidden = !userDropdown.hidden; });
  document.addEventListener("pointerdown", (e) => { if (!e.target.closest(".user-menu")) userDropdown.hidden = true; });

  async function loadMe() {
    const me = await api("/api/me");
    const link = $("#serverLink");
    link.href = me.sandbox.server_url;
    link.textContent = "server: " + me.sandbox.server_url.replace(/^https?:\/\//, "");
    link.hidden = false;
  }

  // ------------------------------------------------------------------ Start
  loadMe().catch(() => {});
  loadProjects().catch((e) => toast("Nu pot încărca proiectele: " + e.message, 6000));
})();
