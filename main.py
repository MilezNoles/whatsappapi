import requests
import sqlite3

db = sqlite3.connect("database.sqlite3")
cursor = db.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS
chatrecord(id INTEGER PRIMARY KEY, token TEXT, instanceId TEXT)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS
users(id INTEGER PRIMARY KEY, status TEXT, name TEXT, phone INTEGER)
''')

headers = {"X-Whatsapp-Token": "5d8af8faaeb61680883a850be0c577e3"}

# получение свободного инстанса чата->{'id': 26, 'token': 'PENGKShj3LbJP8xD', 'instanceId': '2a01:4f9:c011:4f7c:3::27'}
url = "https://dev.whatsapp.sipteco.ru/v3/chat/spare?crm=PIPEDRIVE"
data = requests.get(url,headers=headers)
chat_inf = data.json()
print(data.json())

try:
    cursor.execute('INSERT INTO chatrecord(id, token, instanceId) VALUES(?,?,?)',
                   (chat_inf['id'], chat_inf['token'], chat_inf['instanceId']))
    db.commit()
except sqlite3.IntegrityError as e:
    cursor.execute("""
            select id, token, instanceId
            from chatrecord
            where id=(SELECT max(id) FROM chatrecord);     
            """)
    print(list(*cursor))

# получение данных о статусе подключения(тут же должен получаться qr но его base64 в ответе нет)
method = "status"
url = f"https://dev.whatsapp.sipteco.ru/v3/instance26/{method}?token=PENGKShj3LbJP8xD"
data = requests.get(url, headers=headers)
user_inf = data.json()

# получение данных о подключенном юзере
method = "me"
url = f"https://dev.whatsapp.sipteco.ru/v3/instance26/{method}?token=PENGKShj3LbJP8xD"
data = requests.get(url, headers=headers)
user_inf.update(data.json())
cursor.execute('INSERT INTO users(status, name, phone) VALUES(?,?,?)',
               (user_inf['state'], user_inf['name'], user_inf['number']))
db.commit()
print(user_inf)

# отправка тестового сообщения
method = "sendMessage"
message = """{
  "body": "test",
  "phone": "79112112682"
}"""
url = f"https://dev.whatsapp.sipteco.ru/v3/instance26/{method}?token=PENGKShj3LbJP8xD"
data = requests.post(url, headers=headers, data=message)
print(data.json())

cursor.execute("""
        select status, name, phone
        from users;
        """)

for i in cursor:
    temp = list(i)
    print(temp)
