from web import start_server
from polls import *

schedule_poll(seconds=120)

start_server()
