def get_playlist(seasons_lengths, curr_season, first_episode, num_episodes):
    playlist = []
    episode = first_episode
    season = curr_season
    for i in range(num_episodes):
        playlist.append((season, episode))
        season, episode = next_episode(seasons_lengths, season, episode)
    return playlist


def get_next_episode(series):
    index = open('index.csv', 'r')
    for line in index.readlines():
        attributes = line.split(',')
        if attributes[0] == series:
            return int(attributes[1]), int(attributes[2])
    return 1, 1


def update_index(series, seasons_lengths, curr_season, first_episode, num_episodes):
    index = open('index.csv', 'r')
    content = index.readlines()
    index.close()
    episode = first_episode
    season = curr_season
    for i in range(num_episodes):
        season, episode = next_episode(seasons_lengths, season, episode)
    found = False
    for i in range(len(content)):
        attributes = content[i].split(',')
        if attributes[0] == series:
            content[i] = ','.join([series, str(season), str(episode)]) + '\n'
            found = True
            break
    if not found:
        content.append(','.join([series, str(season), str(episode)]) + '\n')
    with open('index.csv', 'w') as file:
        file.write(''.join(content))


def next_episode(season_lengths, season, episode):
    seasons = season_lengths[::3]
    starts = season_lengths[1::3]
    ends = season_lengths[2::3]
    for i in range(len(seasons)):
        if season == seasons[i] and episode < ends[i]:
            return season, episode + 1
        elif season == seasons[i] and episode == ends[i]:
            if i == len(seasons) - 1:
                return 1, 1
            return seasons[i + 1], starts[i + 1]
    return 1, 1


def get_series_dictionary():
    with open('series.csv', 'r') as series:
        series_d = dict()
        for line in series.readlines():
            attributes = line.split(',')
            if attributes[1][-1] == '\n':
                attributes[1] = attributes[1][:-1]
            series_d[attributes[0]] = attributes[1]
        return series_d


def update_series_dict():
    global series_dict
    series_dict = get_series_dictionary()


series_dict = get_series_dictionary()
