#!/usr/bin/env python3

from datetime import datetime

import argparse
import subprocess
import sys
import os


def clone_repo(url):
	dt_id = datetime.utcnow().strftime("%d.%m.%Y") # Форматируем текущую дату
	folder_name = f"node-js_{dt_id}" # Создаем имя папки, в которую будет склонирован репозиторий

	if folder_name in os.listdir() and len(os.listdir(folder_name)) > 0:
		subprocess.run(
			["rm", "-rf", folder_name],
			encoding="utf-8",
			check=True,
			stdout=sys.stdout)

	git_clone_reply = subprocess.run(
			["git", "clone", f"{url}.git", folder_name], # Команда для клонирования репозитория
			encoding="utf-8", # Устанавливаем кодировку
			check=True, # В случае ошибки в дочернем процессе прокидываем ошибку выше, чтобы перехватить ее в коде
			stdout=sys.stdout) # Указываем в качестве стандартного вывода вывод консоли
	
	return folder_name # Возвращаем имя папки, в которую был склонирован репозиторий


def test_app(path):
	os.chdir(path) # Переходим в директорию с склонированным репозиторием

	npm_setting_up_reply = subprocess.run(
		["npm", "install"], # Устанавливаем зависимости npm
		encoding="utf-8", # Устанавливаем кодировку
		check=True, # Прокидываем исключения вверх в случае их появления
		stdout=sys.stdout) # Вывод в консоль

	node_starting_reply = subprocess.run(
		["node", "test.js"], # Запускаем тестовый скрипт
		encoding="utf-8", # Устанавливаем кодировку
		check=True, # Прокидываем исключения вверх
		stdout=sys.stdout) # Вывод в консоль


def create_dockerfile(config):
	with open("Dockerfile", "w", encoding="utf-8") as file: # Создаем Dockerfile
		file.write(config) # Записываем в него конфигурацию из аргумента


def build_image(image_name):
	# Конфигурация нашего Dockerfile
	config = """FROM node:latest AS builder

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 8080

CMD ["npm", "start"]

"""
	
	create_dockerfile(config) # Создаем Dockerfile и записываем в него конфиг

	image_build_reply = subprocess.run(
		["docker", "buildx", "build", "--tag", image_name, "."], # Создаем Docker-образ с именем
		encoding="utf-8", # Устанавливаем кодировку
		check=True, # Прокидываем исключения вверх
		stdout=sys.stdout) # Вывод в консоль


def run_container_as_a_service(image_name):
	container_as_a_service_reply = subprocess.run(
		["docker", "run", "-d", image_name], # Запускаем контейнер из созданного образа
		encoding="utf-8", # Устанавливаем кодировку
		check=True, # Прокидываем вверх исключение
		stdout=sys.stdout) # Вывод в консоль


def main():
	if os.geteuid() != 0:
		print("[-] This script should be run as root !") # Для работы с Docker нужны root-права
		sys.exit(-1)

	# Будем передавать ссылку на репозиторий как аргумент в командной строке
	parser = argparse.ArgumentParser(
			prog="2_simple_ci_script",
			description="Script that clones a repo from GitHub, checks a perfomance of an app, builds a Docker image and runs it as a service")
	parser.add_argument("url", metavar="U", type=str, help="The URL of a GitHub repo")
	args = parser.parse_args()

	# Запускаем последовательность действий, перехватываем возможные исключения и выводим их на печать
	try:
		name = clone_repo(args.url)
		test_app(name)
		build_image(name)
		run_container_as_a_service(name)
	except Exception as e:
		print(e)
		sys.exit(-1)


if __name__ == "__main__":
	main()
