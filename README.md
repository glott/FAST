# FAST (FlightAware Scraping Thingy)

_by [Josh Glottmann](https://github.com/glott)_

**Version 0.2.7** - 04/07/2023

Creates scenario files for [ATCTrainer](https://atctrainer.collinkoldoff.dev/#about) by [Collin Koldoff](https://github.com/collink2451) using data from [FlightAware](https://flightaware.com/)\*.

__[Download v0.2.7](https://github.com/glott/FAST/releases/latest/download/FAST.zip)__ 

---
### Installation

1) Download and unzip the `FAST.zip` package from the link above or on this repository's [releases](https://github.com/glott/FAST/releases/latest) page.
2) Move the `FAST` folder to a directory of your choosing. The `FAST.txt` configuration file must be saved in the `FAST` folder or in your `Downloads` folder.  
3) Download and install the latest version of [Python](https://www.python.org/downloads/).
4) Download and install the latest version of [Firefox](https://www.mozilla.org/en-US/firefox/new/) or [Chrome](https://www.google.com/chrome/).

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

- The `FAST.txt` configuration file must be saved in the `FAST` folder or in your `Downloads` folder.

- Each configuration line is composed of a key and value, separated by an equals sign (`=`). e.g. `AIRPORT=KSFO`, `AIRPORT` is the key and `KSFO` is the value.  

- Do not modify the name of any key (the part before the equals sign (`=`).

- Any text after the equals sign (`=`) is included in your configuration setting.

#### Global Configuration Settings

`AIRPORT`: the specified airport for the scenario being generated

- `AIRPORT=KSFO`: `KSFO` is the specified airport

`ARTCC`: ARTCC that the scenario is being generated for in the vNAS Data Admin

`BROWSER`: the specified browser to utilize

- `BROWSER=Firefox`: `Firefox` or `Chrome` are acceptable values (case insensitive)

`SLOW_INTERNET_FACTOR`: this value slows down page loading when increased, which may be necessary to download/upload data

- `SLOW_INTERNET_FACTOR=1`: loads pages at the normal speed

- `SLOW_INTERNET_FACTOR=2`: pages load `2` times slower than normal

#### `DEP SCRAPE` Configuration Settings

`FLIGHTAWARE_USER`: FlightAware username

`FLIGHTAWARE_PASS`: FlightAware password

`NUM_DEP`: the number of IFR departures generated, may ultimately be slightly less than this value

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

- `VFR_TYPES=C172:500,C182:300,P28A:200`: in this example, a `C172` (`500/1000`) is 1.67 times as likely to be generated as a `C182` (`300/1000`) and 2.5 times as likely as a `P28A` (`200/1000`)

- `VFR_TYPES=C172:1,C182:1,P28A:1`: in this example, all aircraft are equally likely (`1/3`) of being generated

- The default values included in the default configuration file approximately represents common piston aircraft in the U.S.

#### `DEP UPLOAD` Configuration Settings

`VATSIM_USER`: VATSIM CID

`VATSIM_PASS`: VATSIM password

`DEP_SCENARIO`: the scenario ID that has already been created in the vNAS Data Admin

- The scenario ID can be found after `/training/scenarios/` in the vNAS Data Admin URL

- `DEP_SCENARIO=01GX6E5E0HQKHRR3EA0V42VWPH`: the following URL would result in this configuration value, `https://data-admin.virtualnas.net/training/scenarios/01GX6E5E0HQKHRR3EA0V42VWPH`

`DEP_CSV_FILE`: the CSV file utilized for data upload, located either in your `Downloads` folder or the `FAST` folder, the `.csv` extension does not need to be included

- `DEP_CSV_FILE=SFO_DEP_IFR_230403-1530`: the CSV file being utilized would be `SFO_DEP_IFR_230403-1530.csv`

`DEP_TIME_COMPRESSION`: this causes all spawn delays to be divided by the specified value

- `DEP_TIME_COMPRESSION=4`: if a spawn delay was originally `400` seconds, it would be reduced to `100` seconds

- This is useful for spawning in more departures than an airport may typically see in a certain period of time for training purposes

`DEP_TIME_OFFSET`: all spawn delays are offset (sooner) by this amount of time in seconds; all spawn delays less than the offset spawn immediately; the offset is applied after any `DEP_TIME_COMPRESSION` above 

- `DEP_TIME_OFFSET=600`: all aircraft spawn `600` seconds sooner (after `DEP_TIME_COMPRESSION` is applied); an aircraft with a spawn delay of `300` seconds would spawn immediately; an aircraft with a spawn delay of `1250` seconds would spawn after `650` seconds

- This is useful for spawning in aircraft immediately into a file

#### `ARR SCRAPE` Configuration Settings

`FLIGHTAWARE_USER` and `FLIGHTAWARE_PASS` must be completed in the `DEP SCRAPE` section of the configuration file

`NUM_ARR`: the number of IFR arr generated, may ultimately be slightly less than this value

`INTERCEPT_ALT`: this is the lowest altitude that an aircraft will spawn at

- `INTERCEPT_ALT=4000`: the inbound aircraft's position, time, and altitude at the last data point before reaching (or going below) `4000` feet will be recorded

`ROUTER`: a list of routing information for aircraft to join a final approach course

- Individual routing format: `ARRIVAL:DIRECT TO:PROCEDURE`

- `ROUTER=SERFR:HEMAN:28L,DYAMD:CEPIN:28R`: all aircraft with `SERFR` in their flightplan will fly directly to `HEMAN` and join the approach to runway `28L`; all aircraft with `DYAMD` in their flightplan will fly directly to `CEPIN` and join the approach to runway `28R`

#### `ARR UPLOAD` Configuration Settings

`ARR_SCENARIO`: see `DEP_SCENARIO` above for usage

`ARR_CSV_FILE`: see `DEP_CSV_FILE` above for usage

`ARR_TIME_COMPRESSION`: see `DEP_TIME_COMPRESSION` above for usage

- For busy airports, `ARR_TIME_COMPRESSION` should likely be set to `1`

`ARR_TIME_OFFSET`: see `DEP_TIME_OFFSET` above for usage

- `ARR_TIME_OFFSET=0` is the recommended value for most situations

`MAX_DELAY`: this can be used to reduce the gap between arrivals

- `MAX_DELAY=150`: two aircraft will have at most a `150` second delay between each other

- This setting should be utilized before modifying `ARR_TIME_COMPRESSION` or `ARR_TIME_OFFSET`

`CROSS_RESTRICT`: a list of crossing restrictions for inbound aircraft

- `CROSS_RESTRICT=HEMAN:3100,CEPIN:3000`: aircraft routed via `HEMAN` will cross it at `3100` feet and `210` knots

`SPEED_RESTRICT`: a list of speed restrictions for inbound aircraft

- `SPEED_RESTRICT=HEMAN:180 DUYET,CEPIN:180 AXMUL`: aircraft routed via `HEMAN` will maintain `180` knots until `DUYET` (after passing `HEMAN`)

---
*\* Josh Glottmann is not responsible for any misuse of this software.*
