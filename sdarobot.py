import threading

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import memory
import re
import seasons_lengths as sl
import pyautogui
from selenium.webdriver.common.by import By

wait_time = 34
page_downs = 2
page_loaded = False
finished = False
pause = True
seconds_before_to_quit = 0


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--disable-extensions')
# chrome_options.headless = True
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "load-extension"])
prefs = {'profile.default_content_setting_values.notifications': 2}
chrome_options.add_experimental_option('prefs', prefs)


def do_nothing(*args):
    pass


def get_webdriver_path():
    with open('settings.txt', 'r') as settings:
        return settings.readlines()[0].replace('\n', '')


webdriver_path = get_webdriver_path()


def get_series_url(series):
    return memory.series_dict[series]


def page_down(d):
    for j in range(page_downs):
        d.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)


def click(d, func, element):
    button = func(element)
    while not button.is_displayed() or not button.is_enabled():
        d.refresh()
        button = func(element)
        time.sleep(wait_time)
    button.click()


def try_to_find_element(func, element_name):
    try:
        element = func(element_name)
        return element
    except NoSuchElementException:
        return None


def time_in_seconds(dur):
    t = 0
    mul = 1
    for d in dur[::-1]:
        t += (mul * int(d))
        mul *= 60
    return t


def specify_url(season, episode):
    return "/season/{}/episode/{}".format(season, episode)


def load_page(url, ep_index, drivers):
    global page_loaded
    global finished
    drivers[ep_index] = None
    driver = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options)
    driver.get(url)
    if ep_index == 0:
        page_loaded = True
    for i in range(page_downs):
        driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    time.sleep(wait_time)
    click(driver, driver.find_element_by_id, 'proceed')
    if ep_index == 0:
        finished = True
        while pause:
            time.sleep(1)
    drivers[ep_index] = driver
    driver.minimize_window()


def open_window(url, ep_index, drivers, season, episode, wait=0.1):
    full_url = url + '/season/{}/episode/{}'.format(season, episode)
    threading.Thread(target=load_page, args=[full_url, ep_index, drivers]).start()
    time.sleep(wait)


def play_windows(drivers, playlist, after_watch, repeat, wait=0):
    watched = 0
    current_ep = 0
    while current_ep < len(playlist):
        while drivers[current_ep] is None:
            time.sleep(1)
        if current_ep < len(playlist) - 1:
            repeat(playlist, current_ep)
        time.sleep(wait)
        d = drivers[current_ep]
        d.maximize_window()
        time.sleep(3)
        play_one_tab(d)
        watched += 1
        after_watch(watched)
        d.quit()
        current_ep += 1


def load_all_at_once(url, playlist, after_watch):
    drivers = {}
    ep_index = 0
    for season, episode in playlist:
        open_window(url, ep_index, drivers, season, episode)
        ep_index += 1
    play_windows(drivers, playlist, after_watch, do_nothing)


def load_pairs(url, playlist, after_watch):
    drivers = {}
    season, episode = playlist[0]
    open_window(url, 0, drivers, season, episode)
    repeat = lambda p, ce: open_window(url, ce + 1, drivers, p[ce + 1][0], p[ce + 1][1])
    play_windows(drivers, playlist, after_watch, repeat, wait=1)


def play_one_tab(driver):
    click(driver, driver.find_element_by_class_name, 'vjs-big-play-button')
    time.sleep(3)

    player = driver.find_element_by_id('playerDiv')

    time.sleep(2)

    while len(driver.find_elements_by_tag_name('iframe')) <= 1 \
            and '>00:00<' in re.findall('>\d\d:\d\d<',
                                        player.get_attribute('innerHTML'))[:2]:
        time.sleep(1)

    if '>00:00<' in re.findall('>\d\d:\d\d<', player.get_attribute('innerHTML'))[:2]:
        frames = driver.find_elements_by_tag_name('iframe')
        driver.switch_to.frame(frames[-1])

        while 'Skip' not in driver.page_source:
            time.sleep(1)
            driver.switch_to.default_content()
            if '>00:00<' not in re.findall('>\d\d:\d\d<',
                                           player.get_attribute('innerHTML'))[:2]:
                break
            driver.switch_to.frame(frames[-1])

        driver.switch_to.default_content()

        if '>00:00<' in re.findall('>\d\d:\d\d<', player.get_attribute('innerHTML'))[:2]:
            driver.switch_to.frame(frames[-1])

            time.sleep(2)

            w, h = pyautogui.size()

            x = w / 2.
            y = h / 2.

            pyautogui.click(int(x), int(y))

            time.sleep(1)

            sk = driver.find_element_by_xpath("//*[contains(text(),'Skip')]")

            while any(char.isdigit() for char in sk.text):
                time.sleep(1)

            sk_rect = sk.rect

            driver.switch_to.default_content()

            y_offset = driver.execute_script('return window.pageYOffset;')
            frame_location = driver.find_elements_by_tag_name('iframe')[-1].location

            scroll_offset = 100
            skip_x = frame_location['x'] + sk_rect['x'] + sk_rect['width'] / 2
            skip_y = frame_location['y'] + sk_rect['y'] - y_offset + scroll_offset
            pyautogui.click(int(skip_x), int(skip_y))

            time.sleep(2)

    video = driver.find_element_by_id('videojs_html5_api')

    video.send_keys("f")

    dur = re.findall(">\d\d:\d\d<", player.get_attribute('innerHTML'))

    end = time_in_seconds(dur[0][1:-1].split(':'))

    current_time = 0

    while current_time < end - seconds_before_to_quit:
        dur = re.findall('>\d\d:\d\d<',
                         player.get_attribute('innerHTML'))
        if dur:
            current_time = min([time_in_seconds(d[1:-1].split(':')) for d in dur[:2]])
        time.sleep(3)


def start(series, season, first_episode, num_episodes, load_at_once):

    global page_loaded
    global finished

    page_loaded = False
    finished = False

    url = get_series_url(series)

    lengths = sl.scan(series)
    playlist = memory.get_playlist(lengths, season, first_episode, num_episodes)

    update_watched_episodes = lambda w: memory.update_index(series, lengths, season, first_episode, w)

    if load_at_once:
        load_all_at_once(url, playlist, update_watched_episodes)

    else:
        load_pairs(url, playlist, update_watched_episodes)
