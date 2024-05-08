import sqlite3
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton         #импорт библиотек

bot  = telebot.TeleBot('TOKEN')        #Свой токен

con = sqlite3.connect('Database.db', check_same_thread=False)           #Подключение к БД
cursor = con.cursor()
                                        
cursor.execute('''                                                     
CREATE TABLE IF NOT EXISTS Students (
id INTEGER PRIMARY KEY,
Name TEXT NOT NULL,
Surname TEXT NOT NULL,
Age INTEGER NOT NULL
)
''')                                                                       #Создание БД
keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)          #Основная клавиатура
button_save = telebot.types.KeyboardButton(text="Добавить")
button_see = telebot.types.KeyboardButton(text='Просмотр')
button_delete = telebot.types.KeyboardButton(text='Удалить')
button_sort = telebot.types.KeyboardButton(text='Сортировка')
button_change = telebot.types.KeyboardButton(text='Изменение')
keyboard.add(button_save, button_see, button_delete, button_sort, button_change)


@bot.message_handler(commands=['start'])                                #Ответ на начальную команду
def welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     'Добро пожаловать',
                     reply_markup=keyboard)
    

@bot.message_handler(func = lambda s: 'Добавить' in s.text)             # Кнопка Добавить
def insert(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     'Введите имя, фамилию, возраст учащегося через пробел')
    bot.register_next_step_handler(message, Insert2)

def Insert2(message):
    try:
        args = str(message.text)
        args = args.split(' ')
        if args[0].isalpha() and args[1].isalpha() and args[2].isdigit():
            cursor.execute(f'INSERT INTO Students(Name, Surname, Age) VALUES(?,?,?)', (args[0], args[1], args[2])) 
            con.commit()
            bot.send_message(message.chat.id, 'Успешно')
        else:
            raise Exception
    except Exception:
        bot.send_message(message.chat.id, 'Произошла ошибка при вводе, попробуйте еще раз')


@bot.message_handler(func = lambda s: 'Просмотр' in s.text)                 #Кнопка просмотр
def see(message):
    chat_id = message.chat.id
    students = cursor.execute('SELECT * FROM Students').fetchall()
    for a in students:
        bot.send_message(chat_id,f' {a[0]}, {a[1]}, {a[2]}, {a[3]}')

@bot.message_handler(func = lambda s: 'Удалить' in s.text)                  #Кнопка удалить
def delete(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     'Введите Id учащегося, которого хотели бы удалить')
    bot.register_next_step_handler(message, AskingId)

def AskingId(message):
    try:
        id = message.text
        mx = cursor.execute('SELECT MAX(id) FROM Students').fetchall()
        cursor.execute('DELETE FROM Students WHERE id = ?',(id,))
        con.commit()
        students = cursor.execute('SELECT id FROM Students WHERE id > ?', (id,)).fetchall()
        for a in students:
            cursor.execute('UPDATE Students SET id = ? WHERE id = ?', (a[0]-1, a[0]))
            con.commit()
        cursor.execute('DELETE FROM Students WHERE id = ?', (mx[0]))
        bot.send_message(message.chat.id,'Успешно удалено')
    except Exception:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте еще раз')

@bot.message_handler(func = lambda s: 'Изменение' in s.text)                #Кнопка Изменение
def Change(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton(text="Имя")
    btn2 = telebot.types.KeyboardButton(text="Фамилия")
    btn3 = telebot.types.KeyboardButton(text='Возраст')
    btn4 = telebot.types.KeyboardButton(text='На главную')
    keyboard.add(btn1, btn2, btn3, btn4)
    bot.send_message(chat_id, 
                     'Что нужно изменить?', reply_markup=keyboard)

@bot.message_handler(func = lambda s: 'Имя' in s.text)                  #Изменение имени
def Changename(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Введите ID учащегося и измененное имя через пробел')
    bot.register_next_step_handler(message, Changename1)

def Changename1(message):
    try:
        chat_id = message.chat.id
        args = str(message.text)
        args = args.split(' ')
        mx = cursor.execute('SELECT MAX(id) FROM Students').fetchall()
        if mx[0][0] >= int(args[0]):
            cursor.execute('UPDATE Students SET Name = ? WHERE id = ?', (args[1], args[0]))
            bot.send_message(chat_id, 'Успешно')
        else:
            raise Exception
    except Exception:
        bot.send_message(chat_id, 'Операция не выполнена, попробуйте еще раз')


@bot.message_handler(func = lambda s: 'Фамилия' in s.text)                  #Изменение фамилии
def ChangeSurname(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Введите ID учащегося и измененную фамилию через пробел')
    bot.register_next_step_handler(message, ChangeSurname1)

def ChangeSurname1(message):
    try:
        chat_id = message.chat.id
        args = str(message.text)
        args = args.split(' ')
        mx = cursor.execute('SELECT MAX(id) FROM Students').fetchall()
        if mx[0][0] >= int(args[0]):
            cursor.execute('UPDATE Students SET Surname = ? WHERE id = ?', (args[1], args[0]))
            bot.send_message(chat_id, 'Успешно')
        else:
            raise Exception
    except Exception:
        bot.send_message(chat_id, 'Операция не выполнена, попробуйте еще раз')

@bot.message_handler(func = lambda s: 'Возраст' in s.text)                      #Изменение возраста
def ChangeAge(message):
    if message.text == 'Возраст':
        chat_id = message.chat.id
        bot.send_message(chat_id, 'Введите ID учащегося и измененный возраст через пробел')
        bot.register_next_step_handler(message, ChangeAge1)

def ChangeAge1(message):
    try:
        chat_id = message.chat.id
        args = str(message.text)
        args = args.split(' ')
        mx = cursor.execute('SELECT MAX(id) FROM Students').fetchall()
        if mx[0][0] >= int(args[0]):
            cursor.execute('UPDATE Students SET Age = ? WHERE id = ?', (args[1], args[0]))
            bot.send_message(chat_id, 'Успешно')
        else:
            raise Exception
    except Exception:
        bot.send_message(chat_id, 'Операция не выполнена, попробуйте еще раз')


@bot.message_handler(func = lambda s: 'Сортировка' in s.text)               #Кнопка сортировка
def Filter(message):
    chat_id = message.chat.id
    keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton(text="По возрастанию")
    btn2 = telebot.types.KeyboardButton(text="По убыванию")
    btn3 = telebot.types.KeyboardButton(text='На главную')
    keyboard2.add(btn1, btn2, btn3)
    bot.send_message(chat_id, 
                     'Какая сортировка Вас интересует?', reply_markup=keyboard2)
    
@bot.message_handler(func = lambda s: 'По возрастанию' in s.text)               #Сортировка по возрастанию
def Filter2_1(message):
    global Fltr 
    Fltr = 'ASC'
    chat_id = message.chat.id
    keyboard3 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton(text="По имени")
    btn2 = telebot.types.KeyboardButton(text="По фамилии")
    btn3 = telebot.types.KeyboardButton(text="По возрасту")
    btn4 = telebot.types.KeyboardButton(text='На главную')
    keyboard3.add(btn1, btn2, btn3, btn4)
    bot.send_message(chat_id, 'По какому признаку нужна сортировка?', reply_markup=keyboard3)

@bot.message_handler(func = lambda s: 'По убыванию' in s.text)                   #Сортировка по убыванию
def Filter2_2(message):
    global Fltr
    Fltr = 'DESC'
    chat_id = message.chat.id
    keyboard3 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton(text="По имени")
    btn2 = telebot.types.KeyboardButton(text="По фамилии")
    btn3 = telebot.types.KeyboardButton(text="По возрасту")
    btn4 = telebot.types.KeyboardButton(text='На главную')
    keyboard3.add(btn1, btn2, btn3, btn4)
    bot.send_message(chat_id, 'По какому признаку нужна сортировка?', reply_markup=keyboard3)

@bot.message_handler(func = lambda s: 'На главную' in s.text)                   #Кнопка "на главную"
def Back(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_save = telebot.types.KeyboardButton(text="Добавить")
    button_see = telebot.types.KeyboardButton(text='Просмотр')
    button_delete = telebot.types.KeyboardButton(text='Удалить')
    button_sort = telebot.types.KeyboardButton(text='Сортировка')
    button_change = telebot.types.KeyboardButton(text='Изменение')
    keyboard.add(button_save, button_see, button_delete, button_sort, button_change)
    bot.send_message(chat_id, 'Возвращение на главную', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])                #Сортировка
def Filter3(message):
    chat_id = message.chat.id
    if message.text == 'По имени':
        students =  cursor.execute(f'SELECT * From Students ORDER BY Name {Fltr}').fetchall()
        for a in students:
            bot.send_message(chat_id,f' {a[0]}, {a[1]}, {a[2]}, {a[3]}')
    elif message.text == 'По фамилии':
        students = cursor.execute(f'SELECT * From Students ORDER BY Surname {Fltr}').fetchall()
        for a in students:
            bot.send_message(chat_id,f' {a[0]}, {a[1]}, {a[2]}, {a[3]}')
    elif message.text == 'По возрасту':
        students = cursor.execute(f'SELECT * From Students ORDER BY Age {Fltr}').fetchall()
        for a in students:
            bot.send_message(chat_id,f' {a[0]}, {a[1]}, {a[2]}, {a[3]}')

if __name__ == '__main__':                                                      #Бесконечная работа бота
    print('Бот работает')
    bot.infinity_polling()

con.commit()                                                                      #Коммит и закрытие БД
con.close()
