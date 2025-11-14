thonpython
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import quote_plus

class BingParser:
    def __init__(self, base_url: str, count: int, market: str, lang: str):
        self.base_url = base_url.rstrip("/")
        self.count = count
        self.market = market
        self.lang = lang

    def _build_url(self, keyword: str, page_number: int):
        offset = (page_number - 1) * self.count
        q = quote_plus(keyword)
        return f"{self.base_url}?q={q}&setmkt={self.market}&setLang={self.lang}&count={self.count}&first={offset}"

    def scrape(self, keyword: str, page_number: int = 1):
        url = self._build_url(keyword, page_number)
        logging.info(f"Fetching URL: {url}")

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        return {
            "url": url,
            "keyword": keyword,
            "pageNumber": page_number,
            "topBorders": self._parse_top_borders(soup),
            "news": self._parse_news(soup),
            "images": self._parse_images(soup),
            "videos": self._parse_videos(soup),
            "pages": self._parse_pages(soup),
            "explore": self._parse_explore(soup),
            "related": self._parse_related(soup),
        }

    def _parse_top_borders(self, soup):
        borders = []
        items = soup.select(".b_topBorder .b_title")
        for itm in items:
            title = itm.get_text(strip=True)
            desc_tag = itm.find_next("p")
            url_tag = itm.find("a")
            borders.append({
                "type": "topborder",
                "title": title,
                "description": desc_tag.get_text(strip=True) if desc_tag else "",
                "url": url_tag["href"] if url_tag and url_tag.has_attr("href") else ""
            })
        return borders

    def _parse_news(self, soup):
        news = []
        blocks = soup.select(".newsitem")
        for blk in blocks:
            title_el = blk.select_one(".title")
            desc_el = blk.select_one(".snippet")
            link_el = blk.find("a")
            news.append({
                "title": title_el.get_text(strip=True) if title_el else "",
                "description": desc_el.get_text(strip=True) if desc_el else "",
                "url": link_el["href"] if link_el and link_el.has_attr("href") else ""
            })
        return news

    def _parse_images(self, soup):
        images = []
        imgs = soup.select(".imgpt a.iusc")
        for img in imgs:
            meta = img.get("m")
            if meta:
                try:
                    import json
                    data = json.loads(meta)
                    images.append({
                        "url": data.get("murl", ""),
                        "description": data.get("t", "")
                    })
                except Exception:
                    continue
        return images

    def _parse_videos(self, soup):
        videos = []
        vids = soup.select(".mc_vtvc.b_prominentThumbnail video, .mc_vtvc a")
        for v in vids:
            title = v.get("title") or v.get_text(strip=True)
            videos.append({
                "url": v.get("href", ""),
                "title": title,
                "provider": "Unknown",
                "views": "",
                "channel": "",
                "date": ""
            })
        return videos

    def _parse_pages(self, soup):
        pages = []
        results = soup.select(".b_algo")
        for r in results:
            title_el = r.select_one("h2")
            link_el = title_el.find("a") if title_el else None
            desc_el = r.select_one(".b_caption p")
            pages.append({
                "title": title_el.get_text(strip=True) if title_el else "",
                "link": link_el["href"] if link_el and link_el.has_attr("href") else "",
                "desc": desc_el.get_text(strip=True) if desc_el else ""
            })
        return pages

    def _parse_explore(self, soup):
        explore = []
        cards = soup.select(".ans_nws_card .title")
        for c in cards:
            img_el = c.find_previous("img")
            explore.append({
                "title": c.get_text(strip=True),
                "imgUrl": img_el["src"] if img_el and img_el.has_attr("src") else ""
            })
        return explore

    def _parse_related(self, soup):
        related = []
        items = soup.select(".b_rs ul li a")
        for itm in items:
            related.append({
                "text": itm.get_text(strip=True),
                "url": itm["href"] if itm.has_attr("href") else ""
            })
        return related