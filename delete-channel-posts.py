#!/usr/bin/python3

import argparse
import requests
import asyncio
import json
import pymysql.cursors
from typing import NamedTuple
from concurrent.futures import ThreadPoolExecutor

class DBConn(NamedTuple):
    host: str
    user: str
    password: str
    db: str

class PostDel(NamedTuple):
    dbconn: DBConn
    channel_id: str
    n: int

def query_db(query, postdel):
    connection = pymysql.connect(host=postdel.dbconn.host,
                                 user=postdel.dbconn.user,
                                 password=postdel.dbconn.password,
                                 db=postdel.dbconn.db,
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        connection.close()

def fetch_token(siteurl, user_email, user_password):
    payload = {'login_id':f'{user_email}','password':f'{user_password}'}
    r = requests.post(f'{siteurl}/api/v4/users/login', data = json.dumps(payload))
    return r.headers['Token']

def send_request(session, siteurl, token, post_id):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{siteurl}/api/v4/posts/{post_id}"
    with session.delete(url, headers=headers) as request:
        print(f"DELETE {url} - status_code: {request.status_code}")

async def async_request(workers, siteurl, token, post_ids):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    send_request,
                    *(session, siteurl, token, post_id['Id'])
                )
                for post_id in post_ids
            ]
            for response in await asyncio.gather(*tasks):
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Delete n-posts from channel.")
    parser.add_argument("-n", "--n-posts", help="Number of oldest posts to delete", required=True, type=int)
    parser.add_argument("-s", "--siteurl", help="Mattermost siteurl (e.g. http://localhost:8065)", required=True)
    parser.add_argument("-c", "--channel-id", help="Id of channel", required=True)
    parser.add_argument("-w", "--worker", help="Number of workers used for calling API", required=True, type=int)
    parser.add_argument("-u", "--db-user", help="Username for database", required=True)
    parser.add_argument("-p", "--db-password", help="Password for database", required=True)
    parser.add_argument("-D", "--database", help="Database name", required=True)
    parser.add_argument("-H", "--host", help="Database host (e.g. localhost, 127.0.0.1)", required=True)
    parser.add_argument("--api-user", help="Username for authenticating against API", required=True)
    parser.add_argument("--api-password", help="Password for API user", required=True)
    args = parser.parse_args()

    dbconn = DBConn(args.host, args.db_user, args.db_password, args.database)
    postdel = PostDel(dbconn, args.channel_id, args.n_posts)

    query = f"select Id from Posts where ChannelId = '{postdel.channel_id}' and DeleteAt = '0' order by CreateAt asc limit {postdel.n};"
    post_ids = query_db(query, postdel)
    token = fetch_token(args.siteurl, args.api_user, args.api_password)
    future = asyncio.ensure_future(async_request(args.worker, args.siteurl, token, post_ids))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
