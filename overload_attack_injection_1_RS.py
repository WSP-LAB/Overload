import argparse
import concurrent.futures
import copy
import logging
import os
import random
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup

from utils.attack import OverloadUrlBuilder
from utils.js_injector import HtmlTagHelper
from utils.util import (
    inject_with_positions,
    plan_injection_positions,
    read_webpages,
    write_webpages,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("overload_attack_injection_1_RS.log"))

WORKING_DIR = "websites"
MAX_WORKERS = min(32, (os.cpu_count() or 1) + 4)

# One planned injection: (attack_url, tag_type, fixed positions).
InjectionPlan = List[Tuple[str, str, List[int]]]


def build_injection_plan(
    html: BeautifulSoup,
    random_domain: str,
    url_len: int,
    tag_amount: int,
    domain: str,
    ratio: float,
    seed: int,
) -> Optional[InjectionPlan]:
    """
    Plan the fixed injection once: split tag_amount by ratio between the adblock
    and ubo targets. RS builds many (url, type) pairs (one tag each); each gets a
    fixed position. The same plan is reused for every visit copy, so positions
    never change and only the per-tag random query string differs between copies.
    """
    if html is None:
        logger.error(f"[{domain}] html is None")
        return None

    first = int(tag_amount * ratio)
    second = tag_amount - first

    plan: InjectionPlan = []
    pos_idx = 0
    for target, count in (("adblock", first), ("ubo", second)):
        if count <= 0:
            continue
        try:
            att = OverloadUrlBuilder(target)
            result = att.attack(random_domain, count, url_len, is_gs=False)
            for attack_url, elem_type in result:
                positions = plan_injection_positions(html, 1, elem_type, seed + pos_idx)
                plan.append((attack_url, elem_type, positions))
                pos_idx += 1
        except Exception as e:
            logger.error(f"[{domain}] Error planning RS (target={target}, url_len={url_len}, tags={count}): {e}")
            return None

    return plan


def render_copy(html: BeautifulSoup, plan: InjectionPlan, domain: str) -> Optional[BeautifulSoup]:
    """
    Produce one injected copy from a fixed plan: same positions, fresh random URLs.
    """
    injected = copy.deepcopy(html)
    for attack_url, elem_type, positions in plan:
        try:
            injected = inject_with_positions(injected, attack_url, positions, elem_type)
        except Exception as e:
            logger.error(f"[{domain}] Error injecting RS copy: {e}")
            return None
    return injected


def process_webpage(
    filename: str,
    url_len: int,
    tag_amount: int,
    ratio: float,
    visit_count: int,
) -> None:
    """
    Read one HTML file, plan the injection once, then write `visit_count` output
    copies named {website}_attack_I_rs_{i}.html. Every copy shares the same
    injection positions; only the per-tag random URL string differs between copies.
    """
    html = read_webpages(filename)
    if html is None:
        logger.error(f"Failed to read {filename}")
        return

    website_name = filename.split(".")[0]

    logger.info(f"Injecting RS tags into {website_name} ({visit_count} copies)...")

    # Example: https://ntmudUH9ap.com
    random_domain = HtmlTagHelper().generate_random_domain(10)
    seed = random.randint(0, 10**9)

    plan = build_injection_plan(
        html=html,
        random_domain=random_domain,
        url_len=url_len,
        tag_amount=tag_amount,
        domain=website_name,
        ratio=ratio,
        seed=seed,
    )
    if plan is None:
        logger.error(f"[{website_name}] Injection planning failed.")
        return

    for i in range(visit_count):
        out_path = f"{website_name}_attack_I_rs_{i}.html"
        if os.path.exists(out_path):
            logger.info(f"File {out_path} already exists, skipping.")
            continue

        injected = render_copy(html, plan, website_name)
        if injected is None:
            logger.error(f"[{website_name}] Injection failed for copy {i}.")
            continue

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
    parser.add_argument("--tag_amount", type=int, default=150, help="Total number of tags to inject")
    parser.add_argument("--url_len", type=int, default=10000, help="Length of overload URL")
    parser.add_argument("--ratio", type=float, default=0.5, help="Fraction for first injection (adblock)")
    parser.add_argument("--visit-count", type=int, default=5, help="Number of per-visit copies to generate (_0.html .. _{N-1}.html)")
    args = parser.parse_args()

    if not (0.0 <= args.ratio <= 1.0):
        logger.error(f"Invalid --ratio {args.ratio}. Must be between 0 and 1.")

    filenames = load_filenames_from_domain_file(args.input)
    if not filenames:
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(process_webpage, fn, args.url_len, args.tag_amount, args.ratio, args.visit_count)
            for fn in filenames
        ]
        for fut in concurrent.futures.as_completed(futures):
            fut.result()

if __name__ == "__main__":
    main()
