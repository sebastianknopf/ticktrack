import click
import logging
import os
import time
import yaml

from sqlobject import connectionForURI, sqlhub
from typing import List

from ticktrack.config import Configuration
from ticktrack.model import MonitoredTrip
from ticktrack.worker import MonitorWorker
from ticktrack.version import __version__


logging.basicConfig(
    level=logging.INFO, 
    format= '[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

@click.group()
def cli():
    pass

@cli.command()
def version():
    print(__version__)

@cli.command()
@click.argument('database')
@click.argument('config')
def observe(database, config):

    # load config and set default values
    with open(config, 'r') as config_file:
        config = yaml.safe_load(config_file)

    config = Configuration.default_config(config)

    # init database tables
    database = os.path.join(os.getcwd(), database)
    sqlhub.processConnection = connectionForURI(f"sqlite:///{database}")

    MonitoredTrip.createTable(ifNotExists=True)

    # start monitor thread for each station ID
    station_ids: List[str] = [s.strip() for s in config['stations']]

    while True:

        logging.info('Performing observer requests ...')

        for station_id in station_ids:
            worker: MonitorWorker = MonitorWorker(
                database,
                config['app']['endpoint'], 
                config['app']['api_key'], 
                './datalog' if config['app']['datalog_enabled'] else None,
            )

            if not len(config['lines']) == 0:
                worker.start(station_id, [l.strip() for l in config['lines']])
            else:
                worker.start(station_id, None)

        time.sleep(60)
    

if __name__ == '__main__':
    cli()