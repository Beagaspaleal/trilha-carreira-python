LAYOUT: dict[str, str | dict[str, str]] = {
    "title_template": "TRILHA DE CARREIRA - DIRETOS, INDIRETOS E STAFF - {branch}",
    "graph": {
        "rankdir": "LR",
        "splines": "ortho",
        "nodesep": "0.30",
        "ranksep": "0.65",
        "bgcolor": "white",
        "labelloc": "t",
        "pad": "0.3",
        "fontname": "Arial Bold",
        "fontsize": "18",
    },
    "node": {
        "shape": "box",
        "style": "rounded,filled",
        "fontname": "Arial",
        "fontsize": "10",
        "margin": "0.16,0.08",
        "fontcolor": "white",
    },
    "edge": {
        "color": "#6a6a6a",
        "penwidth": "1.1",
    },
    "cluster": {
        "style": "rounded",
        "penwidth": "1.4",
        "fontname": "Arial",
        "fontsize": "12",
    },
}
