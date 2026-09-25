# SPDX-License-Identifier: MIT
"""mkdocs hook: the docs link straight to repo files (../cad/params.scad, ../cart/ORDER.md …)
so they work when read on GitHub. On the built site those targets don't exist, so rewrite
any relative link that climbs out of docs/ into a GitHub URL (blob for files, tree for dirs)."""
import os
import posixpath
import re

REPO = "https://github.com/zohebzma2-cmyk/autonomous-mower"
BRANCH = "main"
LINK = re.compile(r"(\]\()(\.\./[^)\s#]+)(#[^)\s]*)?(\))")


def on_page_markdown(markdown, page, config, files, **kwargs):
    docs_dir = config["docs_dir"]
    root = os.path.dirname(docs_dir)
    page_dir = posixpath.dirname(page.file.src_uri)

    def fix(m):
        target = posixpath.normpath(posixpath.join("docs", page_dir, m.group(2)))
        if target.startswith("docs/") or target.startswith(".."):
            return m.group(0)                      # stays inside docs/ -> mkdocs resolves it
        kind = "tree" if os.path.isdir(os.path.join(root, target)) else "blob"
        return f"{m.group(1)}{REPO}/{kind}/{BRANCH}/{target}{m.group(3) or ''}{m.group(4)}"

    return LINK.sub(fix, markdown)
