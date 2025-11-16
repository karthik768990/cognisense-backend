from bs4 import BeautifulSoup
import requests
from datetime import datetime
import tldextract

def extract_visible_text_and_metadata(url: str) -> dict:
    '''Only for the visible content of the websites'''

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        html_code = response.text
        soup = BeautifulSoup(html_code, "lxml")

        for tag in soup(["script", "style", "noscript", "svg", "video", "img", "iframe", "header", "footer"]):
            tag.decompose()


        visible_text = " ".join(soup.stripped_strings)
        cleaned_text = " ".join(visible_text.split())

        title = soup.title.string.strip() if soup.title and soup.title.string else None
        meta_desc, meta_keywords, meta_author = None, None, None


        for meta in soup.find_all("meta"):
            if meta.get("name") == "description":
                meta_desc = meta.get("content", "").strip()
            elif meta.get("name") == "keywords":
                meta_keywords = meta.get("content", "").strip()
            elif meta.get("name") == "author":
                meta_author = meta.get("content", "").strip()

        domain_parts = tldextract.extract(url)
        domain_name = f"{domain_parts.domain}.{domain_parts.suffix}"

        data = {
            "url": url,
            "domain": domain_name,
            "title": title,
            "meta_description": meta_desc,
            "meta_keywords": meta_keywords,
            "meta_author": meta_author,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "text_length": len(cleaned_text),
            "visible_text": cleaned_text[:3000] + ("..." if len(cleaned_text) > 3000 else "")
        }

        return data

    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    


    ##TODO Should add the onTabClose and onTabOpen and onTabreload action listeners in the frontend 
