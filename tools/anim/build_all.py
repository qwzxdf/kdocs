import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
from common import Place, Save  # noqa: E402
from preview import Preview  # noqa: E402

MODULES = ["pipeline", "graphics", "pp1", "pp2", "pp3", "pp4", "gfx_shadows", "gfx_ao_gi", "gfx_refl_trans", "gfx_water_terrain", "gfx_atmo", "pp5", "gfx_shadows2", "gfx_skin_hair", "gfx_more", "gfx_more2", "gfx_more3", "gfx_more4", "gfx_more5", "gfx_more6", "gfx_more7", "gfx_more8", "gfx_more9", "g2_ao", "g2_shadow", "g2_refl", "g2_pp", "g2_gi", "g2_ao2", "g2_trans", "g2_water", "g2_world", "g2_pp2", "g2_shadow2", "g2_gi2", "g2_refl2", "g2_skin"]


def Superseded():
    """g2_ で始まる手の込んだ版が持つ図の名前。古い版は作らない。"""
    names = set()
    for mod_name in MODULES:
        if mod_name.startswith("g2_"):
            mod = importlib.import_module(mod_name)
            names.update(getattr(mod, "NAMES", []))
    return names


def Main():
    only = set(sys.argv[1:])
    skip = Superseded()
    for mod_name in MODULES:
        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            continue
        for fn in mod.FIGS:
            info = fn()
            if not mod_name.startswith("g2_") and info["name"] in skip:
                continue
            if only and info["name"] not in only:
                continue
            svg = Save(info["scene"], info["name"])
            Place(info["page"], info["name"], svg, before=info.get("before"), replace_fig=info.get("replace_fig"))
            w, h = info["size"]
            Preview(info["name"], info["times"], w, h)
            print("ok", info["name"], len(svg) // 1024, "KB", svg.count("<animate"), "animates")


if __name__ == "__main__":
    Main()
