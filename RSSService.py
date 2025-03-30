from datetime import datetime
from RenjingwSource import GetArticleListItem, RenjingwSource
import SqliteKV
import time
import PyRSS2Gen as rss
import SqliteKV
from threading import Thread

source = RenjingwSource()
kv = SqliteKV.SQLiteKV('db.db')

# 最多只拉取100篇文章
PAGE_THRESHOLD = 10

class RenjingwRSSService:
    def __init__(self):
        update_process = Thread(target=self.__worker_thread)
        update_process.start()
    
    def __worker_thread(self):
        while True:
            self.__do_update()
            time.sleep(3600)

    def __do_update(self):
        print('start update...')
        all_articles: list[rss.RSSItem] = kv.get('all_articles') or []

        for new_rss_item in self.__do_fetch():
            print(f'append {new_rss_item.guid}')
            all_articles.append(new_rss_item)
            all_articles = list({v.guid: v for v in all_articles}.values())
            all_articles.sort(key = lambda v: v.pubDate, reverse=True)
            all_articles = all_articles[:500]
            kv.set('all_articles', all_articles)
    
    def __do_fetch(self):
        latest_article_id : str = kv.get('latest_article_id') or ''
        
        first_article = None
        for i in range(1, PAGE_THRESHOLD + 1):
            time.sleep(1)
            article_list = source.fetch_list(i)
            if not first_article:
                if not article_list: return
                first_article = article_list[0]
            for article in article_list:
                if article['Id'] == latest_article_id:
                    kv.set('latest_article_id', first_article['Id'])
                    return
                yield self.__to_rss_item(article)
        kv.set('latest_article_id', first_article['Id'])

    def __get_article_content(self, article_id: int) -> str:
        key = f'article:{article_id}'
        if res := kv.get(key):
            return res
        res = source.get_article_content(article_id)
        kv.set(key, res)
        return res

    def __to_rss_item(self, item: GetArticleListItem) -> rss.RSSItem:
        real_link = f'https://www.renjingw.com.cn/{item["LinkUrl"].strip("/")}'
        res = rss.RSSItem(
            title=item['Name'],
            link=real_link,
            description=self.__get_article_content(item['Id']),
            categories=[item['CategoryName']],
            guid=str(item['Id']),
            pubDate=datetime.strptime(f'{item["QTime"]}+0000', '%Y-%m-%d %H:%M:%S%z'),
        )
        print(f'fetch {item["Id"]} success')
        return res
    
    def create_rss(self):
        rss_feed = rss.RSS2(
            title="人境网",
            link="https://www.renjingw.com.cn",
            description="传承红色经典，弘扬革命文化",
            items = kv.get('all_articles') or []
            # items=[
            #     self.fetch_content(item) for item in source.fetch_list()
            # ]
        )
        return rss_feed.to_xml('utf-8')


if __name__ == '__main__': 
    service = RenjingwRSSService()