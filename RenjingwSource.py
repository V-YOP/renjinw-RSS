from pathlib import Path
from typing import List, Optional, TypedDict
import requests
from datetime import datetime
from bs4 import BeautifulSoup

class GetArticleListItem(TypedDict):
    # 类别名称，如"写作营"
    CategoryName: str
    # 新闻ID
    Id: int
    # 新闻标题
    Name: str
    # 短描述，可能为空字符串
    Short: str
    # 价格信息，可能为空字符串
    Price: str
    # 点击数
    Hits: int
    # 图片URL
    PicUrl: str
    # 链接URL
    LinkUrl: str
    # 发布时间
    QTime: str
    # 目标字段，可能为None
    Target: Optional[str]
    # 缩略图URL，可能为None
    ThumbnailUrl: Optional[str]
    # 链接类型，可能为None
    LinkType: Optional[str]
    # 实体ID，可能为None
    EntityId: Optional[int]

class RenjingwSource:
    def fetch_list(self, page_index = 1, page_size = 10) -> List[GetArticleListItem]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.renjingw.com.cn',
            'Origin': 'https://www.renjingw.com.cn',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Priority': 'u=4',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }

        data = {
            'dataType': 'news',
            'pageIndex': page_index,
            'pageSize': page_size,
            'dateFormater': 'yyyy-MM-dd HH:mm:ss',
            'orderByField': 'createtime',
            'orderByType': 'desc',
            'postData': '',
            'es': 'false',
        }
        response = requests.post('https://www.renjingw.com.cn/Designer/Common/GetData',  headers=headers, data=data)
        if response.status_code != 200 or not response.json()['IsSuccess']:
            raise RuntimeError("call GetData failed", response.text)
        return response.json()['Data']

    def get_article_content(self, article_id: int) -> str:
        import requests

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://www.renjingw.com.cn/',
            'Sec-Fetch-Dest': 'script',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }

        article_response = requests.get(
            f'https://www.renjingw.com.cn/newsinfo/{article_id}.html',
            params={},
            headers=headers,
        )
        article_response.raise_for_status()
        article_meta = BeautifulSoup(article_response.text, 'html')
        body_js_url = next(article_meta.select_one('#smart-body').children)['src']

        response = requests.get(
            body_js_url,
            params={},
            headers=headers,
        )

        if response.status_code != 200:
            raise RuntimeError(f'get news {article_id} failed', response.text)

        import json
        text: str = response.text
        text = text.removeprefix('document.write(\'')
        text = text.removesuffix('\'')
        text = f'"{text}"'
        text = json.loads(text).strip()
        soup = BeautifulSoup(text, 'html')

        # redirect img for refer
        # for img in soup.select('img'):
        #     if img.attrs['src'].startswith('//nwzimg.wezhan.cn/contents/sitefiles2067/10336339/images/'):
        #         img.attrs['src'] = f'/image/{img.attrs['src'].removeprefix('//nwzimg.wezhan.cn/contents/sitefiles2067/10336339/images/')}'

        if not (article_content := soup.select_one('.w-detail')):
            raise RuntimeError(f'news {article_id} parse failed', text)

        return article_content.prettify()
