from apscheduler.schedulers.blocking import BlockingScheduler

from cli.main import run


def start_scheduler():
    """
    Start scheduled scraping jobs.
    """
    scheduler = BlockingScheduler()

    # Run every hour
    scheduler.add_job(run, "interval", hours=1)

    print("Scheduler started. Running every hour...")

    scheduler.start()