import requests
from bs4 import BeautifulSoup

import memory


def get_season_start(url, season):
    episode = 1
    full_url = url + '/season/{}'.format(season)
    res_url = requests.get(full_url).url
    if full_url != res_url:
        return -1
    full_url = url + '/season/{}/episode/{}'.format(season, episode)
    res_url = requests.get(full_url).url
    while res_url != res_url:
        full_url = url + '/season/{}/episode/{}'.format(season, episode)
        res_url = requests.get(full_url).url
        episode += 1
    return episode


def get_seasons_lengths(url):
    try:
        main_res = requests.get(url)
        main_soup = BeautifulSoup(main_res.text, "html.parser")
        main_seasons_found = main_soup.find('ul', id='season')
        seasons = [int(e['data-season']) for e in main_seasons_found.find_all('li')]
        series_episodes = []
        for season in seasons:
            s_url = url + '/season/{}'.format(season)
            response = requests.get(s_url)
            soup = BeautifulSoup(response.text, "html.parser")
            found = soup.find('ul', id='episode')
            episodes = [int(e['data-episode']) for e in found.find_all('li')]
            series_episodes.append(episodes)
        lengths = []
        season_index = 1
        for ep_list in series_episodes:
            if not ep_list:
                continue
            i = 1
            while i < len(ep_list):
                lengths.append(season_index)
                last = ep_list[i - 1]
                lengths.append(ep_list[i - 1])
                while i < len(ep_list):
                    if ep_list[i] != ep_list[i - 1] + 1:
                        i += 1
                        break
                    last = ep_list[i]
                    i += 1
                lengths.append(last)
            season_index += 1
    except:
        return None
    return lengths


def scan(series):
    seasons_file = open('seasons.csv', 'r')
    content = seasons_file.readlines()
    for i in range(len(content)):
        line = content[i].split(',')
        if series == line[0]:
            return list(map(int, line[1:]))
    seasons_file.close()
    url = memory.series_dict[series]
    lengths = []
    if url:
        lengths = get_seasons_lengths(url)
        if lengths is None:
            return None
        content.append(series + ',' + ','.join(map(str, lengths)) + '\n')
    with open('seasons.csv', 'w') as file:
        file.write(''.join(content))
    return lengths


def delete_entry(series):
    file = open('seasons.csv', 'r')
    content = file.readlines()
    for i in range(len(content)):
        line = content[i].split(',')
        if line[0] == series:
            content[i] = ''
    file.close()
    with open('seasons.csv', 'w') as seasons_file:
        seasons_file.write(''.join(content))
