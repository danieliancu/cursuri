/* Tema (luminoasă / întunecată / ca sistemul): butonul soare-lună și meniul de setări din bara de sus.
   Preferința e în localStorage („pt-theme”), comună tuturor utilizatorilor de pe dispozitiv. */
(() => {
  "use strict";
  const media = matchMedia("(prefers-color-scheme: dark)");
  const get = () => { try { return localStorage.getItem("pt-theme") || "dark"; } catch { return "dark"; } };
  const set = (v) => { try { localStorage.setItem("pt-theme", v); } catch { /* fără storage */ } apply(); };

  function apply() {
    const pref = get();
    const dark = pref === "dark" || (pref === "system" && media.matches);
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    document.querySelectorAll("[data-theme-pref]").forEach((b) => {
      b.classList.toggle("active", b.dataset.themePref === pref);
      b.setAttribute("aria-checked", String(b.dataset.themePref === pref));
    });
  }

  const menu = document.getElementById("settingsDropdown");
  document.getElementById("themeToggle")?.addEventListener("click", () =>
    set(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));
  document.getElementById("settingsBtn")?.addEventListener("click", (e) => { e.stopPropagation(); menu.hidden = !menu.hidden; });
  document.querySelectorAll("[data-theme-pref]").forEach((b) =>
    b.addEventListener("click", () => { set(b.dataset.themePref); menu.hidden = true; }));
  document.addEventListener("pointerdown", (e) => { if (menu && !e.target.closest(".settings-menu")) menu.hidden = true; });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && menu) menu.hidden = true; });
  media.addEventListener("change", apply);
  apply();
})();
