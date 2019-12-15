import random
import telebot
import numpy as np
from database import *
from telebot import types
from collections import defaultdict


global last_command, group_names
last_command = defaultdict(str)
group_names = defaultdict(str)
passwords = defaultdict(str)
        
help_text = open('data/help.txt', 'r').read()
token = open('data/token.txt', 'r').read()
personal_chats = list(map(int, open('data/personal_chats.txt', 'r').read().split(' ')))
bot = telebot.TeleBot(token)


def get_group(chat_id):
    return User.get(User.chat_id == chat_id).group
            
    
def get_group_users(group_name):
    group = Group.get(Group.name == group_name)
    if group:
        return [user for user in group.users]
    return []
    
    
def has_group(group_name):
    return Group.get_or_none(Group.name == group_name) is not None
    
    
def ok_character(c):
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or ('0' <= c <= '9') or c == ' '
    
    
def correct_name(name):
    for c in name:
        if not ok_character(c):
            return False
    return True

    
def user_in_group(chat_id):
    user = User.get_or_none(User.chat_id == chat_id)
    if user is not None:
        return user.group is not None
    return False
    
    
def delete_user_from_group(chat_id):
    user = User.get(User.chat_id == chat_id)
    user.group = None
    user.save()
    
    
def is_first_message(chat_id):
    if chat_id < 0:
        return False
    return User.get_or_none(User.chat_id == chat_id) is None
    
    
@bot.message_handler(commands=['notify_user'])
def notify_user(message):
    try:
        command, chat_id, *texts = message.text.split()
        text = ' '.join(texts)
        try:
            bot.send_message(chat_id, text, parse_mode='html')
            bot.send_message(message.chat.id, 'User was notified', parse_mode='html')
        except Exception as E:
            bot.send_message(message.chat.id, str(E), parse_mode='html')
    except Exception as E:
        bot.send_message(message.chat.id, 'Incorrect arguments', parse_mode='html')
    

def happy_new_year():
    def generate_wish():
        all_wishes = ['счастья', 
                      'здоровья', 
                      'творческого вдохновления', 
                      'ярких впечатлений', 
                      'радостных эмоций', 
                      'удачи', 
                      'исполнения заветных желаний']
        wishes = random.sample(all_wishes, 3)
        s = 'Команда тайного Санты поздравляет вас с Новым годом и желает вам '
        s += wishes[0] + ', ' + wishes[1] + ' и ' + wishes[2] + '! 🎄🎁'
        return s
        
    my_chat_id = 273440998
    total = 0
    for user in User.select():
        wish = generate_wish()
        try:
            bot.send_message(user.chat_id, wish, parse_mode='html')
            bot.send_message(my_chat_id, str(user.chat_id) + ') ' + user.name + ' ' + wish, parse_mode='html')
            total += 1
        except Exception as e:
            bot.send_message(my_chat_id, 'Can not notify ' + str(user.chat_id) + ') ' + user.name + ' ' + str(e), parse_mode='html')
    bot.send_message(my_chat_id, str(total), parse_mode='html')
            
            
def log_message(message):
    forward_message_to_me(message)
    
    
def ignore_message_from_group(message):
    if message.chat.id < 0:
        bot.send_message(message.chat.id, 'Я отвечаю только на личные сообщения. Жду каждого из участников группы :)', parse_mode='html')
        return True
    return False
    
@bot.message_handler(commands=['start', 'help'])
def start(message):
    log_message(message)
    global last_command
    last_command[message.chat.id] = 'help'
    bot.send_message(message.chat.id, help_text, parse_mode='html')


@bot.message_handler(commands=['create_group'])
def create_group(message):
    log_message(message)
    if ignore_message_from_group(message):
        return
    global last_command
    last_command[message.chat.id] = 'create_group'
    if user_in_group(message.chat.id):
        bot.send_message(message.chat.id, 'Вы уже в группе.', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Введите имя группы:', parse_mode='html')
        
        
@bot.message_handler(commands=['join_group'])
def join_group(message):
    log_message(message)
    if ignore_message_from_group(message):
        return
    global last_command
    last_command[message.chat.id] = 'join_group'
    if user_in_group(message.chat.id):
        bot.send_message(message.chat.id, 'Вы уже в группе.', parse_mode='html')
        last_command[message.chat.id] = 'text'
    else:
        bot.send_message(message.chat.id, 'Введите имя группы:', parse_mode='html')
    
    
@bot.message_handler(commands=['leave_group'])
def leave_group(message):
    log_message(message)
    if ignore_message_from_group(message):
        return
    global last_command
    last_command[message.chat.id] = 'leave_group'
    if user_in_group(message.chat.id):
        delete_user_from_group(message.chat.id)
        bot.send_message(message.chat.id, 'Вы были успешно удалены из группы.', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Вы и так не в группе.', parse_mode='html')
        
        
@bot.message_handler(commands=['list_users'])
def list_users(message):
    log_message(message)
    if ignore_message_from_group(message):
        return
    global last_command
    last_command[message.chat.id] = 'list_users'
    if not user_in_group(message.chat.id):
        bot.send_message(message.chat.id, 'Вы должны создать, или вступить в какую-то группу, чтобы иметь возможность просмотаривать список ее участников.', parse_mode='html')
        last_command[message.chat.id] = 'text'
    else:
        num = 0
        group_name = get_group(message.chat.id).name
        reply = 'Список участников группы {}:\n'.format(group_name)
        users = get_group_users(group_name)
        for num, user in enumerate(users):
            reply += str(1 + num) + ') ' + user.name + '\n'
        bot.send_message(message.chat.id, reply, parse_mode='html')
        
        
@bot.message_handler(commands=['secret_list_all_users'])
def secret_list_list_users(message):
    log_message(message)
    if ignore_message_from_group(message):
        return
    global last_command
    last_command[message.chat.id] = 'secret_list_all_users'
    reply = ''
    for group in Group.select():
        group_name = group.name
        num = 0
        reply += 'Список участников группы {}:\n'.format(group_name)
        for num, user in enumerate(group.users):
            reply += str(1 + num) + ') ' + user.name + '\n'
    reply += 'Список участников, не входящих ни в одну группу:\n'
    for num, user in enumerate(User.select().where(User.group.is_null())):
        reply += str(1 + num) + ') ' + user.name + '\n'
    bot.send_message(message.chat.id, reply, parse_mode='html')
    
    
@bot.message_handler(commands=['generate'])
def generate(message):
    log_message(message)
    if ignore_message_from_group(message):
        return
    global last_command
    last_command[message.chat.id] = 'generate'
    if not user_in_group(message.chat.id):
        bot.send_message(message.chat.id, 'Вы должны создать, или вступить в какую-то группу, чтобы иметь возможность генерировать распределение ее участников.', parse_mode='html')
        last_command[message.chat.id] = 'text'
    else:
        bot.send_message(message.chat.id, 'Введите пароль:', parse_mode='html')
    
    
@bot.message_handler(commands=['leave_feedback'])
def leave_feedback(message):
    log_message(message)
    if ignore_message_from_group(message):
        return
    global last_command
    last_command[message.chat.id] = 'leave_feedback'
    bot.send_message(message.chat.id, 'Введите ваш вопрос/отзыв:', parse_mode='html')        

    
@bot.message_handler(commands=['write_to_santa'])
def write_to_santa(message):
    log_message(message)
    if ignore_message_from_group(message):
        return
    global last_command
    last_command[message.chat.id] = 'write_to_santa'
    user = User.get(User.chat_id == message.chat.id)
    if user.santa is not None:
        bot.send_message(message.chat.id, 'Напишите письмо своему тайному Санте:', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Для начала необходимо выполнить команду /generate.', parse_mode='html')
        last_command[message.chat.id] = 'text'
        
        
@bot.message_handler(commands=['write_to_donee'])
def write_to_donee(message):
    log_message(message)
    if ignore_message_from_group(message):
        return
    global last_command
    last_command[message.chat.id] = 'write_to_donee'
    targets = [target for target in User.get(User.chat_id == message.chat.id).targets]
    if len(targets) > 0:
        bot.send_message(message.chat.id, 'Напишите письмо своему дарополучателю:', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Для начала необходимо выполнить команду /generate.', parse_mode='html')
        last_command[message.chat.id] = 'text'
        
        
def bad_permutation(p):
    return len(p) > 1 and np.any(p == np.arange(len(p)))
    
    
def generate_pairs(group_name):
    users = get_group_users(group_name)
    p = np.random.permutation(len(users))
    while bad_permutation(p):
        p = np.random.permutation(len(users))
    for i in range(len(users)):
        target = p[i]
        users[target].santa = users[i]
        users[target].save()
        bot.send_message(users[i].chat_id, 'От вас ждет подарка ' + users[target].name + ' :)', parse_mode='html')
        bot.forward_message(users[i].chat_id, users[target].chat_id, users[target].message_id)
        
        
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
    is_personal_message = (last_command[message.chat.id] in ['create_group2', 'join_group1', 'write_to_santa', 'write_to_donee'])
    if is_personal_message and message.chat.id in personal_chats:
        my_chat_id = 273440998
        user = User.get(User.chat_id == message.chat.id)
        bot.send_message(my_chat_id, '{} leave personal message {}'.format(user.name, last_command[message.chat.id]), parse_mode='html')
    else:
        log_message(message)
    if ignore_message_from_group(message):
        return
    o_last_command = last_command[message.chat.id]
    last_command[message.chat.id] = 'text'
    if o_last_command == 'create_group':
        if has_group(message.text):
            bot.send_message(message.chat.id, 'Группа с таким названием уже существует.', parse_mode='html')
        elif not correct_name(message.text):
            bot.send_message(message.chat.id, 'Введете корректное название группы. Название может состоять только из англиских букв и цифр.', parse_mode='html')
        else:
            bot.send_message(message.chat.id, 'Придумайте секретный пароль, с помощью которого вы сможете сгенерировать распределение участников:', parse_mode='html')
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
        user = User.get(User.chat_id == message.chat.id)
        user.message_id = message.message_id
        if o_last_command == 'create_group2':
            Group.create(name=group_names[message.chat.id], password=passwords[message.chat.id])
        user.group = Group.get(Group.name == group_names[message.chat.id])
        user.save()
        if o_last_command == 'join_group1':
            bot.send_message(message.chat.id, 'Вы были успешно добавлены в группу!', parse_mode='html')
        else:
            bot.send_message(message.chat.id, 'Вы успешно создали группу! Зовите скорее своих друзей :)', parse_mode='html')
    elif o_last_command == 'generate':
        if message.text == get_group(message.chat.id).password:
            generate_pairs(get_group(message.chat.id).name)
        else:
            bot.send_message(message.chat.id, 'Неверный пароль. Если вы не знаете пароль, свяжитесь с создателем группы.', parse_mode='html')
    elif o_last_command == 'leave_feedback':
        pass
    elif o_last_command == 'write_to_santa':
        user = User.get(User.chat_id == message.chat.id)
        bot.send_message(user.santa.chat_id, 'Вам пришло письмо от вашего дарополучателя, скорее читайте его!', parse_mode='html')
        bot.forward_message(user.santa.chat_id, message.chat.id, message.message_id)
        bot.send_message(user.santa.chat_id, 'Если вы хотите ответить, используйте команду /write_to_donee.', parse_mode='html')
        bot.send_message(message.chat.id, 'Письмо успешно отправлено!', parse_mode='html')
    elif o_last_command == 'write_to_donee':
        targets = [target for target in User.get(User.chat_id == message.chat.id).targets]
        bot.send_message(targets[0].chat_id, 'Вам пришло письмо от персонального Тайного Санты, скорее читайте его!\n\n{}\n\nЕсли вы хотите ответить, используйте команду /write_to_santa.'.format(message.text), parse_mode='html')
        bot.send_message(message.chat.id, 'Письмо успешно отправлено!', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Неизвестная команда. Обратите внимание, что вводить команды нужно обязательно с символом "/". Для просмотра списка допустимых команд выполните /help.', parse_mode='html')
    
    
def forward_message_to_me(message):
    if is_first_message(message.chat.id):
        User.create(chat_id=message.chat.id, name=get_name(message.from_user))
    my_chat_id = 273440998
    bot.forward_message(my_chat_id, message.chat.id, message.message_id)


@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'video', 'document', 'location', 'contact', 'sticker'])
def reply_all_nontext_messages(message):
    global last_command
    o_last_command = last_command[message.chat.id]
    is_personal_message = (o_last_command in ['create_group2', 'join_group1', 'write_to_santa', 'write_to_donee'])
    if is_personal_message and message.chat.id in personal_chats:
        my_chat_id = 273440998
        user = User.get(User.chat_id == message.chat.id)
        bot.send_message(my_chat_id, '{} leave personal non-text message {}'.format(user.name, last_command[message.chat.id]), parse_mode='html')
    else:
        log_message(message)
    if ignore_message_from_group(message):
        return
    last_command[message.chat.id] = 'text'
    if o_last_command == 'write_to_santa':
        user = User.get(User.chat_id == message.chat.id)
        bot.send_message(user.santa.chat_id, 'Вам пришло письмо от вашего дарополучателя, скорее читайте его!', parse_mode='html')
        bot.forward_message(user.santa.chat_id, message.chat.id, message.message_id)
        bot.send_message(user.santa.chat_id, 'Если вы хотите ответить, используйте команду /write_to_donee.', parse_mode='html')
        bot.send_message(message.chat.id, 'Письмо успешно отправлено!', parse_mode='html')
    elif o_last_command == 'write_to_donee':
        bot.send_message(message.chat.id, 'На данный момент оленья почта Тайного Санты принимает только текстовые письма.', parse_mode='html')
    else:
        bot.reply_to(message, 'Если вы хотите отправить это сообщение персональному Тайному Санте, необходимо предварительно вызвать команду /write_to_santa. Обратите внимание, что в одном письме вы можете использовать максимум одну картинку.')

        
if __name__ == '__main__':
    while True:
        try:
            print('Start polling')
            bot.polling(none_stop=True)
        except Exception as E:
            print('Some exception while polling')
            print(E)
