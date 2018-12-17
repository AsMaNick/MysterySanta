﻿import telebot
import datetime
from telebot import types
import json
import numpy as np
from collections import defaultdict
from groups import *
import os


global last_command, group_names
last_command = defaultdict(str)
group_names = defaultdict(str)
passwords = defaultdict(str)


if not os.path.exists('data/all_users.json'):
	print('{"all_users": []}', file=open('data/all_users.json', 'w'))
if not os.path.exists('data/users.json'):
	print('{"users": []}', file=open('data/users.json', 'w'))
if not os.path.exists('data/groups.json'):
	print('{"groups": []}', file=open('data/groups.json', 'w'))
		
help_text = open('data/help.txt', 'r').read()
token = '787172870:AAGjJ-8U7avv2JaJS9xE8Hg-HN7msjbZBP4'
bot = telebot.TeleBot(token)


def has_user(chat_id):
	users = json.load(open('data/users.json', 'r'))
	for u in users['users']:
		if u['chat_id'] == chat_id:
			return True
	return False
	
	
def add_user(user):
	users = json.load(open('data/users.json', 'r'))
	users['users'].append(user)
	json.dump(users, open('data/users.json', 'w'))
	
	
def delete_user(chat_id):
	users = json.load(open('data/users.json', 'r'))
	for i in range(len(users['users'])):
		if users['users'][i]['chat_id'] == chat_id:
			del users['users'][i]
			break
	json.dump(users, open('data/users.json', 'w'))
			
			
def log_message(message):
	forward_message_to_me(message)
	
	
@bot.message_handler(commands=['start', 'help'])
def start(message):
	log_message(message)
	global last_command
	last_command[message.chat.id] = 'help'
	print(help_text)
	bot.send_message(message.chat.id, help_text, parse_mode='html')


@bot.message_handler(commands=['create_group'])
def create_group(message):
	log_message(message)
	global last_command
	last_command[message.chat.id] = 'create_group'
	if has_user(message.chat.id):
		bot.send_message(message.chat.id, 'Вы уже в группе.', parse_mode='html')
	else:
		bot.send_message(message.chat.id, 'Введите имя группы:', parse_mode='html')
		
		
@bot.message_handler(commands=['join_group'])
def join_group(message):
	log_message(message)
	global last_command
	last_command[message.chat.id] = 'join_group'
	if has_user(message.chat.id):
		bot.send_message(message.chat.id, 'Вы уже в группе.', parse_mode='html')
		last_command[message.chat.id] = 'text'
	else:
		bot.send_message(message.chat.id, 'Введите имя группы:', parse_mode='html')
	
	
@bot.message_handler(commands=['leave_group'])
def leave_group(message):
	log_message(message)
	global last_command
	last_command[message.chat.id] = 'leave_group'
	if has_user(message.chat.id):
		delete_user(message.chat.id)
		bot.send_message(message.chat.id, 'Вы были успешно удалены из группы.', parse_mode='html')
	else:
		bot.send_message(message.chat.id, 'Вы и так не в группе.', parse_mode='html')
		
		
@bot.message_handler(commands=['list_users'])
def list_users(message):
	log_message(message)
	global last_command
	last_command[message.chat.id] = 'list_users'
	if not has_user(message.chat.id):
		bot.send_message(message.chat.id, 'Вы должны создать, или вступить в какую-то группу, чтобы иметь возможность просмотаривать список ее участников.', parse_mode='html')
		last_command[message.chat.id] = 'text'
	else:
		num = 0
		group_name = get_group_name(message.chat.id)
		reply = 'Список участников группы {}:\n'.format(group_name)
		users = load_group(group_name)
		for num, user in enumerate(users):
			reply += str(1 + num) + ') ' + user['name'] + '\n'
		bot.send_message(message.chat.id, reply, parse_mode='html')
	
	
@bot.message_handler(commands=['generate'])
def generate(message):
	log_message(message)
	global last_command
	last_command[message.chat.id] = 'generate'
	if not has_user(message.chat.id):
		bot.send_message(message.chat.id, 'Вы должны создать, или вступить в какую-то группу, чтобы иметь возможность генерировать распределение ее участников.', parse_mode='html')
		last_command[message.chat.id] = 'text'
	else:
		bot.send_message(message.chat.id, 'Введите пароль:', parse_mode='html')
	
	
def bad_permutation(p):
	return len(p) > 1 and np.any(p == np.arange(len(p)))
	
	
def generate_pairs(group_name):
	users = load_group(group_name)
	p = np.random.permutation(len(users))
	while bad_permutation(p):
		p = np.random.permutation(len(users))
	for i in range(len(users)):
		target = p[i]
		bot.send_message(users[i]['chat_id'], 'От вас ждет подарка ' + users[target]['name'] + ' :)', parse_mode='html')
		bot.forward_message(users[i]['chat_id'], users[target]['chat_id'], users[target]['message_id'])
		
		
def get_name(user):
	res = ''
	if user.first_name:
		res += user.first_name
	if user.last_name:
		if res != '':
			res += ' '
		res += user.last_name
	return res
	
	
@bot.message_handler(content_types=['text'])
def reply_all_messages(message):	
	global last_command
	o_last_command = last_command[message.chat.id]
	last_command[message.chat.id] = 'text'
	log_message(message)
	if o_last_command == 'create_group':
		if has_group(message.text):
			bot.send_message(message.chat.id, 'Группа с таким названием уже существует.', parse_mode='html')
		elif not correct_name(message.text):
			bot.send_message(message.chat.id, 'Введете корректное название группы. Название может состоять только из англиских букв и цифр.', parse_mode='html')
		else:
			bot.send_message(message.chat.id, 'Введите секретный пароль, с помощью которого вы сможете сгенерировать распределение участников:', parse_mode='html')
			last_command[message.chat.id] = 'create_group1'
			group_names[message.chat.id] = message.text
	elif o_last_command == 'create_group1':
		if not correct_name(message.text):
			bot.send_message(message.chat.id, 'Введете корректный пароль. Пароль может состоять только из англиских букв и цифр.', parse_mode='html')
			last_command[message.chat.id] = 'create_group1'
		else:
			bot.send_message(message.chat.id, 'Напишите письмо вашему тайному Санте:', parse_mode='html')
			last_command[message.chat.id] = 'create_group2'
			passwords[message.chat.id] = message.text
	elif o_last_command == 'join_group':
		if not has_group(message.text):
			bot.send_message(message.chat.id, 'Группы с таким названием не существует.', parse_mode='html')
		else:
			bot.send_message(message.chat.id, 'Напишите письмо вашему тайному Санте:', parse_mode='html')
			last_command[message.chat.id] = 'join_group1'
			group_names[message.chat.id] = message.text
	elif o_last_command == 'create_group2' or o_last_command == 'join_group1':
		user = {'chat_id': message.chat.id, 
				'message_id': message.message_id,
				'name': get_name(message.from_user),
				'group_name': group_names[message.chat.id]}
		add_user(user)
		if o_last_command == 'join_group1':
			bot.send_message(message.chat.id, 'Вы были успешно добавлены в группу!', parse_mode='html')
		else:
			group = {'group_name': group_names[message.chat.id],
					 'password': passwords[message.chat.id]}
			add_group(group)
			bot.send_message(message.chat.id, 'Вы успешно создали группу! Зовите скорее своих друзей :)', parse_mode='html')
	elif o_last_command == 'generate':
		if message.text == get_group_password(get_group_name(message.chat.id)):
			generate_pairs(get_group_name(message.chat.id))
		else:
			bot.send_message(message.chat.id, 'Неверный пароль. Если вы не знаете пароль, свяжитесь с создателем группы.', parse_mode='html')
	else:
		bot.send_message(message.chat.id, 'Неизвестная команда. Обратите внимание, что вводить команды нужно обязательно с символом "/". Для просмотра списка допустимых команд выполните /help.', parse_mode='html')
	
	
def is_first_message(chat_id):
	all_users = json.load(open('data/all_users.json', 'r'))
	for user in all_users['all_users']:
		if user['chat_id'] == chat_id:
			return False
	return True
	
	
def forward_message_to_me(message):
	if is_first_message(message.chat.id):
		all_users = json.load(open('data/all_users.json', 'r'))
		user = {'user_name': get_name(message.from_user),
				'chat_id': message.chat.id}
		all_users['all_users'].append(user)
		json.dump(all_users, open('data/all_users.json', 'w'))
	my_chat_id = 273440998
	bot.forward_message(my_chat_id, message.chat.id, message.message_id)


if __name__ == '__main__':
	while True:
		try:
			print('Start polling')
			bot.polling(none_stop=True)
		except Exception as E:
			print('Some exception while polling')
			print(E)