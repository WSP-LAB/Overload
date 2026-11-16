import logging
import random
import string

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("experiment.log"))

class HtmlTagHelper:

    def _build_iframe_tag(self, url: str) -> str:
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe
        return f'<iframe src="{url}" style="display:none;"></iframe>'
    
    def _build_script_tag(self, url: str) -> str:
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script
        return f'<script src="{url}"></script>'
    
    def _build_img_tag(self, url: str) -> str:
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img
        return f'<img src="{url}" style="display:none;">'
    
    def _build_link_tag(self, url: str) -> str:
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link
        return f'<link href="{url}" rel="stylesheet">' 
    
    def _build_video_tag(self, url: str) -> str:
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video
        return f'<video src="{url}" style="display:none;"></video>'
    
    def _build_audio_tag(self, url: str) -> str:
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio
        return f'<audio src="{url}" style="display:none;"></audio>'
    
    def build_tag(self, url: str, tag_type: str = "") -> str:
        """
        Builds an HTML tag based on the tag type and URL.
        If tag type is not provided, the URL is returned as is.

        :param url: URL to embed in the tag
        :param tag_type: Type of the tag (iframe, script, img, link, video, audio)
        :return: HTML tag as a string
        """
        if tag_type == "iframe" or tag_type == "subdocument" or tag_type == "sub_frame":
            return self._build_iframe_tag(url)
        if tag_type == "script":
            return self._build_script_tag(url)
        if tag_type == "img" or tag_type == "image":
            return self._build_img_tag(url)
        if tag_type == "link" or tag_type == "stylesheet":
            return self._build_link_tag(url)
        if tag_type == "video":
            return self._build_video_tag(url)
        if tag_type == "audio":
            return self._build_audio_tag(url)
        if tag_type == "":
            return url
        
        # Invalid tag type
        return None

    def generate_random_domain(self, domain_length: int = 10) -> str:
        # Build random domain based on rules from https://www.nic.ag/rules.htm

        # List of valid domain extensions
        valid_extensions = ['com', 'net', 'org', 'io', 'co', 'gov', 'edu', 'biz', 'me', 'de']
    
        # Length of the domain extension (e.g., .com, .org)
        extension = random.choice(valid_extensions)  # Randomly select a valid extension
        
        # Allowed characters for the domain part (letters, digits, hyphen)
        allowed_chars = string.ascii_letters + string.digits + '-'
        
        # Ensure the domain doesn't start or end with a hyphen, and doesn't have consecutive hyphens
        while True:
            domain_name = ''.join(random.choice(allowed_chars) for _ in range(domain_length))
            
            # Ensure the domain name doesn't start or end with a hyphen and doesn't contain consecutive hyphens
            if not domain_name.startswith('-') and not domain_name.endswith('-') and '--' not in domain_name:
                break

        # Combine to form the full domain name
        return 'https://' + domain_name + '.' + extension

