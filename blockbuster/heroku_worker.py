import redis
from rq import Worker, Queue, Connection
import os

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:32769/1')
print(REDIS_URL)

listen = ['default']

conn = redis.from_url(REDIS_URL)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
