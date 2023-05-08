# -*- coding: utf-8 -*-
import click
from api import FishPi
from core import __init__
from core.config import GLOBAL_CONFIG, AuthConfig
from core.user import login
from core.websocket import start
from utils.version import __version__


def run(params: dict):
    api = FishPi()
    __init__(api)
    if params:
        GLOBAL_CONFIG.auth_config = AuthConfig.build(params)
    login(api)
    start(api)


@click.command()
@click.version_option(__version__)
@click.option("--username", "-u", type=click.STRING, help="摸鱼派用户名")
@click.option("--password", "-p", type=click.STRING, help="密码")
@click.option("--code", "-c", type=click.STRING, help="两步验证码")
def cli(username: str, password: str, code: str) -> str:
    if username is None or password is None:
        run({})
    else:
        run({
            'username': username,
            'password': password,
            '2fa_code': code
        })


if __name__ == "__main__":
    cli()
