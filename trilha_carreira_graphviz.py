from pathlib import Path
import csv
import shutil
import subprocess

from trilha_dados import CAREER_EDGES as DEFAULT_CAREER_EDGES
from trilha_dados import ROLE_GROUPS as DEFAULT_ROLE_GROUPS
from trilha_layout import LAYOUT


OUTPUT_DIR = Path("Resultados") / "trilhas_carreira"
BRANCHES_CSV_PATH = Path("data") / "filiais_trilha.csv"
ROLES_CSV_PATH = Path("data") / "trilha_cargos.csv"
EDGES_CSV_PATH = Path("data") / "trilha_conexoes.csv"


DEFAULT_BRANCHES = [
    "Oliveira",
    "Itatiba/71",
    "Itatiba/72",
]


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("/", "_")
        .replace("-", "_")
    )


def make_node_id(branch_name: str, role_name: str) -> str:
    safe_branch = slugify(branch_name)
    safe_role = slugify(role_name)
    return f"{safe_branch}__{safe_role}"


def quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def load_branches(csv_path: Path) -> list[str]:
    if not csv_path.exists():
        return DEFAULT_BRANCHES

    branches: list[str] = []
    seen: set[str] = set()

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "filial" not in reader.fieldnames:
            raise ValueError("O arquivo de filiais precisa ter uma coluna chamada 'filial'.")

        for row in reader:
            branch_name = (row.get("filial") or "").strip()
            if not branch_name:
                continue
            normalized = branch_name.casefold()
            if normalized in seen:
                continue
            seen.add(normalized)
            branches.append(branch_name)

    if not branches:
        raise ValueError("Nenhuma filial valida foi encontrada no arquivo de entrada.")

    return branches


def load_role_groups(csv_path: Path) -> dict[str, dict[str, object]]:
    if not csv_path.exists():
        return DEFAULT_ROLE_GROUPS

    role_groups: dict[str, dict[str, object]] = {}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required_fields = {"grupo", "label_grupo", "cor_grupo", "cargo"}
        if not reader.fieldnames or not required_fields.issubset(set(reader.fieldnames)):
            raise ValueError(
                "O arquivo de cargos precisa ter as colunas: grupo, label_grupo, cor_grupo, cargo."
            )

        for row in reader:
            group_key = (row.get("grupo") or "").strip()
            group_label = (row.get("label_grupo") or "").strip()
            group_color = (row.get("cor_grupo") or "").strip()
            role_name = (row.get("cargo") or "").strip()

            if not all([group_key, group_label, group_color, role_name]):
                continue

            group = role_groups.setdefault(
                group_key,
                {"label": group_label, "color": group_color, "roles": []},
            )
            group["roles"].append(role_name)

    if not role_groups:
        raise ValueError("Nenhum cargo valido foi encontrado no arquivo de cargos.")

    return role_groups


def load_career_edges(csv_path: Path) -> list[tuple[str, str]]:
    if not csv_path.exists():
        return DEFAULT_CAREER_EDGES

    edges: list[tuple[str, str]] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required_fields = {"origem", "destino"}
        if not reader.fieldnames or not required_fields.issubset(set(reader.fieldnames)):
            raise ValueError("O arquivo de conexoes precisa ter as colunas: origem, destino.")

        for row in reader:
            source_role = (row.get("origem") or "").strip()
            target_role = (row.get("destino") or "").strip()
            if not source_role or not target_role:
                continue
            edges.append((source_role, target_role))

    if not edges:
        raise ValueError("Nenhuma conexao valida foi encontrada no arquivo de conexoes.")

    return edges


def validate_structure(
    role_groups: dict[str, dict[str, object]],
    career_edges: list[tuple[str, str]],
) -> None:
    known_roles = {
        role_name
        for group_data in role_groups.values()
        for role_name in group_data["roles"]
    }

    invalid_edges = [
        (source_role, target_role)
        for source_role, target_role in career_edges
        if source_role not in known_roles or target_role not in known_roles
    ]

    if invalid_edges:
        raise ValueError(
            f"Existem conexoes com cargos inexistentes: {invalid_edges[:5]}"
        )


def build_branch_dot(
    branch_name: str,
    role_groups: dict[str, dict[str, object]],
    career_edges: list[tuple[str, str]],
) -> str:
    # Ajuste visual centralizado em trilha_layout.py.
    graph_style = LAYOUT["graph"]
    node_style = LAYOUT["node"]
    edge_style = LAYOUT["edge"]
    cluster_style = LAYOUT["cluster"]
    title = LAYOUT["title_template"].format(branch=branch_name)

    lines = [
        "digraph G {",
        '  graph [rankdir=%s, splines=%s, nodesep=%s, ranksep=%s, bgcolor=%s, labelloc=%s, pad=%s, fontname=%s, fontsize=%s, label=%s];'
        % (
            quote(graph_style["rankdir"]),
            quote(graph_style["splines"]),
            quote(graph_style["nodesep"]),
            quote(graph_style["ranksep"]),
            quote(graph_style["bgcolor"]),
            quote(graph_style["labelloc"]),
            quote(graph_style["pad"]),
            quote(graph_style["fontname"]),
            graph_style["fontsize"],
            quote(title),
        ),
        '  node [shape=%s, style=%s, fontname=%s, fontsize=%s, margin=%s];'
        % (
            quote(node_style["shape"]),
            quote(node_style["style"]),
            quote(node_style["fontname"]),
            node_style["fontsize"],
            quote(node_style["margin"]),
        ),
        '  edge [color=%s, penwidth=%s];'
        % (
            quote(edge_style["color"]),
            edge_style["penwidth"],
        ),
    ]

    for group_key, group_data in role_groups.items():
        group_label = f"{group_data['label']} - {branch_name}"
        lines.append(f"  subgraph cluster_{slugify(branch_name)}_{group_key} {{")
        lines.append(f"    label={quote(group_label)};")
        lines.append(f"    color={quote(group_data['color'])};")
        lines.append(f"    style={quote(cluster_style['style'])};")
        lines.append(f"    penwidth={cluster_style['penwidth']};")
        lines.append(f"    fontname={quote(cluster_style['fontname'])};")
        lines.append(f"    fontsize={cluster_style['fontsize']};")

        for role in group_data["roles"]:
            node_id = make_node_id(branch_name, role)
            lines.append(
                "    %s [label=%s, fillcolor=%s, color=%s, fontcolor=%s];"
                % (
                    quote(node_id),
                    quote(role),
                    quote(group_data["color"]),
                    quote(group_data["color"]),
                    quote(node_style["fontcolor"]),
                )
            )

        lines.append("  }")

    for source_role, target_role in career_edges:
        lines.append(
            "  %s -> %s;"
            % (
                quote(make_node_id(branch_name, source_role)),
                quote(make_node_id(branch_name, target_role)),
            )
        )

    lines.append("}")
    return "\n".join(lines)


def render_with_dot(dot_path: Path, output_png_path: Path) -> bool:
    dot_executable = shutil.which("dot")
    # Nao alterar: funcao padrao do Python para localizar o Graphviz
    if not dot_executable:
        common_windows_paths = [
            Path(r"C:\Program Files\Graphviz\bin\dot.exe"),
            Path(r"C:\Program Files (x86)\Graphviz\bin\dot.exe"),
        ]
        for candidate in common_windows_paths:
            if candidate.exists():
                dot_executable = str(candidate)
                break

    if not dot_executable:
        return False

    subprocess.run(
        [dot_executable, "-Tpng", str(dot_path), "-o", str(output_png_path)],
        check=True,
    )
    return True


def render_all(
    branches: list[str],
    role_groups: dict[str, dict[str, object]],
    career_edges: list[tuple[str, str]],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for branch_name in branches:
        file_stem = f"trilha_carreira_{slugify(branch_name)}"
        dot_path = OUTPUT_DIR / f"{file_stem}.dot"
        png_path = OUTPUT_DIR / f"{file_stem}.png"
        dot_path.write_text(
            build_branch_dot(branch_name, role_groups, career_edges),
            encoding="utf-8",
        )

        if render_with_dot(dot_path, png_path):
            print(f"Arquivo gerado: {png_path}")
        else:
            print(f"Arquivo DOT gerado: {dot_path}")
            print("Graphviz 'dot' nao encontrado no PATH. Adicione ao PATH para gerar PNG automaticamente.")


if __name__ == "__main__":
    loaded_role_groups = load_role_groups(ROLES_CSV_PATH)
    loaded_career_edges = load_career_edges(EDGES_CSV_PATH)
    validate_structure(loaded_role_groups, loaded_career_edges)
    render_all(
        load_branches(BRANCHES_CSV_PATH),
        loaded_role_groups,
        loaded_career_edges,
    )
