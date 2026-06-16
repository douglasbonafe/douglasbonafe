"""Entry point for the Douglas Bonafé Galaxy Portfolio generator."""

import argparse
import logging
import os
import sys

import requests
import yaml

from generator.config import ConfigError, validate_config
from generator.github_api import GitHubAPI
from generator.svg_builder import SVGBuilder
from generator.readme_builder import build_readme

logger = logging.getLogger(__name__)

DEMO_STATS = {"commits": 2400, "stars": 128, "prs": 310, "issues": 45, "repos": 24}
DEMO_LANGUAGES = {
    "TypeScript": 520000,
    "Python": 410000,
    "Java": 180000,
    "C#": 140000,
    "Go": 95000,
    "JavaScript": 75000,
    "Shell": 35000,
    "Vue": 25000,
}

CONFIG_FILE = "github-portfolio-data.yml"


def generate(args):
    """Generate SVGs and README from github-portfolio-data.yml."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    demo = getattr(args, "demo", False)
    repo_root = os.path.join(os.path.dirname(__file__), "..")
    config_path = os.path.join(repo_root, CONFIG_FILE)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("%s not found. Expected at repo root.", CONFIG_FILE)
        sys.exit(1)

    try:
        config = validate_config(config)
    except ConfigError as e:
        logger.error("Config invalido: %s", e)
        sys.exit(1)

    username = config["username"]
    logger.info("Gerando portfolio para @%s...", username)

    if demo:
        logger.info("Modo demo: usando dados hardcoded (sem chamadas a API).")
        stats = DEMO_STATS
        languages = DEMO_LANGUAGES
    else:
        api = GitHubAPI(username)

        logger.info("Buscando stats do GitHub...")
        try:
            stats = api.fetch_stats()
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            logger.warning("Erro ao buscar stats (%s). Usando zeros.", e)
            stats = {"commits": 0, "stars": 0, "prs": 0, "issues": 0, "repos": 0}

        logger.info("Buscando linguagens...")
        try:
            languages = api.fetch_languages()
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            logger.warning("Erro ao buscar linguagens (%s). Usando vazio.", e)
            languages = {}

    logger.info("Stats: %s", stats)
    logger.info("Linguagens: %d encontradas", len(languages))

    builder = SVGBuilder(config, stats, languages)
    output_dir = os.path.join(repo_root, "assets", "generated")
    os.makedirs(output_dir, exist_ok=True)

    svgs = {
        "galaxy-header.svg": builder.render_galaxy_header(),
        "stats-card.svg": builder.render_stats_card(),
        "tech-stack.svg": builder.render_tech_stack(),
        "projects-constellation.svg": builder.render_projects_constellation(),
    }

    for filename, content in svgs.items():
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("SVG gerado: %s", path)

    readme_path = os.path.join(repo_root, "README.md")
    readme_content = build_readme(config, stats)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    logger.info("README.md gerado: %s", readme_path)

    logger.info("Concluido! 4 SVGs + README.md gerados.")


def main():
    parser = argparse.ArgumentParser(
        description="Douglas Bonafe Galaxy Portfolio Generator"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Gera com dados de demonstracao (sem chamadas a API do GitHub)",
    )
    args = parser.parse_args()
    generate(args)


if __name__ == "__main__":
    main()
