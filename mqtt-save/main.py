#!venv/bin/python
import sqlite3
import paho.mqtt.client as mqtt
import sys
import traceback

db_createtable = "CREATE TABLE IF NOT EXISTS message (id INTEGER UNIQUE PRIMARY KEY, topic BLOB, message BLOB, timestamp DEFAULT CURRENT_TIMESTAMP);"
db_insertmessage = "INSERT INTO message (topic, message) VALUES (?, ?);"

i=0

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe("#")

def on_message(client, userdata, msg):
	global i
	sys.stdout.write('.')
	try:
		db_cur.execute(db_insertmessage, (msg.topic, msg.payload))
	except UnicodeDecodeError:
		sys.stdout.write("i")
	except Exception:
		raise
	if i % 1024 == 0:
		db_conn.commit()
		sys.stdout.write("c")
		sys.stdout.flush()
	i += 1

client = mqtt.Client()

db_conn = sqlite3.connect("mqtt.sqlite3")
db_cur = db_conn.cursor()
db_cur.execute(db_createtable)

client.on_connect = on_connect
client.on_message = on_message

client.connect("iot.eclipse.org", 1883, 60)

try:
	client.loop_forever()
except Exception as e:
	print(e)
	traceback.print_exc()
	db_cur.close()
	db_conn.close()
