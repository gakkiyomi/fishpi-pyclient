# -*- coding: utf-8 -*-

import json
from enum import Enum
from typing import Any

import requests

from src.api import Base
from src.utils import UA

from .config import GLOBAL_CONFIG


class ArticleType(Enum):
    RECENT = 'recent'
    HOT = RECENT+'/hot'
    GOOD = RECENT+'/good'
    REPLY = RECENT+'/reply'


class Article(object):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        for dict in args:
            for key in dict:
                setattr(self, key, dict[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def vote(self, api) -> None:
        api.vote_for_article(self.oId)

    def thanks(self, api) -> None:
        api.thanks_for_article(self.oId)

    def comment(self, api, comment: str) -> None:
        api.comment_article(self.oId, comment)


class ArticleAPI(Base):
    oId = []
    title = []

    def vote_for_article(self, article_id: str) -> None:
        if self.api_key == '':
            return None
        resp = requests.post(
            f'{GLOBAL_CONFIG.host}/vote/up/article', headers={'User-Agent': UA}, json={
                'apiKey': self.api_key,
                'dataId': article_id
            })
        if resp.status_code == 200:
            data = json.loads(resp.text)
            if 'code' in data and data['code'] == 0:
                if data['type'] == -1:
                    print('点赞成功')
                else:
                    print('取消点赞')
            else:
                print('点赞失败: ' + data['msg'])
        else:
            print('点赞失败')

    def thanks_for_article(self, article_id: str) -> None:
        res = requests.post(f'{GLOBAL_CONFIG.host}/article/thank?articleId={article_id}', headers={'User-Agent': UA}, json={
            'apiKey': self.api_key
        })
        response = json.loads(res.text)
        if 'code' in response and response['code'] == 0:
            print('感谢文章成功')
        else:
            print('感谢文章失败: ' + response['msg'])

    def list_articles(self, type: ArticleType = ArticleType.RECENT, page: int = 1, size: int = 20) -> dict:
        res = requests.get(
            f'{GLOBAL_CONFIG.host}/api/articles/{type.value}?p={page}&size={size}', headers={'User-Agent': UA}, json={
                'apiKey': self.api_key
            })
        response = json.loads(res.text)
        if 'code' in response and response['code'] == 0:
            return response
        else:
            print('获取帖子列表失败: ' + response['msg'])

    def get_article(self, article_id: str) -> Article:
        res = requests.get(
            f'{GLOBAL_CONFIG.host}/api/article/{article_id}', headers={'User-Agent': UA}, json={
                'apiKey': self.api_key
            })
        response = json.loads(res.text)
        if 'code' in response and response['code'] == 0:
            # print(Article(response['data']))
            return Article(response['data'])
        else:
            print('获取帖子详情失败: ' + response['msg'])

    def get_content(self, article_id: str) -> None:
        all_content = self.get_article(article_id).article
        print("\n"+all_content["articleOriginalContent"])

    def get_author(self, article_id: str) -> str:
        all_content = self.get_article(article_id).article
        author_name = all_content["articleAuthor"].get("userNickname", "")
        return author_name if author_name != '' else all_content["articleAuthor"]["userName"]

    def format_article_list(self, article_list: list) -> None:
        grey_highlight = '\033[1;30;1m'
        green_bold = '\033[1;32;1m'
        reset_color = '\033[0m'

        formatted_articles = []

        for index, article in enumerate(article_list):
            author_name = article["articleAuthor"].get("userNickname", "")
            author_name = author_name if author_name != "" else article["articleAuthor"]["userName"]
            colored_name = f'{grey_highlight}{author_name}{reset_color}'
            colored_comments = f'{green_bold}{article["articleCommentCount"]}{reset_color}'
            self.oId.append(article["oId"])
            formatted_article = f'{str(index + 1).zfill(2)}.[{colored_name}] {article["articleTitle"]} {colored_comments}'
            self.title.append(formatted_article)
            formatted_articles.append(formatted_article)
            print(formatted_article)

    def comment_article(self, article_id: str, comment: str) -> Article:
        res = requests.post(f'{GLOBAL_CONFIG.host}/comment/{article_id}', headers={'User-Agent': UA}, json={
            'apiKey': self.api_key,
            'articleId': article_id,
            'commentAnonymous': False,
            'commentVisible': False,
            'commentContent': comment
        })
        response = json.loads(res.text)
        if 'code' in response and response['code'] == 0:
            print('评论成功')
        else:
            print('评论失败: ' + response['msg'])
