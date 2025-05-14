import click
import logging
import os
import time
import yaml

from collections import defaultdict
from datetime import datetime, timedelta, timezone
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

    # create next departure index
    station_dep_index = defaultdict(lambda: None)

    while True:

        logging.info('Performing observer requests ...')

        for station_id in station_ids:

            # check if station preview time is reached
            next_departure_time = station_dep_index[station_id]
            if next_departure_time is not None and next_departure_time >= datetime.now(timezone.utc) + timedelta(minutes=5):
                logging.debug(f"Skipping station {station_id}, preview time window not reached")
                continue
            
            # run worker for this station
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

            # store next departure index
            station_dep_index[station_id] = worker.next_departure_timestamp

        time.sleep(60)
    

if __name__ == '__main__':
    cli()