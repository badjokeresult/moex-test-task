#!/usr/bin/env python3

from elasticsearch7 import Elasticsearch

import psycopg2
import requests
import warnings


def check_nodejs(url):
	try:
		response = requests.get(url) # Выполняем GET-запрос к приложению
		response.raise_for_status() # Если код статуса равен 4xx или 5xx, то вызываем исключение
		print(response.text) # Пишем текст ответа от сервера, чтобы в случае ошибки понять, в чем может быть проблема
		return True
	except Exception as e: # Перехватываем все исключения и снова вызываем его
		print(e) # Пишем текст исключения, чтобы понять, где произошла ошибка
		return False


def check_postgres(**kwargs):
	try:
		response = None
		# Подключаемся к БД
		conn = psycopg2.connect(database=kwargs["database"], 
        	                	host=kwargs["host"],
            	            	user=kwargs["user"],
                	        	password=kwargs["password"],
                    	    	port=kwargs["port"])
		with conn.cursor() as cursor: # Создаем объект курсора
			cursor.execute("SELECT * FROM pg_catalog.pg_user") # Пробуем выполнить простой запрос
			response = cursor.fetchmany(10) # Получаем первые 10 записей из запроса
		print(response) # Пишем первые 10 записей или что-либо другое, что возвращает БД (для упрощения багфикса)
		return True
	except Exception as e: # Перехватываем все исключения
		print(e) # Пишем текст исключения для упрощения багфикса
		return False


def check_elastic(**kwargs):
	user, password, host, port = kwargs["user"], kwargs["password"], kwargs["host"], kwargs["port"]
	try:
		es = Elasticsearch(f"http://{user}:{password}@{host}:{port}") # Подключаемся к elasticsearch
		info = None
		with warnings.catch_warnings(record=True) as warns: # Перехватываем предупреждения и пишем их
			info = es.info() # Пробуем получить информацию о системе
		print(info) # Пишем инфу о системе или что-то другое, что она отдала
		return True
	except Exception as e: # Перехватываем исключения
		print(e) # Пишем перехваченные исключения
		return False


def main():
	# Проверяем NodeJS
	(sign, result) = ("*", "passed") if check_nodejs("http://localhost:3000") else ("-", "failed")
	print(f"[{sign}] NodeJS check {result}\n")

	# Проверяем PostgreSQL
	(sign, result) = ("*", "passed") if check_postgres(database="testdb", host="localhost", user="testuser", password="testpassword", port="5432") else ("-", "failed")
	print(f"[{sign}] PostgreSQL check {result}\n")

	# Проверяем Elasticsearch
	(sign, result) = ("*", "passed") if check_elastic(user="elastic", host="localhost", password="testpassword", port="9200") else ("-", "failed")
	print(f"[{sign}] Elasticsearch check {result}\n")


if __name__ == "__main__":
	main()
