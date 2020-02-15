from web import start_server
from polls import *

schedule_poll(seconds=300)

start_server()
