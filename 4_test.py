#!/usr/bin/env python3

from elasticsearch7 import Elasticsearch

import psycopg2
import requests


def check_nodejs(url):
	try:
		response = requests.get(url) # Выполняем GET-запрос к приложению
		response.raise_for_status() # Если код статуса равен 4xx или 5xx, то вызываем исключение
	except requests.exceptions.HTTPError:
		print("[-] NodeJS works, but returns a bad status code") # Перехватываем исключение о ошибочном статусе и возвращаем False
		return False
	except requests.exceptions.ConnectionError: # Перехватываем ошибку невозможности подключения и возвращаем False
		print("[-] Unable to connect to NodeJS")
		return False
	except Exception as e: # Перехватываем все остальные исключения и снова вызываем его
		print("[-] Something went wrong during perfomance check")
		raise e
	else: # Если не было исключений, то пишем об успешности и возвращаем True
		print("[*] NodeJS perfomance check is successful")
		return True


def check_postgres(**kwargs):
	try:
		# Подключаемся к БД
		conn = psycopg2.connect(database=kwargs["database"], 
        	                	host=kwargs["host"],
            	            	user=kwargs["user"],
                	        	password=kwargs["password"],
                    	    	port=kwargs["port"])
		cursor = conn.cursor() # Создаем объект курсора
		cursor.execute("SELECT * FROM pg_catalog.pg_user") # Пробуем выполнить простой запрос
	except psycopg2.OperationalError: # Перехватываем ошибку подключения
		print("[-] Unable to connect to PostgreSQL")
		return False
	except Exception as e: # Перехватываем прочие ошибки
		print("[-] Something went wrong during perfomance check")
		raise e
	else:
		print("[*] PostgreSQL perfomance check is successful")
		return True


def check_elastic(url):
	# Подключаемся к Elasticsearch
	es = Elasticsearch(
		hosts=[url],
		basic_auth=("elastic", "testpassword"),
	)

	try:
		if not es.cluster.health(): # Пытаемся узнать состояние кластера
			print("[-] Unable to connect to Elasticsearch")
			return False
	except Exception as e: 
		print("[-] Something went wrong during perfomance check")
		raise e
	else:
		print("[*] Elasticsearch perfomance check is successful")
		return True


def main():
	# Проверяем NodeJS
	if check_nodejs("http://localhost:3000"):
		print("[*] NodeJS check passed\n")
	else:
		print("[-] NodeJS check failed\n")

	# Проверяем PostgreSQL
	if check_postgres(database="testdb", host="localhost", user="testuser", password="testpassword", port="5432"):
		print("[*] PostgreSQL check passed\n")
	else:
		print("[-] PostgreSQL check failed\n")

	# Проверяем Elasticsearch
	if check_elastic("http://localhost:9200"):
		print("[*] Elasticsearch check passed\n")
	else:
		print("[-] Elasticsearch check failed\n")


if __name__ == "__main__":
	main()
