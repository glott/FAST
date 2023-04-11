# IMPORTS AND COMMON FUNCTIONS
import csv, math, os, pathlib, random, random, re, requests
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
    + read_config_value('AIRPORT') + '/scheduled'

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

num_acft = int(read_config_value('NUM_DEP'))
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

# CREATE AIRCRAFT DATA FILE
s = 'ident,type,dep,arr,alt,speed,route,rules,equip,spawn-delay,' \
    + 'gate,push-taxiway,taxi-route'
init_spawn_delay = 0

print('Scraping departure data at ' + read_config_value('AIRPORT') + '.')

gates = {}
for gate in read_config_value('GATE_REPLACE').split(','):
    gates[gate.split(':')[0]] = gate.split(':')[1]

def get_plane_info(source):
    temp_text = source[source.rindex(r'"route"') - 3000:
                       source.rindex(r'"route"') + 1500]
    global init_spawn_delay

    ident = between(temp_text, r'"displayIdent":"', r'"')
    flight_plan = between(temp_text, r'"flightPlan":', r'"fuelBurn"')
    alt = between(flight_plan, r'"altitude":', r',') + '00'
    speed = between(flight_plan, r'"speed":', r',')
    route = between(flight_plan, r'"route":"', r'",').replace(',', '')
    delay = int(between(flight_plan, r'departure":', r',"ete"'))
    if delay < round(time.time() - 30 * 60):
        return ident + ',-1'
    spawn_delay = 0 if init_spawn_delay == 0 else delay - init_spawn_delay
    dep = between(source, r'name="origin" content="', r'"')
    arr = between(source, r'name="destination" content="', r'"')
    acft = between(source, r'name="aircrafttype" content="', r'"')
    gate = 'UNKN' if not r'","gate":"' in source \
        else between(source, dep + r'","gate":"', r'"')
    if gate in gates:
        gate = gates[gate]

    if len(alt) == 0 or 'null' in alt: alt = '0'
    if len(speed) == 0 or 'null' in speed: speed = '0'
    if len(dep) == 0 or 'null' in dep: dep = 'ZZZZ'
    if len(arr) == 0 or 'null' in arr: arr = 'ZZZZ'
    if len(acft) == 0 or 'null' in acft: acft = 'ZZZZ'
    if len(gate) == 0 or 'null' in gate: gate = 'UNKN'
    
    if init_spawn_delay == 0: init_spawn_delay = delay

    return ','.join([ident, acft, dep, arr, alt, speed,
                     route, 'I', 'L', str(spawn_delay), gate, '', ''])

num_planes = 0
for filtered_url in filtered_urls:
    if num_planes >= num_acft:
        break
    
    driver.get(filtered_url)
    plane = get_plane_info(driver.page_source)
    
    if len(plane.split(',')) == 2:
        print('Skipping ' + plane.split(',')[0] + '.')
        wait(w=random.uniform(1, 2.5))
        continue
        
    s += '\n' + plane
    print('Scraped ' + plane.split(',')[0] + '\t' \
        + plane.split(',')[2] + '-' + plane.split(',')[3] + ', ' \
        + plane.split(',')[1] + ', ' + plane.split(',')[4])
    num_planes += 1
    wait(w=random.uniform(1, 2.5))

# FILE OUTPUT
out_file = s.split('\n')[1].split(',')[2][1:] + '_DEP_IFR_' \
    + time.strftime('%y%m%d-%H%M', time.gmtime()) + '.csv'
print('Writing aircraft data to \'scenarios/' + str(out_file) + '\'.')

out_file = working_directory + '\\scenarios\\' + out_file
os.makedirs(os.path.dirname(out_file), exist_ok=True)
with open(out_file, 'w') as f: 
    f.write(s)

print('Departure scraping complete!')
driver.quit()