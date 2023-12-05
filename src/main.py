# -*- coding: utf-8 -*-
import signal
import sys

import click
import schedule

from src.api import API
from src.api.config import CliOptions
from src.core import FishPiInitor
from src.utils.version import __version__


def run(options: CliOptions):
    FishPiInitor(api=API, options=options)


@click.command()
@click.version_option(__version__)
@click.option("--username", "-u", type=click.STRING, help="摸鱼派用户名")
@click.option("--password", "-p", type=click.STRING, help="密码")
@click.option("--code", "-c", type=click.STRING, help="两步验证码")
@click.option("--file_path", "-f", type=click.STRING, help="配置文件路径")
@click.option("--host", "-h", type=click.STRING, help="配置域名")
def cli(username: str, password: str, code: str, file_path: str, host: str) -> str:
    run(CliOptions(username, password, code, file_path, host))


def signal_handler(sig, frame):
    schedule.clear()
    for user in API.sockpuppets.values():
        keys = list(user.ws.keys())
        for key in keys:
            user.ws[key].stop()
    print("\n收到 Ctrl+C 信号，程序即将退出...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    cli()
