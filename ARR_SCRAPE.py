# IMPORTS AND COMMON FUNCTIONS
import csv, math, os, pathlib, random, random, re, subprocess
import sys, time, urllib.request, warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import imp
    imp.find_module('requests')
    imp.find_module('selenium')
    imp.find_module('webdriver_manager')
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'requests']);
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'selenium']);
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'webdriver_manager']);
    os.system('cls')

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager

working_directory = ''
if os.path.isfile(os.getcwd() + '\\FAST.txt'):
    working_directory = os.getcwd()
elif os.path.isfile(str(pathlib.Path.home() / 'Downloads\\FAST.txt')):
    working_directory = str(pathlib.Path.home() / 'Downloads')
else:
    print('FAST.txt file not found!\nPlace valid FAST.txt file in this ' \
          + 'folder or in your Downloads folder.\nDefault file:' \
          + ' https://raw.githubusercontent.com/glott/FAST/main/FAST.txt')
    
def check_for_updates():
    try: 
        response = urllib.request.urlopen( \
            'https://github.com/glott/FAST/releases/latest')
        ver = str(response.read()).split('FAST/tree/')[1].split(r'"')[0][1:]
        
        config_file = os.getcwd() + '\\FAST.txt'
        readme_file = os.getcwd() + '\\README.md'
        if os.path.isfile(config_file) and not os.path.isfile(readme_file):
            with open(config_file, 'r') as file:
                config = file.read()
            if 'Version ' in config:
                config_version = config.split('Version ')[1].split(' ')[0]
                if config_version not in ver:
                    os.system('python FAST_UPDATE.py 0')
                    print('Updated FAST files to v' + ver + '.')
                    for i in range(5, 0, -1):
                        print('Restarting ' + os.path.basename(__file__) \
                            + ' in ' + str(i) + '.', end='\r')
                        time.sleep(1)
                    print(end='\n')
                    os.system('cls')
                    os.system('python ' + ' '.join(sys.argv))
    except Exception:
        pass

print('-------------------- FAST --------------------')
check_for_updates()

def read_config_value(key):
    config = open(working_directory + '\\FAST.txt', 'r').read()
    if key + '=' in config:
        return config.split(key + '=')[1].split('\n')[0]
    return 'NULL'

def between(text, start, end):
    try: 
        return text.split(start)[1].split(end)[0]
    except Exception:
        return ''
    
def click_button(text):
    try: 
        button = driver.find_element('xpath', 
           '//button[contains(text(), \'' + text + '\')]')
        driver.execute_script('arguments[0].scrollIntoView(true);', button)
        driver.execute_script('window.scrollBy(0, -' + 
            str(round(button.size['height'] * 2)) + ');')
        button.click()
    except Exception:
        print('Unable to click button \'' + text + '\'.')

sleep_factor = float(read_config_value('SLOW_INTERNET_FACTOR'))
def wait(w=1, t=5):
    try:
        webdriver.support.ui.WebDriverWait(driver, t).until(webdriver \
        .support.expected_conditions.url_changes(driver.current_url))
    except Exception:
        pass
    time.sleep(w * sleep_factor)

# OPEN BROWSER
browser = read_config_value('BROWSER').capitalize()
print('Opening ' + browser + '.')

driver = None
if 'C' in browser:
    options = webdriver.chrome.options.Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(executable_path=ChromeDriverManager()
        .install(), options=options);
else:
    driver = webdriver.Firefox(executable_path=GeckoDriverManager() \
        .install(), service_log_path=os.devnull);
driver.minimize_window()

# GENERATE AIRCRAFT URLs
print('Logging in to FlightAware.')
url = 'https://flightaware.com/live/airport/' \
    + read_config_value('AIRPORT') + '/arrivals'

driver.get(url)

try:
    driver.find_element('name', 'flightaware_username') \
        .send_keys(read_config_value('FLIGHTAWARE_USER'))
    driver.find_element('name', 'flightaware_password') \
        .send_keys(read_config_value('FLIGHTAWARE_PASS'))
    driver.find_element('id', 'loginButton').click()
    if 'account/session' in driver.current_url:
        print('Unsuccessfully logged in to FlightAware.')
    else:
        print('Successfully logged in to FlightAware.')
except Exception:
    print('Unsuccessfully logged in to FlightAware.')

wait()

num_acft = int(read_config_value('NUM_ARR'))
filtered_urls = list()

for i in range(0, -(-(num_acft + 15) // 40)):
    if i != 0:
        driver.get(url + '?;offset=' + str(i * 40))
        wait()
    
    plane_urls = driver.find_elements('xpath', '//a[@href]')
    for plane_url in plane_urls:
        href = plane_url.get_attribute('href')
        if 'live/flight/id/' in href:
            filtered_urls.append(href)

print('Captured URLs for ' + str(num_acft) + ' planes.')

# GENERATE WAYPOINTS USED IN CALCULATIONS
paths = list()
for path in read_config_value('ARR_PATHS').split(','):
    paths.append(path.split(':'))

waypoints = {}
waypoints_file = ''
if os.path.isfile(working_directory + '\\Waypoints.xml'):
    waypoints_file = working_directory + '\\Waypoints.xml'
elif os.path.isfile(os.getenv('APPDATA') + '\\vSTARS\\Waypoints.xml'):
    waypoints_file = os.getenv('APPDATA') + '\\vSTARS\\Waypoints.xml'
elif os.path.isfile(os.getenv('LOCALAPPDATA') + '\\vERAM\\Waypoints.xml'):
    waypoints_file = os.getenv('LOCALAPPDATA') + '\\vERAM\\Waypoints.xml'
else:
    print('Waypoints.xml not found. ' \
        + 'Please place Waypoints.xml in your FAST folder.')

with open(waypoints_file, 'r') as file:
    wxml = file.read()
    for w in [row[1] for row in paths]:
        if w in wxml:
            w_info = wxml.split(w)[1].split('/Waypoint')[0]
            lat = float(w_info.split(r'Lat="')[1].split(r'"')[0])
            lon = float(w_info.split(r'Lon="')[1].split(r'"')[0])
            waypoints[w] = [lat, lon]

# POSITION CALCULATION METHODS
def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) \
        * math.sin(dlon / 2) ** 2
    return 2 * math.asin(math.sqrt(a)) * 3440.07

def get_plane_time(alt, t_str):
    altitude_json = between(driver.page_source, 'altitude_json = ', ';')
    alts = altitude_json.replace('[[', '').replace(']]', '') \
        .replace('],[', ';').split(';')
    
    for t_a in alts:
        if ',' not in t_a:
            continue
        a = int(t_a.split(',')[1])
        if a == int(alt):
            t = int(int(t_a.split(',')[0]) / 1000)
            if time.strftime('%M:%S', time.gmtime(t)) in t_str:
                return t
    return -1

def read_plane_data(line, latlon=False):
    if latlon:
        return [float(line[3]), float(line[4])]
    lat = float(line[3])
    lon = float(line[4])
    hdg = int(line[6].replace('°', ''))
    spd = int(line[7])
    k = 1 if 'mph' in driver.find_element('xpath', \
        '//tr[@class=\'thirdHeader\']').text else 0
    alt = int('0' + line[8 + k].replace(',', ''))
    t = get_plane_time(alt, ':'.join(line[1].split(':')[1:]))
    return [lat, lon, hdg, spd, alt, t]

def get_plane_data(rte, url):
    driver.get(url)
    proc = ''
    dct = ''
    fix = [0, 0]
    offset = 0
    for path in paths:
        if re.search(path[0].replace('#', '[0-9]'), rte):
            proc = re.search(path[0].replace('#', '[0-9]'), rte).group(0)
            dct = path[1]
            fix = waypoints[path[1]]
            offset = float(path[2])
            break
    elems = driver.find_elements('xpath', '//tr[@class=\'smallrow1\']')   

    min_dist = 1e6
    min_dist_idx = -1
    idx = 0
    while idx < len(elems):
        lat, lon = read_plane_data(elems[idx].text.split(' '), latlon=True)
        dist = haversine(fix[0], fix[1], lat, lon)
        if dist > 500:
            idx += int(.1 * (len(elems) - idx))
        if dist + offset < min_dist:
            min_dist = dist
            min_dist_idx = idx
        idx += 1
    return read_plane_data(elems[min_dist_idx - 1].text.split(' ')) \
        + [dct, proc]

# SCRAPING METHOD
s = 'ident,type,dep,arr,alt,speed,route,rules,equip,spawn-delay,' \
    + 'gate,lat,lon,ralt,rspeed,hdg,dct,proc'

def get_plane_info(source):
    temp_text = source[source.rindex(r'"route"') - 3000:
                       source.rindex(r'"route"') + 1500]

    ident = between(temp_text, r'"displayIdent":"', r'"')
    flight_plan = between(temp_text, r'"flightPlan":', r'"fuelBurn"')
    alt = between(flight_plan, r'"altitude":', r',') + '00'
    speed = between(flight_plan, r'"speed":', r',')
    route = between(flight_plan, r'"route":"', r'",').replace(',', '')
    dep = between(source, r'name="origin" content="', r'"')
    arr = between(source, r'name="destination" content="', r'"')
    acft = between(source, r'name="aircrafttype" content="', r'"')
    gate = 'UNKN' if not r'","gate":"' in temp_text \
        else between(temp_text, arr + r'","gate":"', r'","term')
    
    if len(alt) == 0 or 'null' in alt: alt = '0'
    if len(speed) == 0 or 'null' in speed: speed = '0'
    if len(dep) == 0 or 'null' in dep: dep = 'ZZZZ'
    if len(arr) == 0 or 'null' in arr: arr = 'ZZZZ'
    if len(acft) == 0 or 'null' in acft: acft = 'ZZZZ'
    if len(gate) == 0 or 'null' in gate: gate = 'UNKN'
    
    lat, lon, hdg, rspeed, ralt, rtime, dct, proc = \
        0, 0, 0, -1, -1, -1, '', ''
    try:
        lat, lon, hdg, rspeed, ralt, rtime, dct, proc = get_plane_data( \
            route, driver.current_url +'/tracklog')
    except Exception:
        pass
    
    return ','.join([ident, acft, dep, arr, alt, speed, route, 
        'I', 'L', str(rtime), gate, str(lat), str(lon), str(ralt), 
        str(rspeed), str(hdg), dct, proc])

# SCRAPE AND CREATE AIRCRAFT DATA FILE
print('Scraping arrival data at ' + read_config_value('AIRPORT') + '.')

num_planes = 0
for filtered_url in filtered_urls:
    if num_planes >= num_acft:
        break
    
    driver.get(filtered_url)
    plane = get_plane_info(driver.page_source)
    
    if float(plane.split(',')[11]) == 0:
        continue
    
    s += '\n' + plane
    print('Scraped ' + plane.split(',')[0] + '\t' \
        + plane.split(',')[2] + '-' + plane.split(',')[3] + ', ' \
        + plane.split(',')[1] + ', ' + plane.split(',')[4])
    num_planes += 1
    wait(w=random.uniform(1, 2.5))

# FILE OUTPUT
s_sorted = sorted([i.split(',') for i in s.split('\n')[1:]], \
    key=lambda x: x[9])
s_out = s.split('\n')[0]
init_spawn_delay = 0
for plane in s_sorted:
    if float(plane[11]) == 0:
        continue
    delay = int(plane[9])
    plane[9] = 0 if init_spawn_delay == 0 else delay - init_spawn_delay
    if init_spawn_delay == 0: 
        init_spawn_delay = delay
    s_out += '\n' + ','.join(str(x) for x in plane)
    
out_file = s_out.split('\n')[1].split(',')[3][1:] + '_ARR_' \
    + time.strftime('%y%m%d-%H%M', time.gmtime()) + '.csv'
print('Writing aircraft data to \'scenarios/' + str(out_file) + '\'.')

out_file = working_directory + '\\scenarios\\' + out_file
os.makedirs(os.path.dirname(out_file), exist_ok=True)
with open(out_file, 'w') as f: 
    f.write(s_out)

print('Arrival scraping complete!')
driver.quit()