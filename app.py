import os
import psycopg2
from psycopg2.errors import DivisionByZero
from dotenv import load_dotenv
import database

WELCOME = 'Welcome to the Poll App!'

DATABASE_PROMPT = "Enter the DATABASE_URL value or leave empty to load from .env file: "
MENU_PROMPT = """ -- Menu --
1) Create new polls
2) List all polls
3) Vote on polls
4) Show poll results
5) Select a random winner from a poll
6) Exit

Enter your choice: """

NEW_OPTION_PROMPT = 'Enter new option text (or leave empty to stop adding options): '

def prompt_poll(connection):
    title = input('Enter poll title: ')
    owner = input('Enter poll owner: ')
    options = []
    while new_poll_option := input(NEW_OPTION_PROMPT): #don't do this: while new_poll_option != '':
        options.append(new_poll_option)
    database.add_poll(connection, title, owner, options)


def print_polls(connection):
    polls = database.get_all_polls(connection)
    for _id, name, created_by in polls:
        print(f"{_id}: {name} (created by {created_by})")
    print('\n')

def _print_poll_options(options):
    increment = 1
    for _id, _poll_id, option in options:
        print(f'{increment}: {option}')
        increment += 1


def prompt_poll_vote(connection):
    poll_id = int(input('Enter the poll_id of the poll you would like to vote for: '))
    options = database.select_poll_options(connection, poll_id)
    _print_poll_options(options)
    option_choice = int(input("Enter option you'd like to vote for: "))-1
    poll_options_ids = database.select_poll_options_ids(connection, poll_id) #I know this isn't the best way.. IDK how to keep it in 1 call and use the first column intead of the second, but maybe he will teach this or do it differnetly
    poll_option_id = poll_options_ids[option_choice]
    #print(f'poll_options_ids: {poll_options_ids}') #[(4,), (5,), (6,)]
    #print(f'poll_option_id: {poll_option_id}') #(5,)
    voter_username = input("Enter the username you'd like to vote as (case-sensitive): ")
    database.insert_votes(connection, poll_option_id, voter_username)
    print(f"{voter_username}'s vote was added to the database! \n")


def show_poll_votes(connection):
    poll_choice = input('Enter poll id you would like to see votes for: ')
    try:
        votes = database.get_poll_votes(connection, poll_choice)
    except DivisionByZero:
        print('No votes cast yet for this poll.')
    for _id, option, count in votes: #need window fxns to get percentage in sql -- add percentage as var
        print(f'{option} got {count} votes.') #add this to the end ({percentage:.%})


def pick_random_winner(connection):
    poll_id = int(input('Enter the poll_id of the poll you would like to pick random winners for: '))
    options = database.select_poll_options(connection, poll_id)
    _print_poll_options(options)
    option_choice = int(input("Enter the option number for the winning option, and we'll randomly pick a winner from voters: "))-1
    poll_options_ids = database.select_poll_options_ids(connection, poll_id) #I know this isn't the best way.. IDK how to keep it in 1 call and use the first column intead of the second, but maybe he will teach this or do it differnetly
    poll_option_id = poll_options_ids[option_choice]
    winner = database.select_random_poll_vote(connection, poll_option_id)
    print(f'The winner is: {winner}!') #The winner is: [('Blaine',)]!


MENU_OPTIONS = {
    '1': prompt_poll,
    '2': print_polls,
    '3': prompt_poll_vote,
    '4': show_poll_votes,
    '5': pick_random_winner
}


def menu():
    database_url = input(DATABASE_PROMPT)
    if not database_url:
        load_dotenv()
        database_url = os.environ["DATABASE_URL"]
    connection = psycopg2.connect(database_url)
    database.create_tables(connection)
    print(WELCOME)
    while(selection := input(MENU_PROMPT)) != '6':
        try:
            MENU_OPTIONS[selection](connection)
        except KeyError:
            print('Not a valid selection. Please pick 1-5: ')

menu()

connection_close()
