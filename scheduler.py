import time
import process
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()

sched.add_job(process.run_process, 'cron',  hour='10', minute='30' , id="test_1")

sched.start()

while True:
    print("running-----")
    time.sleep(1)