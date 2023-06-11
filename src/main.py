# -*- coding: utf-8 -*-
import click
from src.core import __init__
from src.core.config import GLOBAL_CONFIG, AuthConfig
from src.core.user import login, auto_check_in
from src.core.cli import cli_handler
from src.core.websocket import init_chatroom
from src.utils.version import __version__
from src.api import API


class CliConfig(object):
    def __init__(self, username: str = '', password: str = '', code: str = '', file_path: str = None):
        self.username = username
        self.password = password
        self.code = code
        self.file_path = file_path


def run(config: CliConfig):
    __init__(API, config.file_path)
    if config.username is not None and config.password is not None:
        GLOBAL_CONFIG.auth_config = AuthConfig(
            config.username, config.password, config.code)
    login(API)
    auto_check_in(API)
    init_chatroom(API)
    cli_handler(API)

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
