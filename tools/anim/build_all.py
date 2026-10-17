import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
from common import Place, Save  # noqa: E402
from preview import Preview  # noqa: E402

MODULES = ["pipeline", "graphics", "pp1", "pp2", "pp3", "pp4", "gfx_shadows", "gfx_ao_gi", "gfx_refl_trans"]


def Main():
    only = set(sys.argv[1:])
    for mod_name in MODULES:
        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            continue
        for fn in mod.FIGS:
            info = fn()
            if only and info["name"] not in only:
                continue
            svg = Save(info["scene"], info["name"])
            Place(info["page"], info["name"], svg, before=info.get("before"), replace_fig=info.get("replace_fig"))
            w, h = info["size"]
            Preview(info["name"], info["times"], w, h)
            print("ok", info["name"], len(svg) // 1024, "KB", svg.count("<animate"), "animates")


if __name__ == "__main__":
    Main()
