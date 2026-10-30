from decimal import Decimal

from django import template

register = template.Library()


def format_gbp(value) -> str:
    """£12.34 pentru sume mari, £0.0026 pentru sume mici (un mesaj costă fracțiuni de penny)."""
    v = Decimal(value or 0)
    if v == 0:
        return "£0"
    return f"£{v:,.2f}" if abs(v) >= 1 else f"£{v:.4f}"


register.filter("gbp", format_gbp)


@register.simple_tag
def asset(path: str) -> str:
    """URL static cu `?v=<data modificării>`, ca browserul să ia mereu versiunea nouă după o schimbare."""
    from django.contrib.staticfiles import finders
    from django.templatetags.static import static

    url = static(path)
    found = finders.find(path)
    if found:
        import os

        url += f"?v={int(os.path.getmtime(found))}"
    return url


_sprite_cache: dict[str, tuple[float, str]] = {}


@register.simple_tag
def icon_sprite():
    """Setul de iconițe (tutor/icons.svg) pus o dată în pagină, ascuns; `{% icon %}` și PTIcons îl referă cu `#nume`.

    Un <use> spre un fișier extern n-ar merge dacă fișierele statice vin de pe alt domeniu (CDN).
    Conținutul se citește o dată și se recitește doar când fișierul se schimbă.
    """
    import os

    from django.contrib.staticfiles import finders
    from django.utils.safestring import mark_safe

    path = finders.find("tutor/icons.svg")
    mtime = os.path.getmtime(path)
    cached = _sprite_cache.get(path)
    if not cached or cached[0] != mtime:
        with open(path, encoding="utf-8") as f:
            svg = f.read().replace("<svg ", '<svg class="icon-sprite" aria-hidden="true" ', 1)
        cached = _sprite_cache[path] = (mtime, svg)
    return mark_safe(cached[1])


@register.simple_tag
def icon(name: str, cls: str = ""):
    """Iconița Lucide `name` din setul pus în pagină de `{% icon_sprite %}` (ca PTIcons.svg din icons.js)."""
    from django.utils.html import format_html

    return format_html('<svg class="i {}" aria-hidden="true"><use href="#{}"/></svg>', cls, name)
