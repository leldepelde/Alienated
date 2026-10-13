import textwrap


def center(term, line: str, width: int) -> str:
    pad = max(0, (width - term.length(line)) // 2)
    return " " * pad + line


def wrap(text: str, width: int) -> list:
    return textwrap.wrap(text, width) or [""]


def box(term, lines: list, width: int, title: str = "") -> list:
    inner = width - 4
    if title:
        head = f"╔═ {title} " + "═" * max(0, width - len(title) - 5) + "╗"
    else:
        head = "╔" + "═" * (width - 2) + "╗"
    out = [head]
    for line in lines:
        pad = max(0, inner - term.length(line))
        out.append("║ " + line + " " * pad + " ║")
    out.append("╚" + "═" * (width - 2) + "╝")
    return out


def color(term, name: str, text: str) -> str:
    return getattr(term, name, term.normal)(text)
