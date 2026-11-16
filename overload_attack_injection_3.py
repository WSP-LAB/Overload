import argparse
import concurrent.futures
import copy
import logging
import os
from typing import Optional

from bs4 import BeautifulSoup

from utils.util import inject_iframe_into_html, read_webpages, write_webpages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("overload_attack_injection_3.log"))

WORKING_DIR = "websites"
MAX_WORKERS = min(32, (os.cpu_count() or 1) + 4)


def inject_attack(
    html: BeautifulSoup,
    tag_amount: int,
    domain: str,
) -> Optional[BeautifulSoup]:
    """
    Inject tag_amount iframes with about:blank into a copy of the given BeautifulSoup HTML.

    Returns:
        BeautifulSoup if successful, otherwise None.
    """
    if html is None:
        logger.error(f"[{domain}] html is None")
        return None

    injected_html = copy.deepcopy(html)

    try:
        injected_html = inject_iframe_into_html(injected_html, "about:blank", tag_amount)
        return injected_html
    except Exception as e:
        logger.error(f"[{domain}] Error injecting (tags={tag_amount}): {e}")
        return None


def process_webpage(
    filename: str,
    tag_amount: int,
) -> None:
    """
    Read one HTML file, inject tags, then write the output file.
    """
    html = read_webpages(filename)
    if html is None:
        logger.error(f"Failed to read {filename}")
        return

    website_name = filename.split(".")[0]

    logger.info(f"Injecting Attack III tags into {website_name}...")

    out_path = f"{website_name}_attack_III.html"
    if os.path.exists(out_path):
        logger.info(f"File {out_path} already exists, skipping.")
        return

    injected = inject_attack(
        html=html,
        tag_amount=tag_amount,
        domain=website_name,
    )

    if injected is None:
        logger.error(f"[{website_name}] Injection failed.")
        return

    write_webpages(out_path, injected)
    logger.info(f"[{website_name}] Wrote injected HTML -> {out_path}")


def load_filenames_from_domain_file(input_file: str) -> list:
    """
    Read input_file and convert each line into a full filepath under working_dir/.
    """
    if not os.path.exists(input_file):
        logger.error(f"No domain file: {input_file}")
        return []

    with open(input_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    filenames = [os.path.join(WORKING_DIR, line) for line in lines]
    logger.info(f"Read {len(filenames)} files from {input_file}.")
    return filenames


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input file path")
    parser.add_argument("--tag_amount", type=int, default=300, help="Total number of tags to inject")
    args = parser.parse_args()

    filenames = load_filenames_from_domain_file(args.input)
    if not filenames:
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(process_webpage, fn, args.tag_amount)
            for fn in filenames
        ]
        for fut in concurrent.futures.as_completed(futures):
            fut.result()

if __name__ == "__main__":
    main()
