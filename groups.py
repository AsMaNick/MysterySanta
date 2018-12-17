import json


def get_group_name(chat_id):
	users = json.load(open('data/users.json', 'r'))['users']
	for i in range(len(users)):
		if users[i]['chat_id'] == chat_id:
			return users[i]	['group_name']
			
	
def load_group(group_name):
	users = json.load(open('data/users.json', 'r'))['users']
	res = []
	for user in users:
		if user['group_name'] == group_name:
			res.append(user)
	return res
	
	
def has_group(group_name):
	groups = json.load(open('data/groups.json', 'r'))['groups']
	for group in groups:
		if group['group_name'] == group_name:
			return True
	return False
	
	
def ok_character(c):
	return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or ('0' <= c <= '9')
	
	
def correct_name(name):
	for c in name:
		if not ok_character(c):
			return False
	return True
	
	
def add_group(group):
	groups = json.load(open('data/groups.json', 'r'))
	groups['groups'].append(group)
	json.dump(groups, open('data/groups.json', 'w'))
	

def get_group_password(group_name):
	groups = json.load(open('data/groups.json', 'r'))['groups']
	for group in groups:
		if group['group_name'] == group_name:
			return group['password']
	return 'undefined'