"""국내 언론사 RSS 피드에서 이상치 발생 시점 전후의 관련 기사를 찾는다.

네이버 뉴스 검색 API가 현재 신규 발급을 막아둔 상태라, 별도 인증키 없이
쓸 수 있는 언론사 공개 RSS로 대체했다. 저작권을 고려해 기사 본문은 저장하지
않고 제목·링크만 보관한다 (연합뉴스 RSS는 "AI 학습 및 활용 금지" 조항이
있어 제외).

한계: RSS는 최근 1~2일치 기사만 제공하므로, 방금 발생한 이상치의 원인
조사에는 쓸 수 있지만 과거(예: 몇 년 전) 이상치의 원인 뉴스를 찾는 데는
쓸 수 없다. 과거 이상치까지 다루려면 별도 뉴스 아카이브 연동이 필요하다.
"""

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx

from app.core.time import KST

DEFAULT_FEEDS = [
    "https://rss.donga.com/national.xml",
    "https://www.khan.co.kr/rss/rssdata/total_news.xml",
    "https://www.chosun.com/arc/outboundfeeds/rss/category/national/?outputType=xml",
    "https://www.seoul.co.kr/xml/rss/rss_society.xml",
    "https://www.mk.co.kr/rss/30200030/",
    "https://www.hani.co.kr/rss",
]


class RssNewsClient:
    def __init__(self, feeds: list[str] | None = None):
        self.feeds = feeds or DEFAULT_FEEDS

    async def search(
        self, keywords: list[str], around: datetime, window_days: int = 2
    ) -> list[dict]:
        if around.tzinfo is None:
            # observed_at은 KST wall-clock 기준 naive datetime
            around = around.replace(tzinfo=KST)
        start = around - timedelta(days=window_days)
        end = around + timedelta(days=window_days)

        matches: list[dict] = []
        async with httpx.AsyncClient(timeout=15) as client:
            for feed_url in self.feeds:
                try:
                    resp = await client.get(feed_url)
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue
                matches.extend(self._parse_feed(resp.content, keywords, start, end))
        return matches

    @staticmethod
    def _parse_feed(
        xml_bytes: bytes, keywords: list[str], start: datetime, end: datetime
    ) -> list[dict]:
        root = ElementTree.fromstring(xml_bytes)
        results = []
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub_date_raw = item.findtext("pubDate")
            if not title or not pub_date_raw:
                continue
            try:
                pub_date = parsedate_to_datetime(pub_date_raw)
            except (TypeError, ValueError):
                continue
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            if not (start <= pub_date <= end):
                continue
            if keywords and not any(kw in title for kw in keywords):
                continue
            results.append(
                {"title": title, "link": link, "published_at": pub_date.isoformat()}
            )
        return results
