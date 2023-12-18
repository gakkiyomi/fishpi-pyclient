# -*- coding: utf-8 -*-
import os
import re
from abc import ABC, abstractmethod
from typing import Tuple

from objprint import op

from src.api import FishPi, UserInfo
from src.api.article import Article
from src.api.config import GLOBAL_CONFIG, Config, init_defualt_config
from src.api.redpacket import RedPacket, RedPacketType, RPSRedPacket, SpecifyRedPacket
from src.utils import (
    COMMAND_GUIDE,
    RP_RE,
    RP_SEND_TO_CODE_RE,
    RP_TIME_CODE_RE,
    TRANSFER_RE,
)
from src.utils.file import ensure_directory_exists

from .blacklist import (
    ban_someone,
    put_keyword_to_bl,
    release_someone,
    remove_keyword_to_bl,
)
from .chatroom import ChatRoom
from .user import render_online_users, render_user_info


class Command(ABC):
    @abstractmethod
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        pass


class HelpCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        print(COMMAND_GUIDE)


class DefaultCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        curr_user = api.sockpuppets[api.current_user]
        if curr_user.ws is not None:
            if GLOBAL_CONFIG.chat_config.answer_mode:
                api.chatroom.send(
                    f"鸽 {' '.join(args)}")
            else:
                api.chatroom.send(' '.join(args))
        else:
            print("请先进入聊天室")


class EnterCil(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        curr_user = api.sockpuppets[api.current_user]
        if len(curr_user.ws) == 0:
            print("已在交互模式中")
        else:
            keys = list(curr_user.ws.keys())
            for key in keys:
                curr_user.ws[key].stop()
            print("进入交互模式")


class EnterChatroom(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        curr_user = api.sockpuppets[api.current_user]
        if ChatRoom.WS_URL in curr_user.ws:
            curr_user.ws[ChatRoom.WS_URL].stop()
        cr = ChatRoom()
        curr_user.ws[ChatRoom.WS_URL] = cr
        cr.start()


class SiGuoYa(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        api.chatroom.siguoya()


class ArticleCommand(Command):
    def __init__(self, article: Article = None) -> None:
        self.curr_article = article

    def exec(self, api: FishPi, args: Tuple[str, ...]):
        lt = [i for i in args]
        if len(lt) == 0:
            article_list = api.article.list_articles()
            api.article.format_article_list(article_list)

        elif lt[0] == "page":
            try:
                page_index = int(lt[1])
                article_list = api.article.list_articles(
                    page=page_index)
                api.article.format_article_list(article_list)
            except Exception:
                print("参数错误，#article page {int}")

        elif len(lt) > 1 and lt[0] == "view":
            try:
                article_index = int(lt[1])
                if article_index <= 0:
                    print("页数必须大于0")
                    return
                if 0 <= article_index < len(api.article.articles_oid()):
                    article = api.article.get_article(api.article.articles_oid(article_index))
                    article.get_content()
                    self.curr_article = article
                    api.article.format_comments_list(
                        article.get_articleComments())
                    print(f"\n[*** 当前帖子:{article.get_tittle()} ***]\n")

                elif len(api.article.articles_oid()) < 1:
                    article_list = api.article.list_articles()
                    api.article.format_article_list(article_list)
                    article = api.article.get_article(api.article.articles_oid(article_index))
                    article.get_content()
                    self.curr_article = article
                    api.article.format_comments_list(
                        article.get_articleComments())
                    print(f"\n[*** 当前帖子:{article.get_tittle()} ***]\n")

                else:
                    print("找不到对应编号或索引的文章")
            except Exception:
                print("参数错误，#article view {int}")

        elif len(lt) > 1 and lt[0] == "comment":
            comment_content = lt[1]

            try:
                api.article.comment_article(self.curr_article.oId, comment_content)
            except Exception:
                print("选择需要评论的帖子")


class AnswerMode(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        if GLOBAL_CONFIG.chat_config.answer_mode:
            GLOBAL_CONFIG.chat_config.answer_mode = False
            print("退出答题模式")
        else:
            GLOBAL_CONFIG.chat_config.answer_mode = True
            print("进入答题模式")


class ConfigCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        lt = [i for i in args]
        if len(lt) == 0:
            print('非法指令, 正确指令为: config [dump|show] {-d|-c} (file_path)')
            return
        it = iter(lt)
        if len(lt) < 2:
            print('非法指令, 正确指令为: config [dump|show] {-d|-c} (file_path)')
            return
        opreator = next(it)
        if opreator == 'dump':
            if len(lt) < 3:
                print('非法指令, 正确指令为: config [dump|show] {-d|-c} (file_path)')
                return
            config_option = next(it)
            try:
                export_config: Config = None
                if config_option == '-d':
                    export_config = init_defualt_config()
                elif config_option == '-c':
                    export_config = GLOBAL_CONFIG
                else:
                    print('非法指令, 正确指令为: dump config {-d|-c} file_path')
                    return
                file_path = os.path.abspath(next(it))
                ensure_directory_exists(file_path)
                with open(file_path, 'w', encoding='utf-8') as configfile:
                    export_config.to_ini_template().write(configfile)
                print(f'导出位置:{file_path}')
            except Exception as e:
                print(f'导出配置时发生错误: {e}')
        elif opreator == 'show':
            config_option = next(it)
            if config_option == '-d':
                default_config = init_defualt_config()
                op(default_config)
            elif config_option == '-c':
                op(GLOBAL_CONFIG)
            else:
                print('非法指令, 正确指令为: dump show {-d|-c}')
        else:
            print('非法指令, 更多功能敬请期待!')


class BreezemoonsCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        api.user.send_breezemoon(' '.join(args))


class CheckInCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        if api.user.checked_status()["checkedIn"]:
            print("今日你已签到！")
        else:
            print("今日还未签到，摸鱼也要努力呀！")


class OnlineUserCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        render_online_users(api)


class GetLivenessCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        print("当前活跃度: " + str(api.user.get_liveness_info()["liveness"]))


class BrushLivenessCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        articles = map(lambda article: api.article.get_article(
            article_id=article['oId']), api.article.list_articles())
        # TODO


class GetRewardCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        api.chatroom.send("小冰 去打劫")  # 魔法
        # api.user.get_yesterday_reward()


class GetPointCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        print(
            f'当前积分: {str(api.user.get_user_info(api.current_user)["userPoint"])}')


class RevokeMessageCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        if api.chatroom.last_msg_id is not None:
            api.chatroom.revoke(api.chatroom.last_msg_id)


class BlackListCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        print('小黑屋用户:' + str(GLOBAL_CONFIG.chat_config.blacklist))
        print('关键词屏蔽:' + str(GLOBAL_CONFIG.chat_config.kw_blacklist))


class BanSomeoneCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        it = (i for i in args)
        ban_type = next(it)
        if ban_type == 'keyword':
            put_keyword_to_bl(it)
        elif ban_type == 'user':
            ban_someone(api, ' '.join(it))
        else:
            print('非法指令, ban指令应该为: ban keyword|user name')


class ReleaseSomeoneCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        it = (i for i in args)
        release_type = next(it)
        if release_type == 'keyword':
            remove_keyword_to_bl(it)
        elif release_type == 'user':
            release_someone(api, ' '.join(it))
        else:
            print('非法指令, release指令应该为: release keyword|user name')


class GetUserInfoCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        userInfo = api.user.get_user_info(' '.join(args))
        if userInfo is not None:
            render_user_info(userInfo)


class ShowCurrentUserCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        print('当前用户')
        op(api.sockpuppets[api.current_user], exclude=["ws"])


class ShowSockpuppetCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        print('分身账户')
        for user in api.sockpuppets.values():
            op(user, exclude=["ws"])


class ChangeCurrentUserCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        target_user_name = " ".join(args)
        print(f'账户切换 {api.current_user} ===> {target_user_name}')
        api.sockpuppets[api.current_user].offline()
        if target_user_name in api.sockpuppets:
            api.sockpuppets[target_user_name].online(ChatRoom().start)
        else:
            print('请输入密码:')
            api_key = ''
            while len(api_key) == 0:
                password = input("")
                api.login(target_user_name, password)
                api_key = api.api_key
            GLOBAL_CONFIG.auth_config.username = target_user_name
            GLOBAL_CONFIG.auth_config.password = password
            GLOBAL_CONFIG.auth_config.key = api_key
            api.sockpuppets[target_user_name] = UserInfo(
                target_user_name, password, api_key)
            api.sockpuppets[target_user_name].online(ChatRoom().start)


class PointTransferCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        res = re.fullmatch(TRANSFER_RE, ' '.join(args))
        if res is not None:
            api.user.transfer(args[1], args[0], args[2])
        else:
            print("非法转账命令")


class RedpacketCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        res = re.fullmatch(RP_RE, ' '.join(args))
        if res is not None:
            api.chatroom.send_redpacket(
                RedPacket("那就看运气吧!", args[1],
                          args[0], RedPacketType.RANDOM)
            )
        else:
            print("非法红包指令")


class AVGRedpacketCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        res = re.fullmatch(RP_RE, ' '.join(args))
        if res is not None:
            api.chatroom.send_redpacket(
                RedPacket(
                    "不要抢,人人有份!", args[1], args[0], RedPacketType.AVERAGE
                )
            )
        else:
            print("非法红包指令")


class HBRedpacketCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        res = re.fullmatch(RP_RE, ' '.join(args))
        if res is not None:
            api.chatroom.send_redpacket(
                RedPacket(
                    "玩的就是心跳!", args[1], args[0], RedPacketType.HEARTBEAT
                )
            )
        else:
            print("非法红包指令")


class RPSRedpacketCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        res = re.fullmatch(RP_RE, ' '.join(args))
        if res is not None:
            api.chatroom.send_redpacket(
                RPSRedPacket("剪刀石头布!", args[1], args[0])
            )
        else:
            print("非法红包指令")


class RPSLimitCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        try:
            limit = args[0]
            GLOBAL_CONFIG.redpacket_config.rps_limit = int(limit)
            print(f"猜拳红包超过{limit}不抢")
        except Exception:
            print("非法红包指令")


class RedpacketTimeCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        res = re.fullmatch(RP_TIME_CODE_RE, ' '.join(args))
        if res is not None:
            time = args[0]
            GLOBAL_CONFIG.redpacket_config.rate = int(time)
            print(f"红包等待时间已设置成功 {time}s")
        else:
            print("非法红包指令")


class RedpacketToCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        res = re.fullmatch(RP_SEND_TO_CODE_RE, ' '.join(args))
        if res is not None:
            api.chatroom.send_redpacket(
                SpecifyRedPacket(
                    "听我说谢谢你,因为有你,温暖了四季!",
                    args[0],
                    args[1].replace("，", ",").split(","),
                )
            )
        else:
            print("非法红包指令")


class CLIInvoker:
    def __init__(self, api):
        self.api = api
        self.commands = {}

    def add_command(self, command_name, command):
        self.commands[command_name] = command

    def run(self):
        while True:
            msg = input("")
            params = msg.split(' ')
            if len(params) < 2 and not msg.startswith('#'):
                DefaultCommand().exec(self.api, tuple(params))
            else:
                args = tuple(params[1:])
                command = self.commands.get(params[0], DefaultCommand())
                if isinstance(command, DefaultCommand):
                    args = tuple(params)
                command.exec(self.api, args)


def init_cli(api: FishPi):
    cli_handler = CLIInvoker(api)
    help_c = HelpCommand()
    cli_handler.add_command('#', help_c)
    cli_handler.add_command('#h', help_c)
    cli_handler.add_command('#help', help_c)
    cli_handler.add_command('#cli', EnterCil())
    cli_handler.add_command('#chatroom', EnterChatroom())
    cli_handler.add_command('#siguo', SiGuoYa())
    cli_handler.add_command('#article', ArticleCommand())
    cli_handler.add_command('#bm', BreezemoonsCommand())
    cli_handler.add_command('#config', ConfigCommand())
    cli_handler.add_command('#transfer', PointTransferCommand())
    cli_handler.add_command('#answer', AnswerMode())
    cli_handler.add_command('#checked', CheckInCommand())
    cli_handler.add_command('#reward', GetRewardCommand())
    cli_handler.add_command('#revoke', RevokeMessageCommand())
    cli_handler.add_command('#liveness', GetLivenessCommand())
    cli_handler.add_command('#point', GetPointCommand())
    cli_handler.add_command('#me', ShowCurrentUserCommand())
    cli_handler.add_command('#account', ShowSockpuppetCommand())
    cli_handler.add_command('#change', ChangeCurrentUserCommand())
    cli_handler.add_command('#user', GetUserInfoCommand())
    cli_handler.add_command('#online-users', OnlineUserCommand())
    cli_handler.add_command('#blacklist', BlackListCommand())
    cli_handler.add_command('#ban', BanSomeoneCommand())
    cli_handler.add_command('#release', ReleaseSomeoneCommand())
    cli_handler.add_command('#rp', RedpacketCommand())
    cli_handler.add_command('#rp-ave', AVGRedpacketCommand())
    cli_handler.add_command('#rp-hb', HBRedpacketCommand())
    cli_handler.add_command('#rp-rps', RPSRedpacketCommand())
    cli_handler.add_command('#rp-rps-limit', RPSLimitCommand())
    cli_handler.add_command('#rp-time', RedpacketTimeCommand())
    cli_handler.add_command('#rp-to', RedpacketToCommand())
    cli_handler.run()
