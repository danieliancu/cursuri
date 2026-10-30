/* Markdown → HTML sigur, cu blocuri de cod colorate (CodeMirror runmode) și buton „Copiază”.
   Folosit de chat (app.js) și de pagina de progres (progress.js). */
window.PTMarkdown = (() => {
  "use strict";
  marked.setOptions({ gfm: true, breaks: false });

  const MODES = {
    python: "python", py: "python", html: "django", django: "django", js: "javascript", javascript: "javascript",
    css: "css", bash: "shell", sh: "shell", shell: "shell", console: "shell", json: { name: "javascript", json: true },
  };
  const LABELS = {
    python: "Python", py: "Python", html: "HTML", django: "HTML", css: "CSS", js: "JavaScript", javascript: "JavaScript",
    json: "JSON", bash: "Terminal", sh: "Terminal", shell: "Terminal", console: "Terminal", text: "Text",
  };
  const TERMINAL = new Set(["bash", "sh", "shell", "console", "text"]);

  function codeBlock(pre, text, lang, { lineStart = null, output = false } = {}) {
    const code = pre.querySelector("code") || pre;
    const mode = MODES[lang];
    if (mode) { code.textContent = ""; CodeMirror.runMode(text, mode, code); } else code.textContent = text;
    const wrap = document.createElement("div");
    wrap.className = "code-block" + (lineStart ? " numbered" : "") + (output ? " output" : "");
    const head = document.createElement("div");
    head.className = "code-head";
    const label = document.createElement("span");
    label.className = "code-label";
    // În lecții, blocul ```text de după cod e rezultatul rulării.
    const name = output ? "Rezultat (output)" : LABELS[lang] || lang || "Cod";
    const logo = output ? null : PTIcons.lang(lang);
    label.innerHTML = logo || PTIcons.svg(TERMINAL.has(lang) || output ? "square-terminal" : "code-xml");
    label.append(name);
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.innerHTML = PTIcons.svg("copy") + "<span>Copiază</span>";
    btn.addEventListener("click", () => {
      navigator.clipboard?.writeText(text).then(() => {
        btn.lastChild.textContent = "Copiat ✓";
        setTimeout(() => (btn.lastChild.textContent = "Copiază"), 1400);
      });
    });
    head.append(label, btn);
    pre.replaceWith(wrap);
    if (lineStart) {
      const nums = document.createElement("pre");
      nums.className = "line-nums";
      nums.setAttribute("aria-hidden", "true");
      nums.textContent = text.replace(/\n$/, "").split("\n").map((_, i) => lineStart + i).join("\n");
      const body = document.createElement("div");
      body.className = "code-body";
      body.append(nums, pre);
      wrap.append(head, body);
    } else {
      wrap.append(head, pre);
    }
    return wrap;
  }

  // Lecțiile au mereu aceleași 7 secțiuni; fiecare devine un card cu iconița ei.
  const SECTIONS = [
    [/^ce este/i, "book-open", "blue"],
    [/^de ce/i, "database", "purple"],
    [/^cum func/i, "cog", "orange"],
    [/^exemplu/i, "code-xml", "green"],
    [/^gre[șş]eli/i, "triangle-alert", "red"],
    [/^exerci/i, "pencil-line", "teal"],
    [/^pe scurt/i, "list-checks", "indigo"],
  ];
  function lessonSections(el) {
    const kids = [...el.children];
    if (!kids.some((k) => k.tagName === "H2")) return;
    el.innerHTML = "";
    let card = null;
    let intro = null;
    for (const k of kids) {
      if (k.tagName === "H2") {
        const [, icon, color] = SECTIONS.find(([re]) => re.test(k.textContent.trim())) || [null, "book-open", "blue"];
        card = document.createElement("section");
        card.className = "lesson-card";
        const head = document.createElement("div");
        head.className = "sec-head";
        const tile = document.createElement("span");
        tile.className = "sec-icon " + color;
        tile.innerHTML = PTIcons.svg(icon);
        intro = document.createElement("div");
        intro.className = "sec-intro";
        intro.append(k);
        head.append(tile, intro);
        card.append(head);
        el.append(card);
      } else if (intro && k.tagName === "P" && intro.children.length === 1) {
        intro.append(k);  // primul paragraf stă lângă iconiță, sub titlu
      } else {
        intro = null;
        (card || el).append(k);
      }
    }
  }

  // În chat: titlul „Sarcina ta” / „Exercițiu” și ce urmează după el (până la alt titlu) devin un card.
  function taskCards(el) {
    const isTask = (h) => /^(sarcina|exerci[țţt]i|tema ta|provocare)/i.test(h.textContent.trim());
    [...el.querySelectorAll(":scope > h1, :scope > h2, :scope > h3, :scope > h4")].filter(isTask).forEach((h) => {
      const card = document.createElement("div");
      card.className = "task-card";
      const head = document.createElement("div");
      head.className = "task-head";
      head.innerHTML = `<span class="task-icon">${PTIcons.svg("clipboard-list")}</span>`;
      h.replaceWith(card);
      head.append(h);
      card.append(head);
      let n = card.nextElementSibling;
      while (n && !/^H[1-4]$/.test(n.tagName) && !n.classList.contains("task-card")) {
        const next = n.nextElementSibling;
        card.append(n);
        n = next;
      }
    });
  }

  /** `lesson`: lecție din pagina de progres (secțiuni-card, numere de rând); altfel mesaj de chat. */
  function render(el, md, { lesson = false } = {}) {
    el.innerHTML = DOMPurify.sanitize(marked.parse(md || ""));
    let prevLang = null;
    el.querySelectorAll("pre > code").forEach((code) => {
      const lang = ((code.className.match(/language-(\S+)/) || [])[1] || "").toLowerCase();
      // în lecții, un bloc ```text după unul de cod (cel mult cu un rând „...:” între ele) e output-ul lui
      const pre = code.parentElement;
      const prev = pre.previousElementSibling;
      const isCode = (e) => e?.classList.contains("code-block");
      const afterCode = isCode(prev) || (prev?.tagName === "P" && /:\s*$/.test(prev.textContent) && isCode(prev.previousElementSibling));
      const output = lesson && lang === "text" && afterCode && prevLang !== "text";
      codeBlock(pre, code.textContent, lang, { lineStart: lesson ? 1 : null, output });
      prevLang = lang;
    });
    el.querySelectorAll("a").forEach((a) => { a.target = "_blank"; a.rel = "noopener"; });
    // O listă întreruptă de un bloc de cod continuă cu <ol start="3">; cerculețele din chat (app.css) sunt un
    // contor CSS care ar porni iar de la 1, așa că îl pornim de la numărul listei.
    el.querySelectorAll("ol[start]").forEach((ol) => { ol.style.counterReset = `step ${ol.start - 1}`; });
    if (lesson) lessonSections(el); else taskCards(el);
  }

  /** Un bloc de cod simplu (fără Markdown), opțional cu numere de linie. */
  function code(text, lang, opts) {
    const holder = document.createElement("div");
    const pre = document.createElement("pre");
    pre.appendChild(document.createElement("code"));
    holder.appendChild(pre);
    return codeBlock(pre, text, lang, opts);
  }

  return { render, code };
})();
