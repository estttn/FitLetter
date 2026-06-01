import sqlite3

c = sqlite3.connect("/opt/hh-job-scout/data/hhscout.db")
applied = c.execute("select count(*) from vacancies where applied=1").fetchone()[0]
bad = c.execute(
    "select count(*) from vacancies where cover_letter like '%По описанию вижу пересечение%'"
).fetchone()[0]
rule = c.execute(
    "select count(*) from vacancies where cover_letter like '%discovery, бэклог%'"
).fetchone()[0]
print("applied", applied)
print("fallback_bad", bad)
print("rule_old", rule)
print("total", c.execute("select count(*) from vacancies").fetchone()[0])
