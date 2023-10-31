#!/usr/bin/env python3

from elasticsearch import AsyncElasticsearch

import aiohttp
import asyncpg


async def check_nodejs(url):
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(url, raise_for_status=True) as response:
				resp_text = await resp.text()
				return bool(resp_text)
	except Exception as e:
		return False
	else:
		return True


async def check_postgres(**kwargs):
	conn = await asyncpg.connect(
		database=kwargs["database"],
		user=kwargs["user"],
		password=kwargs["password"],
		host=kwargs["host"],
		port=kwargs["port"],
	)

	try:
		values = await conn.fetch(
			"SELECT * FROM pg_catalog.pg_user",
			10,
		)
		await conn.close()
		return bool(values)
	except Exception as e:
		return False
	else:
		return True


async def check_elastic(url):
	try:
		es = AsyncElasticsearch([url], http_auth=("elastic", "testpassword"))

		
