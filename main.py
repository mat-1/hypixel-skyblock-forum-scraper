import forums
import asyncio
import time
import json

loop = asyncio.get_event_loop()

with open('output.json', 'r') as f:
	try:
		data = json.loads(f.read())
	except json.decoder.JSONDecodeError:
		print('no data')
		data = []

existing_titles = set([d['title'] for d in data])


async def main():
	first_page = True
	page_posts = []
	page_number = 0

	while True:
		while page_posts or first_page:
			page_number += 1
			page_start_time = time.time()
			page_posts = await forums.get_recent_posts('skyblock', page=page_number)
			page_end_time = time.time()
			first_page = False

			for post in page_posts:
				if post['title'] in existing_titles:
					print('already seen post', post['title'])
					continue
				thread_start_time = time.time()
				thread = await forums.get_thread(post['id'])
				thread_end_time = time.time()
				thread_load_time = thread_end_time - thread_start_time
				if thread_load_time < 1:
					await asyncio.sleep(1 - thread_load_time)
				if not thread: continue
				if thread['title'] not in existing_titles:
					print('added post', thread['title'])
					data.append({
						'title': thread['title'],
						'body': thread['body']
					})

			print('gotten page')
			page_load_time = page_end_time - page_start_time
			if page_load_time < 2:
				await asyncio.sleep(2 - page_load_time)

			try:
				with open('output.json', 'w') as f:
					f.write(json.dumps(data, indent=2))
			except OSError:
				print('\nfailed writing??? wacky\n')
			print(len(data), page_number)
		print('being ratelimited :( trying again in a minute')
		await asyncio.sleep(60)
		page_number -= 1
		first_page = True

loop.run_until_complete(main())
