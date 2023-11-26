# -*- coding: utf-8 -*-
import re
from abc import ABC, abstractmethod
from typing import Tuple

from src.api import FishPi
from src.api.redpacket import RedPacket, RedPacketType, RPSRedPacket, SpecifyRedPacket
from src.utils.utils import (
    COMMAND_GUIDE,
    RP_RE,
    RP_SEND_TO_CODE_RE,
    RP_TIME_CODE_RE,
    TRANSFER_RE,
)

from .blacklist import ban_someone, release_someone
from .config import GLOBAL_CONFIG
from .user import render_online_users, render_user_info
from .websocket import chatroom_out, init_chatroom


class Command(ABC):
    @abstractmethod
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        pass


class HelpCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        print(COMMAND_GUIDE)


class DefaultCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        if api.ws is not None:
            if GLOBAL_CONFIG.chat_config.answer_mode:
                api.chatroom.send(
                    f"鸽 {' '.join(args)}")
            else:
                api.chatroom.send(' '.join(args))
        else:
            print("请先进入聊天室")


class EnterCil(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        if api.ws is None:
            print("已经进入交互模式了")
        else:
            chatroom_out(api)
            print("进入交互模式")


class EnterChatroom(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        if api.ws is None:
            init_chatroom(api)
        else:
            chatroom_out(api)
            init_chatroom(api)


class AnswerMode(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        if GLOBAL_CONFIG.chat_config.answer_mode:
            GLOBAL_CONFIG.chat_config.answer_mode = False
            print("退出答题模式")
        else:
            GLOBAL_CONFIG.chat_config.answer_mode = True
            print("进入答题模式")


class GetAPIKey(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        print(api.api_key)


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


class GetRewardCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        api.user.get_yesterday_reward()


class GetPointCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        print(
            "当前积分: " + str(api.user.get_user_info(GLOBAL_CONFIG.auth_config.username)["userPoint"]))


class BlackListCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        print(GLOBAL_CONFIG.chat_config.blacklist)


class BanSomeoneCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        ban_someone(api, ' '.join(args))


class ReleaseSomeoneCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        release_someone(api, ' '.join(args))


class GetUserInfoCommand(Command):
    def exec(self, api: FishPi, args: Tuple[str, ...]):
        userInfo = api.user.get_user_info(' '.join(args))
        if userInfo is not None:
            render_user_info(userInfo)


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
    cli_handler.add_command('#bm', BreezemoonsCommand())
    cli_handler.add_command('#api-key', GetAPIKey())
    cli_handler.add_command('#transfer', PointTransferCommand())
    cli_handler.add_command('#answer', AnswerMode())
    cli_handler.add_command('#checked', CheckInCommand())
    cli_handler.add_command('#reward', GetRewardCommand())
    cli_handler.add_command('#liveness', GetLivenessCommand())
    cli_handler.add_command('#point', GetPointCommand())
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
