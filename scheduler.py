from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import subprocess
import sys

scheduler=BlockingScheduler()

def run_briefcase():
    print(f"\n BriefCase scheduler triggered at {datetime.now().strftime('%I:%M %p')}")
    print("Running morning briefings...\n")
    subprocess.run([sys.executable, "Briefcase.py"])
    print("\n All briefings sent successfully")

#Schedule to run every day at 6:00 am
scheduler.add_job(
    run_briefcase,
    trigger="cron",
    hour=10,
    minute=0,
    day_of_week="mon-fri",
    id="morning_briefing"
)

print("="*50)
print("BriefCase Scheduler is running")
print("Briefings scheduled for 6:00 AM daily")
print("Waiting for next scheduled run...")
print("="*50)
print("\nPress Ctrl+C to stop the scheduler\n")

#Test it immediately so you can see it working right now
print("Running a test briefing right now so you can see it work...")
run_briefcase()

scheduler.start()