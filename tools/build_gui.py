#!/usr/bin/env python3
"""Builds gui/timemanip.gui = vanilla timemanip.gui + this mod's snippets.

After a game patch: copy the new game/gui/timemanip.gui over
tools/timemanip.vanilla.gui and re-run:  python3 tools/build_gui.py
"""
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
MOD = TOOLS.parent / "mod"

lines = (TOOLS / "timemanip.vanilla.gui").read_text(encoding="utf-8-sig").split("\n")


def stepper(indent, field, label, value):
    """`#@STEPPER <field> <label loc> <value loc>` -> label, minus, value, plus.
    Buttons follow the in-game convention: click 1, shift-click 5, ctrl-click 10,
    calling dsm_<field>_<up|down>_<step>_sgui."""
    def sgui(d, step):
        return f"\"[GetScriptedGui('dsm_{field}_{d}_{step}_sgui').Execute( GuiScope.SetRoot( GetPlayer.MakeScope ).End )]\""

    def button(kind, d):
        return [
            f"\t{kind} = {{",
            "\t\tsize = { 26 26 }",
            "\t\tparentanchor = vcenter",
            "\t\tclick_modifiers = {",
            f"\t\t\tondefault = {sgui(d, 1)}",
            f"\t\t\tonshift = {sgui(d, 5)}",
            f"\t\t\tonctrl = {sgui(d, 10)}",
            "\t\t}",
            "\t}",
        ]

    body = (["flowcontainer = {",
             "\tdirection = horizontal",
             "\tspacing = 6",
             f"\ttext_single = {{ text = \"{label}\" minimumsize = {{ 60 0 }} parentanchor = vcenter }}"]
            + button("button_icon_minus_action", "down")
            + [f"\ttext_single = {{ text = \"{value}\" minimumsize = {{ 56 0 }} align = center|nobaseline parentanchor = vcenter }}"]
            + button("button_icon_plus_action", "up")
            + ["}"])
    return [indent + l for l in body]


def snippet(name):
    out = []
    for line in (TOOLS / name).read_text().rstrip("\n").split("\n"):
        if line.strip().startswith("#@STEPPER"):
            indent = line[:len(line) - len(line.lstrip())]
            out += stepper(indent, *line.split()[1:])
        else:
            out.append(line)
    return out


# Toggle button: last child of the date box (the widget after "### DATE"),
# so it draws on top of the date text and weekday bar.
d = next(n for n, l in enumerate(lines) if l.strip() == "### DATE")
open_ = next(n for n in range(d, d + 3) if lines[n].strip() == "widget = {")
depth = 0
for close in range(open_, len(lines)):
    depth += lines[close].count("{") - lines[close].count("}")
    if depth == 0:
        break
lines[close:close] = [""] + snippet("gui_toggle_button.gui")

# Panel + auto-pause widget: just before the closing brace of `type timemanip`.
start = next(n for n, l in enumerate(lines) if "type timemanip = container" in l)
end = next(n for n in range(start, len(lines)) if lines[n] == "\t}")
lines[end:end] = snippet("gui_panel.gui")

out = MOD / "gui/timemanip.gui"
text = "\n".join(lines)
assert text.count("{") == text.count("}"), "unbalanced braces"
out.write_text(text, encoding="utf-8")
print(f"wrote {out}")
