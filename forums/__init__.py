
# hypixel forums.py v0.13

from bs4 import BeautifulSoup
import time
from . import aiocloudscraper
import aiohttp
import asyncio

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'

s = aiocloudscraper.AsyncCloudScraper()

'''
User data:
- id (forum id)
- title (forum title, new member, well known, etc)
- name (forum username)
- follower_count (forum follower acount)
- messages (total number of forum posts)
'''

reaction_id_to_names = {
	'': 'All',
	'1': 'Like',

	'3': 'Funny',
	'4': 'Creative',
	'5': 'Dislike',

	'7': 'Agree',
	'8': 'Disagree',
	'9': 'Useful',
	'10': 'Mod Emerald',
	'11': 'Hype Train',
	'12': 'Admin Diamond',
	'13': 'Helper Lapis',
	'14': 'Wat',
	'15': 'Bug',
}

def avatar_from_id(user_id):
	id_start = str(user_id)[:-3]
	return f'https://hypixel.net/data/avatars/l/{id_start}/{user_id}.jpg'

async def get_recent_posts(forum='skyblock', page=1):
	forum_ids = {
		'skyblock': 157,
		'skyblock-patch-notes': 158,
		'news-and-announcements': 4,
		'official-hypixel-minecraft-server': 'official-hypixel-minecraft-server',
		'hypixel-server-discussion': 'official-hypixel-minecraft-server'
	}

	forum_id = forum_ids.get(forum.lower().replace(' ', '-'), forum)
	print(f'https://hypixel.net/forums/{forum_id}/page-{page}')
	r = await s.get(f'https://hypixel.net/forums/{forum_id}/page-{page}')
	url_page_part = str(r.url).split('/')[-1]
	# Reached max page
	if url_page_part.startswith('page-'):
		if url_page_part[5:] != str(page):
			return {}
	forum_listing_html = await r.text()
	soup = BeautifulSoup(forum_listing_html, features='html5lib')
	bs4_post_lists = soup.findAll(class_='structItem-cell--main')

	posts = []
	for post_main_el in bs4_post_lists:
		title = post_main_el.find(class_='structItem-title').text.strip()
		url = post_main_el.find(class_='structItem-title').a['href']
		author_id = int(post_main_el.find(class_='username')['data-user-id'])
		author_name = post_main_el.find(class_='username').text.strip()
		created_time_string = post_main_el.find(class_='u-dt')['data-time']
		created_time = int(created_time_string)
		post_id = url.split('/')[-2].split('.')[-1]

		last_message_author_id = int(post_main_el.findAll(class_='username')[-1]['data-user-id'])
		last_message_author_name = post_main_el.findAll(class_='username')[-1].text.strip()

		is_recent = (time.time() - created_time) < 60 * 60 * 24 * 2

		posts.append({
			'title': title,
			'url': url,
			'author': {
				'id': int(author_id),
				'name': author_name,
			},
			'last_message_author': {
				'id': int(last_message_author_id),
				'name': last_message_author_name
			},
			'time': created_time,
			'is_recent': is_recent,
			'id': int(post_id)
		})
	return posts

async def get_thread(post_id, is_thread=True):
	post_url = f'https://hypixel.net/threads/{post_id}/'
	r = await s.get(post_url)
	forum_post_html = await r.text()
	soup = BeautifulSoup(forum_post_html, features='html5lib')
	post_element = soup.find(class_='message-inner')
	if not post_element: return
	body_text = post_element.find(class_='message-body').text.strip()
	body_image_element = post_element.find(class_='message-body').find('img')
	if body_image_element:
		body_image = body_image_element['src']
	else:
		body_image = None

	user_name = post_element.find(class_='username').text.strip()
	user_id = post_element.find(class_='username')['data-user-id'].strip()
	user_title = post_element.find(class_='userTitle').text.strip()
	user_avatar_url = avatar_from_id(user_id)
	user_url = f'https://hypixel.net/members/{user_id}'


	post_title = soup.find(class_='p-title-value').text.strip()

	created_time_string = soup.find(class_='u-dt')['data-time']
	created_time = int(created_time_string)

	is_recent = (time.time() - created_time) < 60 * 60 * 24 * 2


	return {
		'body': body_text,
		'title': post_title,
		'id': int(post_id),
		'is_recent': is_recent,
		'url': str(r.url),
		'image': body_image,
		'author': {
			'name': user_name,
			'url': user_url,
			'id': user_id,
			'title': user_title,
			'avatar_url': user_avatar_url,
		}
	}


