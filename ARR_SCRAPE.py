# IMPORTS AND COMMON FUNCTIONS
import csv, os, pathlib, random, random, re, requests
import subprocess, sys, time, urllib.request, warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import imp
    imp.find_module('selenium')
    imp.find_module('webdriver_manager')
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'selenium']);
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'webdriver_manager']);
    
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
                    os.system('python FAST_UPDATE.py')
                    print('Updated FAST files to v' + ver + '.')
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

print('Captured URLs for ' + str(num_acft) + '.')

# SCRAPING METHODS
s = 'ident,type,dep,arr,alt,speed,route,rules,equip,spawn-delay,' \
    + 'gate,lat,lon,ralt,rspeed,hdg,dct,proc'
goal_intercept_alt = int(read_config_value('INTERCEPT_ALT'))
router_long = read_config_value('ROUTER').split(',')
router = [i.split(':') for i in router_long]
routes = [i[0] for i in router]

def find_intercept(tracklog_url):
    wait(w=random.uniform(1, 2.5))
    driver.get(tracklog_url)
    
    altitude_json = between(driver.page_source, 'altitude_json = ', ';')
    alts = altitude_json.replace('[[', '').replace(']]', '') \
        .replace('],[', ';').split(';')

    intercept_time = -1
    intercept_alt = -1
    for i in range(round(3 * len(alts) / 4), len(alts) - 1):
        if len(alts[i].split(',')) < 2:
            continue
        current_alt = int(alts[i].split(',')[1])
        if int(alts[i].split(',')[1]) < goal_intercept_alt:
            intercept_time = int(int(alts[i - 1].split(',')[0]) / 1e3)
            intercept_alt = int(alts[i - 1].split(',')[1])
            break
    if intercept_alt == -1:
        return intercept_alt, intercept_time, -1, 0, 0, 0
    int_time = time.strftime('%a %I:%M:%S %p', time.gmtime(intercept_time))
    position_data = driver.find_element('xpath', \
        '//span[contains(text(), \'' + int_time +'\')]') \
        .find_element('xpath', '../..').get_attribute('innerHTML')

    p = position_data.split(r'<span class="show-for-medium-up">')
    lat = float(p[2].split('</span>')[0])
    lon = float(p[3].split('</span>')[0])
    
    intercept_speed = int(position_data.split(r'<td align="right">')[4] \
        .split(r'</td>')[0])
    
    hdg = position_data.split(r'<td align="right">')[3].split(r'</td>')[0]
    hdg = int(re.sub('[^0-9]', '', hdg))
    
    return intercept_alt, intercept_time, intercept_speed, hdg, lat, lon

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
    
    ralt, rtime, rspeed, hdg, lat, lon = -1, -1, -1, 0, 0, 0
    try:
        ralt, rtime, rspeed, hdg, lat, lon = find_intercept( \
            driver.current_url +'/tracklog')
    except Exception:
        pass

    dct, proc = '', ''
    for i in range(0, len(routes)):
        if routes[i] in route:
            dct, proc = router[i][1], router[i][2]
    
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
    
    s += '\n' + plane
    print('Scraped ' + plane.split(',')[0] + '\t' \
        + plane.split(',')[2] + '-' + plane.split(',')[3] + ', ' \
        + plane.split(',')[1] + ', ' + plane.split(',')[4])
    num_planes += 1
    wait(w=random.uniform(1, 2.5))
    
s_sorted = sorted([i.split(',') for i in s.split('\n')[1:]], \
    key=lambda x: x[9])
s_out = s.split('\n')[0]
init_spawn_delay = 0
for plane in s_sorted:
    if plane[11] == 0:
        continue
    delay = int(plane[9])
    plane[9] = 0 if init_spawn_delay == 0 else delay - init_spawn_delay
    if init_spawn_delay == 0: 
        init_spawn_delay = delay
    s_out += '\n' + ','.join(str(x) for x in plane)
    
out_file = s_out.split('\n')[1].split(',')[3][1:] + '_ARR_APP_' \
    + time.strftime('%y%m%d-%H%M', time.gmtime()) + '.csv'
print('Writing aircraft data to ' + str(out_file) + '.')
with open(working_directory + '\\' + out_file, 'w') as f: 
    f.write(s_out)

print('Arrival scraping complete!')
driver.quit()