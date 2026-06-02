"""Daily cron: collect HH vacancies for all active users and resumes."""
from app.collector import collect_all_sync

if __name__ == "__main__":
    results = collect_all_sync()
    for r in results:
        print(r)
