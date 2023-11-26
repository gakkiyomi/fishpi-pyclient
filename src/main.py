# -*- coding: utf-8 -*-
import click

from src.api import API
from src.core import init_config
from src.core.command import init_cli
from src.core.config import CliConfig
from src.core.user import check_in, login
from src.core.websocket import init_chatroom
from src.utils.version import __version__


def run(config: CliConfig):
    init_config(API, config)
    login(API)
    check_in(API)
    init_chatroom(API)
    init_cli((API))


@click.command()
@click.version_option(__version__)
@click.option("--username", "-u", type=click.STRING, help="摸鱼派用户名")
@click.option("--password", "-p", type=click.STRING, help="密码")
@click.option("--code", "-c", type=click.STRING, help="两步验证码")
@click.option("--file_path", "-f", type=click.STRING, help="配置文件路径")
def cli(username: str, password: str, code: str, file_path: str) -> str:
    run(CliConfig(username, password, code, file_path))


if __name__ == "__main__":
    cli()
