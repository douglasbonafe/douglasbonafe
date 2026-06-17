"""README builder — assembles the full README.md from config and stats."""

from generator.utils import format_number

REPO_RAW = "https://raw.githubusercontent.com/douglasbonafe/douglasbonafe/main"

ARM_COLORS = {
    "dendrite_violet": "#a78bfa",
    "synapse_cyan": "#00d4ff",
    "axon_amber": "#ffb020",
    "emerald_green": "#10b981",
    "rose_pink": "#f43f5e",
}


def _badge(label: str, message: str, color: str, logo: str = "") -> str:
    label_enc = label.replace(" ", "_").replace("-", "--")
    msg_enc = message.replace(" ", "_").replace("-", "--")
    logo_part = f"&logo={logo}" if logo else ""
    return (
        f"![{label}](https://img.shields.io/badge/{label_enc}-{msg_enc}"
        f"-{color.lstrip('#')}?style=flat-square{logo_part}&logoColor=white)"
    )


def _section_header(title: str, icon: str = "") -> str:
    prefix = f"{icon} " if icon else ""
    return f"\n## {prefix}{title}\n"


def _build_hero(config: dict) -> str:
    profile = config["profile"]
    return (
        f'<div align="center">\n\n'
        f'<img src="{REPO_RAW}/assets/generated/galaxy-header.svg" '
        f'alt="Galaxy Header" width="100%"/>\n\n'
        f'<img src="{REPO_RAW}/assets/generated/stats-card.svg" '
        f'alt="Mission Telemetry" width="100%"/>\n\n'
        f'</div>\n'
    )


def _build_about(config: dict) -> str:
    profile = config["profile"]
    bio = profile.get("bio", "").strip()
    philosophy = profile.get("philosophy", "").strip()
    location = profile.get("localizacao", profile.get("location", ""))
    company = profile.get("empresa", profile.get("company", ""))

    lines = ['<div align="center">\n']

    if bio:
        for line in bio.splitlines():
            stripped = line.strip()
            if stripped:
                lines.append(f"<p>{stripped}</p>\n")

    if philosophy:
        lines.append(f"\n<blockquote>{philosophy}</blockquote>\n")

    meta_parts = []
    if location:
        meta_parts.append(f"📍 {location}")
    if company:
        meta_parts.append(f"🏢 {company}")
    if meta_parts:
        lines.append("\n" + " &nbsp;•&nbsp; ".join(meta_parts) + "\n")

    lines.append("\n</div>\n")
    return _section_header("About Me", "👨‍💻") + "".join(lines)


def _build_tech_stack(config: dict) -> str:
    out = _section_header("Tech Stack", "🚀")
    out += '<div align="center">\n\n'
    out += (
        f'<img src="{REPO_RAW}/assets/generated/tech-stack.svg" '
        f'alt="Tech Stack Galaxy" width="100%"/>\n\n'
    )

    # Arm badges summary below the SVG
    arms = config.get("galaxy_arms", [])
    for arm in arms:
        color = ARM_COLORS.get(arm.get("color", "synapse_cyan"), "#00d4ff").lstrip("#")
        items = arm.get("items", [])
        arm_name = arm.get("name", "")
        if not items:
            continue
        badges = " ".join(
            f'`{item}`' for item in items
        )
        out += f"**{arm_name}:** {badges}\n\n"

    out += "</div>\n"
    return out


def _build_projects(config: dict) -> str:
    projects = config.get("projects", [])
    arms = config.get("galaxy_arms", [])

    out = _section_header("Featured Projects", "🌌")
    out += '<div align="center">\n\n'
    out += (
        f'<img src="{REPO_RAW}/assets/generated/projects-constellation.svg" '
        f'alt="Projects Constellation" width="100%"/>\n\n'
    )
    out += "</div>\n\n"

    # Tracked repos table
    out += "### Tracked Repositories\n\n"
    out += "| Repository | Description | Stack | Stars | Forks |\n"
    out += "|---|---|---|---|---|\n"

    for proj in projects:
        repo = proj.get("repo", "")
        desc = proj.get("descricao", proj.get("description", ""))
        arm_idx = proj.get("arm", 0)
        arm_name = arms[arm_idx]["name"] if arm_idx < len(arms) else ""
        arm_color = ARM_COLORS.get(
            arms[arm_idx].get("color", "synapse_cyan") if arm_idx < len(arms) else "synapse_cyan",
            "#00d4ff",
        ).lstrip("#")
        repo_path = repo.split("/")[-1] if "/" in repo else repo
        stars_badge = f"![Stars](https://img.shields.io/github/stars/{repo}?style=flat-square&color={arm_color}&labelColor=0f1623)"
        forks_badge = f"![Forks](https://img.shields.io/github/forks/{repo}?style=flat-square&color=64748b&labelColor=0f1623)"
        arm_badge = f"![{arm_name}](https://img.shields.io/badge/{arm_name.replace(' ', '_')}-{arm_color}?style=flat-square)"
        out += f"| [{repo_path}](https://github.com/{repo}) | {desc} | {arm_badge} | {stars_badge} | {forks_badge} |\n"

    return out


def _formation_badge_url(titulo: str, inst: str, color: str, logo_color: str) -> str:
    t = titulo.replace(" ", "_").replace("&", "%26").replace("#", "").replace(".", "")
    i = inst.replace(" ", "_").replace("&", "%26") if inst else ""
    label = f"{t}-{i}" if i else t
    return (
        f"https://img.shields.io/badge/{label}-{color}"
        f"?style=flat-square&logoColor={logo_color}"
    )


def _build_formation(config: dict) -> str:
    formacao = config.get("formacao", [])
    if not formacao:
        return ""

    out = _section_header("Education & Certifications", "🎓")

    tipo_order = ["graduacao", "pos_graduacao", "mba"]
    tipo_label = {
        "graduacao": ("Bachelor's Degree", "a78bfa"),
        "pos_graduacao": ("Graduate", "00d4ff"),
        "mba": ("MBA", "ffb020"),
    }

    for tipo in tipo_order:
        items = [f for f in formacao if f.get("tipo") == tipo and f.get("status") == "concluido"]
        if not items:
            continue
        _, logo_color = tipo_label[tipo]
        for item in items:
            titulo = item.get("titulo", "")
            inst = item.get("instituicao", "")
            url = _formation_badge_url(titulo, inst, "1a2332", logo_color)
            suffix = f" — {inst}" if inst else ""
            out += f"![{titulo}]({url})  **{titulo}**{suffix}\\\n"

    return out + "\n"


def _build_contact(config: dict) -> str:
    social = config.get("social", {})
    links = []

    if social.get("linkedin"):
        links.append(
            f'<a href="https://linkedin.com/in/{social["linkedin"]}">'
            f'<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/></a>'
        )
    if social.get("github"):
        links.append(
            f'<a href="https://github.com/{social["github"]}">'
            f'<img src="https://img.shields.io/badge/GitHub-1a2332?style=for-the-badge&logo=github&logoColor=white"/></a>'
        )
    if social.get("portfolio"):
        links.append(
            f'<a href="{social["portfolio"]}">'
            f'<img src="https://img.shields.io/badge/Portfolio-ff5a03?style=for-the-badge&logo=astro&logoColor=white"/></a>'
        )
    if social.get("email"):
        links.append(
            f'<a href="mailto:{social["email"]}">'
            f'<img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white"/></a>'
        )
    if social.get("twitter"):
        links.append(
            f'<a href="https://twitter.com/{social["twitter"]}">'
            f'<img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white"/></a>'
        )

    if not links:
        return ""

    out = _section_header("Connect", "📡")
    out += '<div align="center">\n\n'
    out += " &nbsp; ".join(links)
    out += "\n\n</div>\n"
    return out


def _build_footer() -> str:
    return (
        "\n---\n\n"
        '<div align="center">\n\n'
        "<sub>🤖 This README is auto-generated every Sunday night from "
        "<a href=\"github-portfolio-data.yml\"><code>github-portfolio-data.yml</code></a>. "
        "Run <code>./generate-data.sh</code> to update locally.</sub>\n\n"
        "</div>\n"
    )


def build_readme(config: dict, stats: dict) -> str:
    """Assemble the full README.md content from config and stats."""
    sections = [
        "<!-- AUTO-GENERATED — Do not edit manually. Edit github-portfolio-data.yml instead. -->\n",
        _build_hero(config),
        _build_about(config),
        _build_tech_stack(config),
        _build_projects(config),
        _build_formation(config),
        _build_contact(config),
        _build_footer(),
    ]
    return "\n".join(s for s in sections if s)
