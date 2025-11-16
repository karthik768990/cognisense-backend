from ..scraper import extract_visible_text_and_metadata

url_list = [
      "https://example.com",                    
    "https://www.wikipedia.org/",               
    "https://www.bbc.com/news",                 
    "https://www.reddit.com",                   
    "https://developer.mozilla.org/en-US/docs",

]

for url in url_list:
        print("testing urls : ")
        result = extract_visible_text_and_metadata(url)
        for k,v in result.items():
            if isinstance(v, str) and len(v) > 50000:
                print(f"{k}: {v[:50000]}...")  # print only first 50000 chars
            else:
                print(f"{k}: {v}")