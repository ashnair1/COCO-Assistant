from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()


for path in sorted(Path("coco_assistant").glob("**/*.py")):

    module_path = path.relative_to(".").with_suffix("")
    if "classic" in str(module_path) or "__init__" in str(module_path):
        continue

    doc_path = path.relative_to("coco_assistant").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    nav[module_path.parts] = doc_path

    with mkdocs_gen_files.open(full_doc_path, "w") as f:
        ident = ".".join(module_path.parts)
        print("::: " + ident, file=f)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())