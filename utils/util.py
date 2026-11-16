import os
import random
import string
import copy
from bs4 import BeautifulSoup
from utils.js_injector import HtmlTagHelper

def read_webpages(filename: str) -> BeautifulSoup:
    """
    Read a webpage from a file and return a BeautifulSoup object.
    """
    path = filename
    if not os.path.exists(path):
        return None
    
    try:

        with open(path, "r", errors="ignore") as file:
            content = file.read()

        return BeautifulSoup(content, "html.parser")
    
    except Exception as e:
        return None

def write_webpages(path_filename: str, html: str) -> None:
    """
    Write a BeautifulSoup object to a file.

    """

    # ensure all directories in path exist
    os.makedirs(os.path.dirname(path_filename), exist_ok=True)

    try:
        with open(path_filename, "w") as file:
            file.write(str(html))
    except Exception as e:
        pass

def plan_injection_positions(html: BeautifulSoup, tag_amount: int, tag_type: str, seed: int) -> list:
    """
    Pick tag_amount injection positions (indices into the head/body element list)
    using a seeded RNG so the positions are FIXED and can be reused across multiple
    output copies. Only the per-tag random query string varies between copies.
    """
    if tag_type in ("link", "stylesheet") and html.head is None:
        new_head = html.new_tag("head")
        if html.html is not None:
            html.html.insert(0, new_head)
        else:
            html.insert(0, new_head)

    if html.body is None:
        raise Exception("No <body> element found")

    head_elements = html.head.find_all() if html.head else []
    body_elements = html.body.find_all()
    all_elements = head_elements if tag_type in ("link", "stylesheet") else body_elements

    if not all_elements:
        return [0] * tag_amount

    rng = random.Random(seed)
    return [rng.randrange(len(all_elements)) for _ in range(tag_amount)]


def inject_with_positions(html: BeautifulSoup, attack_url: str, positions: list, tag_type: str) -> BeautifulSoup:
    """
    Inject a tag at each planned position. The injection positions stay fixed
    (so every output copy is structurally identical), but each tag gets a fresh
    random ?<string> query so the URLs differ between copies/visits.
    """
    if not (html.head and html.body):
        raise Exception("No head/body element found")

    head_elements = html.head.find_all()
    body_elements = html.body.find_all()
    all_elements = head_elements if tag_type in ("link", "stylesheet") else body_elements

    for idx in positions:
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        attack_url_copy = f"{attack_url}?{random_string}"
        tag = BeautifulSoup(HtmlTagHelper().build_tag(attack_url_copy, tag_type), "html.parser")

        if idx < len(all_elements):
            all_elements[idx].insert_after(tag)
        elif tag_type in ("link", "stylesheet"):
            html.head.append(tag)
        else:
            html.body.append(tag)

    return html


def inject_into_html(html: BeautifulSoup, attack_url: str, tag_amount: int, tag_type: str) -> BeautifulSoup:
    """
    Inject a tag with text into the HTML soup.
    """

    if tag_type in ("link", "stylesheet") and html.head is None:
        new_head = html.new_tag("head")

        if html.html is not None:
            html.html.insert(0, new_head)
        else:
            html.insert(0, new_head)
    
    if html.head and html.body:

        head_elements = html.head.find_all()
        body_elements = html.body.find_all()
        for _ in range(tag_amount):
                
            # Make attack_url unique by appending random string after ?
            attack_url_copy = copy.deepcopy(attack_url)
            random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            attack_url_copy = f"{attack_url_copy}?{random_string}"
            tag = HtmlTagHelper().build_tag(attack_url_copy, tag_type)
            tag = BeautifulSoup(tag, 'html.parser')

            # Find random place in dom
            # Check if element should be in head or body (e.g. link in head, rest in body)
            all_elements = head_elements if tag_type in ("link", "stylesheet") else body_elements
            if all_elements:
                random_element = random.choice(all_elements)
                random_element.insert_after(tag)
            else:
                if tag_type in ("link", "stylesheet") :
                    html.head.append(tag)
                else :
                    html.body.append(tag)

        # Return patched HTML
        return html

    # No head/body element found
    raise Exception("No head/body element found")


def inject_iframe_into_html(html: BeautifulSoup, attack_url: str, tag_amount: int) -> BeautifulSoup:
    """
    Inject a iframe tag with text into the HTML soup.
    """

    if html.body:

        body_elements = html.body.find_all(recursive=True)
        for i in range(tag_amount):
                
            # Make attack_url unique by appending random string after ?
            attack_url_copy = copy.deepcopy(attack_url)
            tag = HtmlTagHelper().build_tag(attack_url_copy, "iframe")
            tag = BeautifulSoup(tag, 'html.parser')

            # Find random place in dom
            # Check if element should be in head or body (e.g. link in head, rest in body)
            if body_elements:
                random_element = random.choice(body_elements)
                random_element.insert_after(tag)
            else:
                html.body.append(tag)

        # Return patched HTML
        return html

    # No head/body element found
    raise Exception("No body element found")
