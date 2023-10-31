#!/usr/bin/env python3

from elasticsearch7 import AsyncElasticsearch

import asyncio
import aiohttp
import asyncpg


async def check_nodejs(url):
	try:
		response = None
		async with aiohttp.ClientSession() as session: # Устанавливаем соединение с сервером
			response = await session.get(url, raise_for_status=True) # Отправляем GET-запрос к странице и генерируем исключение в случае неуспешного кода статуса
		return response.text, True # Возвращаем текст ответа и "Тру"
	except Exception as e: # Перехватываем исключения
		return e, False # Возвращаем объект исключения и "Фолс"


async def check_postgres(**kwargs):
	values = None
	try:
		# Подключаемся к БД
		conn = await asyncpg.connect(
				database=kwargs["database"],
				user=kwargs["user"],
				password=kwargs["password"],
				host=kwargs["host"],
				port=kwargs["port"],
			)
		values = await conn.fetch("SELECT * FROM pg_catalog.pg_user") # Выполняем простой запрос к БД
		return values, True # Возвращаем результаты запроса и "Тру"
	except Exception as e: # Перехватываем исключения
		return e, False # Возвращаем исключение и "Фолс"


async def check_elastic(user, password, host, port):
	try:
		info = None
		async with AsyncElasticsearch(f"http://{user}:{password}@{host}:{port}") as es: # Подключаемся к Elasticsearch
			info = await es.info() # Получаем информацию о системе
		return info, True # Возвращаем сведения о системе и "Тру"
	except Exception as e: # Перехватываем исключения
		return e, False # Возвращаем исключение и "Фолс"


async def main():
	# Создаем задачи для асинхронного выполнения
	nodejs_check_task = asyncio.create_task(check_nodejs("http://localhost:3000"))
	postgres_check_task = asyncio.create_task(check_postgres(
								database="testdb",
								user="testuser",
								password="testpassword",
								host="localhost",
								port="5432",
							))
	elasticsearch_check_task = asyncio.create_task(check_elastic("elastic", "testpassword", "localhost", "9200"))

	# Выполняем задачи асинхронно и получаем возвращенные задачами значения
	is_nodejs_healthy = await nodejs_check_task
	is_postgres_healthy = await postgres_check_task
	is_elasticsearch_healthy = await elasticsearch_check_task

	# Пишем результаты проверок работоспособности
	print(is_nodejs_healthy[0])
	(sign, result) = ("*", "passed") if is_nodejs_healthy[1] else ("-", "failed")
	print(f"[{sign}] NodeJS check {result}\n")

	print(is_postgres_healthy[0])
	(sign, result) = ("*", "passed") if is_postgres_healthy[1] else ("-", "failed")
	print(f"[{sign}] PostgreSQL check {result}\n")

	print(is_elasticsearch_healthy[0])
	(sign, result) = ("*", "passed") if is_elasticsearch_healthy[1] else ("-", "failed")
	print(f"[{sign}] Elasticsearch check {result}\n")


if __name__ == "__main__":
	asyncio.run(main())
