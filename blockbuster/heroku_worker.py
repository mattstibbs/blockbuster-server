import os
from redis import Redis
from rq import Queue, Connection
from rq.worker import HerokuWorker as Worker


listen = ['high', 'default', 'low']

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:32769/1')

if not REDIS_URL:
    raise RuntimeError('Set up Redis first.')

conn = Redis.from_url(REDIS_URL)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()

