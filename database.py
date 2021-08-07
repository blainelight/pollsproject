import os
import psycopg2
import datetime
from psycopg2.extras import execute_values

from dotenv import load_dotenv
load_dotenv()

CREATE_USERS = """ CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY, name TEXT);"""
CREATE_POLLS = """ CREATE TABLE IF NOT EXISTS polls (
    id SERIAL PRIMARY KEY, name TEXT, created_by TEXT);"""
CREATE_POLL_OPTIONS = """ CREATE TABLE IF NOT EXISTS poll_options (
    id SERIAL PRIMARY KEY, poll_id INTEGER, option TEXT, FOREIGN KEY(poll_id) REFERENCES polls (id));""" #I Forgot Syntax for Foriegn Key
CREATE_POLL_VOTES = """ CREATE TABLE IF NOT EXISTS poll_votes (
    id SERIAL PRIMARY KEY, poll_options_id INTEGER, voter_username TEXT, FOREIGN KEY(poll_options_id) REFERENCES poll_options (id));"""

SELECT_ALL_POLLS = "SELECT * FROM polls;"
SELECT_POLL_ID = "SELECT id FROM polls WHERE name = %s AND created_by = %s;" #not sure if I can do 2 variables as %s, but let's try
SELECT_LATEST_POLL_ID = """select * from polls p 
join poll_options o on p.id = o.poll_id
WHERE p.id = (select id from polls p ORDER BY id DESC limit 1)
;"""
SELECT_POLL_OPTIONS = "SELECT * FROM poll_options WHERE poll_id = %s;"
SELECT_POLL_OPTIONS_IDS = "SELECT id FROM poll_options WHERE poll_id = %s;"
SELECT_POLL_VOTES = """SELECT poll_id, option, count(*)
FROM poll_options po JOIN poll_votes pv on po.id = pv.poll_options_id
WHERE poll_id = %s
GROUP BY 1,2;""" #need to add 3 here when adding in window fxn
SELECT_RANDOM_WINNER = """ SELECT voter_username
FROM poll_options po JOIN poll_votes pv on po.id = pv.poll_options_id
WHERE poll_options_id = %s
ORDER BY random()
LIMIT 1"""


INSERT_POLL = "INSERT INTO polls (name, created_by) VALUES (%s,%s) RETURNING id;"
INSERT_POLL_OPTIONS = "INSERT INTO poll_options (poll_id, option) VALUES %s;"
INSERT_VOTES = "INSERT INTO poll_votes (poll_options_id,voter_username) VALUES (%s, %s);"


connection = psycopg2.connect(os.environ["DATABASE_URL"])


def create_tables(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USERS)
            cursor.execute(CREATE_POLLS)
            cursor.execute(CREATE_POLL_OPTIONS)
            cursor.execute(CREATE_POLL_VOTES)


def get_all_polls(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_POLLS)
            return cursor.fetchall()


def add_poll(connection, title, owner, options):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_POLL, (title, owner))
            #cursor.execute(SELECT_POLL_ID, (title, owner)) #No longer need this because the query above is returning hte poll_id, which gets pulled below.

            poll_id = cursor.fetchone()[0] #accessing column 0, which is really the only column returned. But this is interesting.
            option_values = [(poll_id,option) for option in options]

            execute_values(cursor, INSERT_POLL_OPTIONS, option_values) #this is the same as below:
            #for option_value in option_values:
            #    cursor.execute(INSERT_POLL_OPTIONS, option_value)


def get_latest_poll(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_LATEST_POLL_ID)
            return cursor.fetchall()

def select_poll_options(connection, poll_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_OPTIONS, (poll_id,))
            return cursor.fetchall()


def select_poll_options_ids(connection, poll_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_OPTIONS_IDS, (poll_id,))
            return cursor.fetchall()


def insert_votes(connection, poll_option_id, voter_username):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_VOTES, (poll_option_id, voter_username))


def get_poll_votes(connection, poll_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_VOTES, (poll_id,))
            return cursor.fetchall()

def select_random_poll_vote(connection, option_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_RANDOM_WINNER, (option_id,))
            return cursor.fetchall()

def connection_close(connection):
    connection.close()