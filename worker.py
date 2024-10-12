# worker.py
import os
import sys
from redis import Redis
from rq import Worker, Queue, Connection

def main():
    redis_url = os.environ.get('REDIS_URL')
    if not redis_url:
        print("REDIS_URL is not set. Please check your environment variables.")
        sys.exit(1)

    try:
        conn = Redis.from_url(redis_url)
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        sys.exit(1)

    with Connection(conn):
        worker = Worker(['default'])
        worker.work()

if __name__ == '__main__':
    main()
