from flask import Flask, Response
from os import environ

import requests

from RSSService import RenjingwRSSService

ON_SCF = environ.get('ON_SCF', default='False') == 'True'

app = Flask(__name__)
@app.route('/renjingw')
def hello_world():
   return Response(rss_service.create_rss(), mimetype='application/xml') 

# 图像代理的视图函数
# @app.route('/image/<image_name>')
# def image_proxy(image_name: str):
#     # 假设图像存储在另一个服务器上
#     image_url = f'https://nwzimg.wezhan.cn/contents/sitefiles2067/10336339/images/{image_name}'  # 替换为你的图像来源 URL

#     # 发起请求获取图像内容
#     resp = requests.get(image_url, headers={'referer':'https://www.renjingw.com.cn/'})

#     # 如果请求成功，返回图像内容并设置缓存头
#     if resp.status_code == 200:
#         response = Response(
#             resp.content,
#             content_type=resp.headers['Content-Type']
#         )
        
#         # 设置缓存控制头
#         response.headers['Cache-Control'] = 'public, max-age=86400'  # 缓存一天 (86400秒)
#         response.headers['Expires'] = 'Wed, 21 Oct 2025 07:28:00 GMT'  # 设置过期时间

#         return response
#     else:
#         return "Image not found", 404

if __name__ == '__main__':
   rss_service = RenjingwRSSService()
   app.run(host='0.0.0.0',port=9000)
