# -*- coding: utf-8 -*-
import os
import click
import logging
from .config import Config
from .exchange import Poloniex
from .cointrader import Cointrader
from .strategy import InteractivStrategyWrapper
from .strategies.trend import Followtrend

log = logging.getLogger(__name__)
CONFIG = ".cointrader"


def get_path_to_config():
    env = os.getenv("HOME")
    return os.path.join(env, CONFIG)


def setup_logging(level):
    if level == "INFO":
        logging.basicConfig(level=logging.INFO)
    elif level == "DEBUG":
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)


class Context(object):

    """Docstring for Context. """

    def __init__(self):
        self.exchange = None


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.option("--config", help="Configuration File for cointrader.", type=click.File("r"))
@click.option("--log-level", help="Loglevel.", default="ERROR")
@pass_context
def main(ctx, config, log_level):
    """Console script for cointrader on the Poloniex exchange"""
    setup_logging(log_level)
    if config:
        config = Config(config)
    else:
        config = Config(open(get_path_to_config(), "r"))
    ctx.exchange = Poloniex(config)


@click.command()
@click.argument("market")
@click.option("--resolution", help="Resolution of the chart which is used for trend analysis", default="30m")
@click.option("--timeframe", help="Timeframe of the chart which is used for trend analysis", default="1d")
@click.option("--automatic", help="Start cointrader in automatic mode.", is_flag=True)
@pass_context
def start(ctx, market, interval, resolution, timeframe, automatic):
    """Start a new bot on the given market"""
    # balance = ctx.exchange.get_balance("BTC")
    # btc = balance["btc_value"]

    # # Calculate position to trade:
    # trade_btc = btc * position
    # trade_dollar = ctx.exchange.btc2dollar(trade_btc)
    # log.debug("Will trade {}BTC / {}$ ({}%) out of total {}BTC".format(trade_btc, trade_dollar, position, btc))

    market = ctx.exchange.get_market(market)
    strategy = Followtrend()
    if not automatic:
        interval = 0  # Disable waiting in interactive mode
        strategy = InteractivStrategyWrapper(strategy)
    else:
        interval = ctx.exchange.resolution2seconds(resolution)
    bot = Cointrader(market, strategy, resolution, timeframe)
    bot.start(interval)


main.add_command(start)

if __name__ == "__main__":
    main()
