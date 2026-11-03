"""移動したページの古い URL に、新しいページへ転送するページを作る（redirects.yml）。"""
import os

import yaml


def on_post_build(config, **kwargs):
    root = os.path.dirname(config["config_file_path"])
    path = os.path.join(root, "redirects.yml")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        moves = yaml.safe_load(f) or {}
    site = config["site_dir"]
    for old, new in moves.items():
        old_dir = old[:-3] if old.endswith(".md") else old
        if old.endswith("/index.md"):
            old_dir = old[: -len("/index.md")]
        new_dir = new[: -len("/index.md")] if new.endswith("/index.md") else new[:-3]
        out = os.path.join(site, old_dir, "index.html")
        if os.path.exists(out):
            continue
        depth = old_dir.count("/") + 1
        target = "../" * depth + new_dir + "/"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write('<!doctype html><meta charset="utf-8"><title>移動しました</title>'
                    '<meta http-equiv="refresh" content="0; url=%s">'
                    '<link rel="canonical" href="%s"><p><a href="%s">新しい場所へ移動します</a></p>\n'
                    % (target, target, target))
