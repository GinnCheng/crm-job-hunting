import os
import subprocess

# 自动 migration
subprocess.run(["python", "manage.py", "makemigrations"])
subprocess.run(["python", "manage.py", "migrate"])

# 启动 server
subprocess.run(["python", "manage.py", "runserver"])