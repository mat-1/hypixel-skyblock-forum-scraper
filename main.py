
import forums
import asyncio
import time
import json

loop = asyncio.get_event_loop()

with open('output.json', 'r') as f:
	try:
		data = json.loads(f.read())
	except json.decoder.JSONDecodeError:
		data = []

existing_titles = set([d['title'] for d in data])

async def main():
	first_page = True
	page_posts = []
	page_number = 0
	data = []
	
	while page_posts or first_page:
		page_number += 1
		page_start_time = time.time()
		page_posts = await forums.get_recent_posts('skyblock', page=page_number)
		page_end_time = time.time()
		first_page = False

		for post in page_posts:
			thread = await forums.get_thread(post['id'])
			page_load_time = page_end_time - page_start_time
			if page_load_time < .5:
				await asyncio.sleep(.5 - page_load_time)
			if not thread: continue
			if thread['title'] not in existing_titles:
				data.append({
					'title': thread['title'],
					'body': thread['body']
				})

		print('gotten page')
		page_load_time = page_end_time - page_start_time
		if page_load_time < .5:
			await asyncio.sleep(.5 - page_load_time)

		if page_number % 10 == 0:
			with open('output.json', 'w') as f:
				f.write(json.dumps(data))
			print(len(data), page_number)
	
loop.run_until_complete(main())