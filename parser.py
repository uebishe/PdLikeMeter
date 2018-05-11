import requests
import re
import os.path
import pickle
from collections import OrderedDict
from bs4 import BeautifulSoup

topic_id = 214632
filename = 'cache/topic' + str(topic_id) + '.p'
base_url = 'https://prodota.ru/forum/index.php?showtopic=' + str(topic_id)
cookies = {'mobileBrowser': '1',
           'language': '2'}
force_load = False

pages = []

if force_load or not os.path.isfile(filename):
    params = {'view': 'getlastpost'}
    r = requests.get(base_url, params=params, cookies=cookies)
    last_page = r.text
    total_pages = re.compile('(?<=page=)\d+').search(r.url).group()

    for page_number in range(1, int(total_pages)):
        params = {'page': str(page_number)}
        r = requests.get(base_url, params=params, cookies=cookies)
        pages.append(r.text)
    pages.append(last_page)

    with open(filename, 'wb') as f:
        pickle.dump(pages, f)

if not pages:
    with open(filename, 'rb') as f:
        pages = pickle.load(f)

users = {}

for page in pages:
    soup = BeautifulSoup(page, 'html.parser')
    for post in soup.find_all(class_='topic_reply'):
        username_tag = post.find(attrs={'title': 'Просмотреть профиль'})
        username = str(username_tag.string) if username_tag else str(post.find(class_='ddk33_post_info')['post-author'])
        like_bar = post.find(class_='ipsLikeBar_info')
        like_str = str(like_bar.string).strip() if like_bar else ''
        like_str = like_str if like_str else '0'
        like_count = int(re.compile('\d+').search(like_str).group())
        users[username] = (users[username] + like_count) if username in users else like_count

sorted_users = OrderedDict(sorted(users.items(), key=lambda x: x[1], reverse=True))
for username in sorted_users:
    print(username + ': ' + str(sorted_users[username]) + ' like(s)')