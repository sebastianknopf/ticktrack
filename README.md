# Ticktrack
Python client for monitoring and logging of realtime data in passenger information systems using [VDV431](https://github.com/VDVde/TRIAS) interface. 

## Purpose & Usage
Ticktrack is a simple tool to monitor departures and the availability of realtime data. Each trip detected is logged to a SQLite database which can be used for analyzing problems and behind the generation of realtime data. Following questions can be answered using those data:

- Which lines have a good or less realtime coverage?
- Are there some trips which have no realtime data available for several days?
- How is the realtime coverage over some lines in the past 5 days?

To collect the data, the ticktrack client performs StopEventRequests periodically for each configured station ID and adds an entry for each unique trip per operation day. 

Everythin results in a table with the following structure:

| Column                  | Type   | Description                | Comment
|-------------------------|------------|------------------------------|---|
| id                      | INTEGER    | Primary Key, AutoID     |    |
| operation_day           | TEXT       | Operation Day (YYYY-MM-DD)  ||
| trip_id                 | TEXT       | Trip-ID                     ||
| line_id                 | TEXT       | Line-ID                     ||
| line_name               | TEXT       | Line Name                   ||
| origin_stop_id          | TEXT       | Start Station ID            ||
| origin_name             | TEXT       | Start Station Name          ||
| destination_stop_id     | TEXT       | Destination Station ID      ||
| destination_name        | TEXT       | Destination Station Name    ||
| start_time              | TEXT       | Nominal Start Time (ISO8601) ||
| end_time                | TEXT       | Nominal End Timestamp (ISO8601) ||
| realtime_ref_station    | TEXT       | Reference Station ID | station ID where the trip has been seen the first time |
| realtime_first_appeared | TEXT       | First Realtime Timestamp (ISO8601) |timestamp when the trip had realtime information the first time | 
| realtime_cancelled | INTEGER | Realtime Cancellation Flag | indicates whether the complete trip was cancelled for at least one time |
| realtime_num_cancelled_stops | INTEGER | Realtime No. Cancelled Stops | number of stops in this trip which are cancelled |
| realtime_num_added_stops | INTEGER | Realtime No. Added Stops | number of stops in this trip which are added |

### Installation
There're different options to use ticktrack. You can use it by cloning this repository and install it into your virtual environment directly:
```
git clone https://github.com/sebastianknopf/ticktrack.git
cd ticktrack

pip install .
```
and run it by using
```
python -m ticktrack observe ./data/ticktrack.db3 ./config/your-config.yaml
```
This is especially good for development. 

If you simply want to run ticktrack on your server, you also can use docker:
```
docker run 
    --rm 
    -v ./host/config.yaml:/app/config/config.yaml 
    -v ./host/ticktrack.db3:/app/data/data.db3
    sebastianknopf/ticktrack:latest
```
Please note, that you're required to mount a configuration file with your specific configuration and a SQLite database file into the docker container to make the application running. 

## Configuration
There's a YAML file for configuring the VDV431 interface and the stations and lines which shouled be observed. See [config/default.yaml](config/default.yaml) for reference.

As ticktrack performs periodic StopEventRequests for each configured station, the number of stations should be as small as possible to match all trips of the lines you want to monitor. This is known as `set-cover` problem in operations research. See [set-cover-gtfs.py]() for finding this minimal set of stations. This becomes the more important than the higher of lines you want to monitor is.

### Data Logging
The whole data transfer on the VDV431 interface can be logged to XML files. However, please note that ticktrack may perform several requests per minute depending on your configuration. The total amount of logged data may exceed several GB of data. _Hence, datalogging is meant to be used only for debugging purposes!_

The logging is implemented as circular logging. That means, log files are available for 24h hours and will then be deleted automatically.

## License
This project is licensed under the Apache License. See [LICENSE.md](LICENSE.md) for more information.
