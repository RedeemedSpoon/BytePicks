import multiprocessing

bind = "127.0.0.1:8000"

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

user = "root"
group = "www-data"

timeout = 30
max_requests = 1000
max_requests_jitter = 50
proc_name = "bytepicks"
