# FAST (FlightAware Scraping Thingy)

_by [Josh Glottmann](https://github.com/glott)_

**Version 0.1.0** - 04/04/2023

Creates scenario files for [ATCTrainer](https://atctrainer.collinkoldoff.dev/#about) by [Collin Koldoff](https://github.com/collink2451) using data from [FlightAware](https://flightaware.com/)\*. 

__[Download](https://github.com/vzoa/FAST/releases)__ 

---
### Installation

1) Download and unzip the `FAST.zip` package from the link above or on this repository's [releases](https://github.com/vzoa/FAST/releases) page. 
2) Move the `FAST` folder to a directory of your choosing. The `FAST.txt` configuration file must be saved in the `FAST` folder **\[not working as of 04/04/23\]** or in your `Downloads` folder.  
3) Download and install the latest version of [Python](https://www.python.org/downloads/). 
4) Download and install the latest version of [Firefox](https://www.mozilla.org/en-US/firefox/new/).

---
### File Descriptions/Usage

**DEP_SCRAPE.py**: Generates a CSV file containing aircraft data for the next 40 departures from a specified airport. 

**DEP_VFR.py**: Generates a CSV file containing aircraft data for a specified number of VFR departures. 

**DEP_UPLOAD.py**: Uploads departure CSV files to [vNAS Data Admin](https://data-admin.virtualnas.net/).

**ARR_SCRAPE.py**: Generates a CSV file containing aircraft data for the previous 40 arrivals from a specified airport. The arrival data is specifically targeted for nearby inbound arrivals joining a final approach course. 

**FAST.txt**: Configuration file for all `FAST` settings. See below for more specific information.

---
### `FAST.txt` Configuration File

#### General Information

- The `FAST.txt` configuration file must be saved in the `FAST` folder **\[not working as of 04/04/23\]** or in your `Downloads` folder. 

- Each configuration line is composed of a key and value, separated by an equals sign (`=`). e.g. `AIRPORT=KSFO`, `AIRPORT` is the key and `KSFO` is the value.  

- Do not modify the name of any key (the part before the equals sign (`=`).

- Any text after the equals sign (`=`) is included in your configuration setting. 

#### Global Configuration Settings

`AIRPORT`: the specified airport for the scenario being generated

- `AIRPORT=KSFO`: `KSFO` is the specified airport

`SLOW_INTERNET_FACTOR`: this value slows down page loading when increased, which may be necessary to download/upload data

- `SLOW_INTERNET_FACTOR=1`: loads pages at the normal speed

- `SLOW_INTERNET_FACTOR=2`: pages load `2` times slower than normal.

#### `DEP SCRAPE` Configuration Settings

`FLIGHTAWARE_USER`: FlightAware username

`FLIGHTAWARE_PASS`: FlightAware password

#### `DEP VFR` Configuration Settings

`GA_PARKING`: this is a list of pre-defined GA parking spots in your aircraft file, all separated by commas (`,`)

- `GA_PARKING=SIG1,SIG2,SIG3,41-1,41-2,41-3`: this would indicate that GA parking is available at spots `SIG1`, `SIG2`, `SIG3`, `41-1`, `41-2`, and `41-3`

`GA_PARKING_RESERVED`: these GA parking spots will not be utilize in generating VFR aircraft

- `GA_PARKING_RESERVED=SIG1,41-1`: parking spots `SIG1` and `41-1` would not be utilized

`NUM_VFR`: the number of VFR aircraft generated, cannot be greater than the number of available GA parking spots

- `NUM_VFR=20`: 20 VFR departures will be generated (less will be generated if there are fewer than 20 available GA parking spots)

`SPAWN_DELAY_RANGE`: spawn delays (in seconds) will be randomly generated between this range of numbers, separated by a hyphen (`-`)

- `SPAWN_DELAY_RANGE=0-900`: spawn delays will be a random number between `0` and `900` seconds

`VFR_TYPES`: a list of possible VFR departure aircraft types separated by commas (`,`) with each aircraft type including a weighting following the type code and a colon (`:`)

- `VFR_TYPES=C172:500,C182:350,P28A:150`: in this example, a `C172` is twice as likely (`500/1000`) to be generated than a `C182` (`350/1000`) or `P28A` (`150/1000`)

- `VFR_TYPES=C172:1,C182:1,P28A:1`: in this example, all aircraft are equally likely (`1/3`) of being generated

- The default values included in the default configuration file approximately represents common piston aircraft in the U.S.

#### `DEP UPLOAD` Configuration Settings

`VATSIM_USER`: VATSIM CID

`VATSIM_PASS`: VATSIM password

`ARTCC`: ARTCC that the scenario is being generated for in the vNAS Data Admin

`SCENARIO`: the scenario ID that has already been created in the vNAS Data Admin

- The scenario ID can be found after `/training/scenarios/` in the vNAS Data Admin URL

- `SCENARIO=01GX6E5E0HQKHRR3EA0V42VWPH`: the following URL would result in this configuration value, `https://data-admin.virtualnas.net/training/scenarios/01GX6E5E0HQKHRR3EA0V42VWPH`

`CSV_FILE`: the CSV file utilized for data upload, located either in your `Downloads` folder or the `FAST` folder, the `.csv` extension does not need to be included

- `CSV_FILE=SFO_DEP_IFR_230403-1530`: the CSV file being utilized would be `SFO_DEP_IFR_230403-1530.csv`

`TIME_COMPRESSION`: this causes all spawn delays to be divided by the specified value

- `TIME_COMPRESSION=4`: if a spawn delay was originally `400` seconds, it would be reduced to `100` seconds

- This is useful for spawning in more departures than an airport may typically see in a certain period of time for training purposes

`TIME_OFFSET`: all spawn delays are offset (sooner) by this amount of time in seconds; this is applied after the `TIME_COMPRESSION` above; all spawn delays less than the offset spawn immediately

- `TIME_OFFSET=600`: all aircraft spawn `600` seconds sooner (after `TIME_COMPRESSION` is applied); an aircraft with a spawn delay of `300` seconds would spawn immediately; an aircraft with a spawn delay of `1250` seconds would spawn after `650` seconds

#### `ARR SCRAPE` Configuration Settings

`FLIGHTAWARE_USER` and `FLIGHTAWARE_PASS` must be completed in the `DEP SCRAPE` section of the configuration file

`INTERCEPT_ALT`: this is the lowest altitude that an aircraft will spawn at

- `INTERCEPT_ALT=4000`: the inbound aircraft's position, time, and altitude at the last data point before reaching (or going below) `4000` feet will be recorded

`ROUTER`: information TBD

---
*\* Josh Glottmann and vZOA are not responsible for any misuse of this software.*