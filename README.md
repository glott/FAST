# FAST (FlightAware Scraping Thingy)

_by [Josh Glottmann](https://github.com/glott)_

**Version 0.4.4** - 04/11/2023

Creates scenario files for [ATCTrainer](https://atctrainer.collinkoldoff.dev/#about) by [Collin Koldoff](https://github.com/collink2451) using data from [FlightAware](https://flightaware.com/)\*.

__[Download v0.4.4](https://github.com/glott/FAST/releases/latest/download/FAST.zip)__ 

---
### Installation

1) Download and unzip the `FAST.zip` package from the link above or on this repository's [releases](https://github.com/glott/FAST/releases/latest) page.
2) Move the `FAST` folder to a directory of your choosing. The `FAST.txt` configuration file must be saved in the `FAST` folder or in your `Downloads` folder.  
3) Download and install the latest version of [Python](https://www.python.org/downloads/).
4) Download and install the latest version of [Firefox](https://www.mozilla.org/en-US/firefox/new/) or [Chrome](https://www.google.com/chrome/).
5) `FAST` will automatically update files after running any file. 

---
### File Descriptions/Usage

**APP_SCRAPE.py**: Generates a CSV file containing aircraft data for arrivals from a specified airport. The arrival data is specifically targeted for nearby inbound arrivals joining a final approach course. This is useful for generating S1/S2 files. 

**ARR_SCRAPE.py**: Generates a CSV file containing aircraft data for arrivals from a specified airport. The arrival data is specifically targeted for distant inbound arrivals established on a STAR or other routing. This is useful for generating S3 files. 

**DEP_SCRAPE.py**: Generates a CSV file containing aircraft data for IFR departures from a specified airport.

**DEP_VFR.py**: Generates a CSV file containing aircraft data for a specified number of VFR departures.

**APP_UPLOAD.py**: Uploads approach (`APP_SCRAPE`) CSV files to [vNAS Data Admin](https://data-admin.virtualnas.net/).

**ARR_UPLOAD.py**: Uploads approach (`ARR_SCRAPE`) CSV files to [vNAS Data Admin](https://data-admin.virtualnas.net/).

**DEP_UPLOAD.py**: Uploads departure (`DEP_SCRAPE` and `DEP_VFR`) CSV files to [vNAS Data Admin](https://data-admin.virtualnas.net/).

**FAST.txt**: Configuration file for all `FAST` settings. See below for more specific information.

**FAST_UPDATE.py**: Updates all `FAST` files, merging previous configuration settings into a new configuration file. 

---
### `FAST.txt` Configuration File

#### General Information

- The `FAST.txt` configuration file must be saved in the `FAST` folder or in your `Downloads` folder.

- Each configuration line is composed of a key and value, separated by an equals sign (`=`). e.g. `AIRPORT=KSFO`, `AIRPORT` is the key and `KSFO` is the value.  

- Do not modify the name of any key (the part before the equals sign (`=`).

- Any text after the equals sign (`=`) is included in your configuration setting.

---
#### `GLOBAL` Configuration Settings

`AIRPORT`: the specified airport for the scenario being generated

- `AIRPORT=KSFO`: `KSFO` is the specified airport

`ARTCC`: ARTCC that the scenario is being generated for in the vNAS Data Admin

`BROWSER`: the specified browser to utilize

- `BROWSER=Firefox`: `Firefox` or `Chrome` are acceptable values (case insensitive)

`SLOW_INTERNET_FACTOR`: this value slows down page loading when increased, which may be necessary to download/upload data

- `SLOW_INTERNET_FACTOR=1`: loads pages at the normal speed

- `SLOW_INTERNET_FACTOR=2`: pages load `2` times slower than normal

---
#### `LOGIN` Configuration Settings

`FLIGHTAWARE_USER`: FlightAware username

`FLIGHTAWARE_PASS`: FlightAware password

`VATSIM_USER`: VATSIM CID

`VATSIM_PASS`: VATSIM password

---
#### `DEP SCRAPE` Configuration Settings

`NUM_DEP`: the number of IFR departures generated, may ultimately be slightly less than this value

`GATE_REPLACE`: any gates listed here will be replaced by the value after the colon (`:`); useful when a gate may have multiple definitions

- `GATE_REPLACE=A1:A1V,A6:A6S`: planes parking at gate `A1` will be assigned `A1V` in the CSV output file

---
#### `DEP VFR` Configuration Settings

`NUM_VFR`: the number of VFR aircraft generated, cannot be greater than the number of available GA parking spots

- `NUM_VFR=20`: 20 VFR departures will be generated (less will be generated if there are fewer than 20 available GA parking spots)

`GA_PARKING`: this is a list of pre-defined GA parking spots in your aircraft file, all separated by commas (`,`)

- `GA_PARKING=SIG1,SIG2,SIG3,41-1,41-2,41-3`: this would indicate that GA parking is available at spots `SIG1`, `SIG2`, `SIG3`, `41-1`, `41-2`, and `41-3`

`GA_PARKING_RESERVED`: these GA parking spots will not be utilize in generating VFR aircraft

- `GA_PARKING_RESERVED=SIG1,41-1`: parking spots `SIG1` and `41-1` would not be utilized

`SPAWN_DELAY_RANGE`: spawn delays (in seconds) will be randomly generated between this range of numbers, separated by a hyphen (`-`)

- `SPAWN_DELAY_RANGE=0-900`: spawn delays will be a random number between `0` and `900` seconds

`VFR_TYPES`: a list of possible VFR departure aircraft types separated by commas (`,`) with each aircraft type including a weighting following the type code and a colon (`:`)

- `VFR_TYPES=C172:500,C182:300,P28A:200`: in this example, a `C172` (`500/1000`) is 1.67 times as likely to be generated as a `C182` (`300/1000`) and 2.5 times as likely as a `P28A` (`200/1000`)

- `VFR_TYPES=C172:1,C182:1,P28A:1`: in this example, all aircraft are equally likely (`1/3`) of being generated

- The default values included in the default configuration file approximately represents common piston aircraft in the U.S.

---
#### `DEP UPLOAD` Configuration Settings

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

---
#### `APP SCRAPE` Configuration Settings

`NUM_APP`: the number of IFR arrivals generated which spawn on final approach, may ultimately be slightly less than this value

`INTERCEPT_ALT`: this is the lowest altitude that an aircraft will spawn at

- `INTERCEPT_ALT=4000`: the inbound aircraft's position, time, and altitude at the last data point before reaching (or going below) `4000` feet will be recorded

`ROUTER`: a list of routing information for aircraft to join a final approach course

- Individual routing format: `ARRIVAL:DIRECT TO:PROCEDURE`

- `ROUTER=SERFR:HEMAN:28L,DYAMD:CEPIN:28R`: all aircraft with `SERFR` in their flightplan will fly directly to `HEMAN` and join the approach to runway `28L`; all aircraft with `DYAMD` in their flightplan will fly directly to `CEPIN` and join the approach to runway `28R`

---
#### `APP UPLOAD` Configuration Settings

`APP_SCENARIO`: see `DEP_SCENARIO` above for usage

`APP_CSV_FILE`: see `DEP_CSV_FILE` above for usage

`APP_TIME_COMPRESSION`: see `DEP_TIME_COMPRESSION` above for usage

- For busy airports, `APP_TIME_COMPRESSION` should likely be set to `1`

`APP_TIME_OFFSET`: see `DEP_TIME_OFFSET` above for usage

- `APP_TIME_OFFSET=0` is the recommended value for most situations

`APP_MAX_DELAY`: this can be used to reduce the gap between arrivals

- `APP_MAX_DELAY=150`: two aircraft will have at most a `150` second delay between each other

- This setting should be utilized before modifying `APP_TIME_COMPRESSION` or `APP_TIME_OFFSET`

`CROSS_RESTRICT`: a list of crossing restrictions for inbound aircraft

- `CROSS_RESTRICT=HEMAN:3100,CEPIN:3000`: aircraft routed via `HEMAN` will cross it at `3100` feet and `210` knots

`SPEED_RESTRICT`: a list of speed restrictions for inbound aircraft

- `SPEED_RESTRICT=HEMAN:180 DUYET,CEPIN:180 AXMUL`: aircraft routed via `HEMAN` will maintain `180` knots until `DUYET` (after passing `HEMAN`)

---
#### `ARR SCRAPE` Configuration Settings

`NUM_ARR`: the number of IFR arrivals generated which spawn at a specified location on an arrival, may ultimately be slightly less than this value

`ARR_PATHS`: the arrival paths that will be searched for in an aircraft's route, the specified spawn in location, and the specified distance before the spawn in location, all separated by colons (`:`), each path is separated by a comma (`,`); the number sign (`#`) can be used as a wildcard for an arrival version number

- `ARR_PATHS=SERFR#:NRRLI:10,ALWYS CEDES ARCHI:ALWYS:10`: aircraft on the `SERFR` arrival (of any version, e.g. `SERFR4`) will spawn in no closer than `10` nm before `NRRLI`; aircraft with the route `ALWYS CEDES ARCHI` in their flightplan will spawn in no closer then `10` nm before `ALWYS`

**NOTE**: in order to use `ARR SCRAPE`, a `Waypoints.xml` file must be placed in either the `FAST` folder, `%appdata%\vSTARS`, or `%localappdata%\vERAM`; the script will not work without this file included in either of those locations

---
#### `ARR UPLOAD` Configuration Settings

`ARR_SCENARIO`: see `DEP_SCENARIO` above for usage

`ARR_CSV_FILE`: see `DEP_CSV_FILE` above for usage

`ARR_TIME_COMPRESSION`: see `DEP_TIME_COMPRESSION` above for usage

- For busy airports, `ARR_TIME_COMPRESSION` should likely be set to `1`

`ARR_TIME_OFFSET`: see `DEP_TIME_OFFSET` above for usage

- `ARR_TIME_OFFSET=0` is the recommended value for most situations

`ARR_MAX_DELAY`: this can be used to reduce the gap between arrivals

- `ARR_MAX_DELAY=120`: two aircraft will have at most a `120` second delay between each other

- This setting should be utilized before modifying `ARR_TIME_COMPRESSION` or `ARR_TIME_OFFSET`

`RWY_TRANSITION`: runway transitions can be specified if the arrival requires one

- `RWY_TRANSITION=DYAMD:28R,ALWYS:19L`: aircraft on the `DYAMD` arrival will fly the `28R` transition; aircraft on the `ALWYS` arrival will fly the `19L` transition

---
*\* Josh Glottmann is not responsible for any misuse of this software.*
