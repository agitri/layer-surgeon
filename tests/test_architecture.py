import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1] / "layer_surgeon"


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
    return modules


def assert_layer_excludes(directory: str, forbidden_parts: set[str]) -> None:
    for path in (PACKAGE_ROOT / directory).rglob("*.py"):
        violations = {
            module for module in imported_modules(path) if set(module.split(".")) & forbidden_parts
        }
        assert not violations, f"{path} imports forbidden dependencies: {sorted(violations)}"


def test_domain_has_no_infrastructure_dependencies():
    assert_layer_excludes(
        "domain",
        {
            "adapters",
            "application",
            "argparse",
            "cli",
            "composition",
            "difflib",
            "pathlib",
            "ports",
            "zipfile",
        },
    )


def test_application_depends_on_ports_not_adapters():
    assert_layer_excludes(
        "application",
        {"adapters", "cli", "composition"},
    )
