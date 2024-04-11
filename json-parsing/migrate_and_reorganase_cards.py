from variables import username, password, wekan_url, token, trello_lists_ids, new_boards, nesessary_lists
from parsing_script import filtered_cards
import requests

#prerequiesites: 
# - exported trello json which you can't import via official import-from-trello feature

#script creates wekan boards and lists in them according to new_boards list, 
#as well as imports cards using information from trello json

login_url = 'users/login'
wekan_login_url = wekan_url + login_url
api_boards = 'api/boards/'
api_users = 'api/users' 
s = '/'
l = 'lists'
sws = 'swimlanes'
cs = 'cards'
bs = 'boards'
users = wekan_url + api_users

board_theme = "pomegranate" #moderndark 

def get_all_boards(user_id):
    """Get list of all boards."""
    request_url = users + s + str(user_id) + s + bs
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
    body = requests.get(request_url, headers=headers)
    return body.json()

def get_all_lists(board_id):
    """Get all lists from the board."""
    request_url = wekan_url + api_boards + str(board_id) + s + l
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
    body = requests.get(request_url, headers=headers)
    return body.json()

def get_swimlane(board_id):
    """Get swimlane from the board. Return default swimlane ID."""
    swimlanes_url = wekan_url + api_boards + str(board_id) + s + sws
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
    body = requests.get(swimlanes_url, headers=headers)
    swimlane_info = body.json()
    return swimlane_info[0].get('_id')

def add_list(board_id, list_title):
    """Create a list with the specified name on the board."""
    request_url = wekan_url + api_boards + str(board_id) + s + l
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
    post_data = {
        'title': '{}'.format(list_title)
    }
    body = requests.post(request_url, data=post_data, headers=headers)
    return body.json()

def get_added_list_info(list_name, last_added_list):
    """Get the list name, ID and Trello ID and return as dictionary."""
    trello_list_info = [trello_list for trello_list in trello_lists_ids if trello_list.get('name') == list_name]
    new_list = {
        '_id': last_added_list.get('_id'),
        'title': list_name,
        'id_trello': trello_list_info[0].get('id_trello')
    }
    return new_list

def add_cards(board_lists_ids, filtered_cards, user_id):
    """Create cards in lists."""
    for list in board_lists_ids:    
        for card in filtered_cards:
            if card.get('idTrello') == list.get('id_trello'):
                request_url = wekan_url + api_boards + str(board_id) + s + l + s + list.get('_id') + s + cs
                card_title = card.get("name")
                card_description = card.get("desc")

                headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
                post_data = {
                    'authorId': '{}'.format(user_id), 
                    'title': '{}'.format(card_title), 
                    'description': '{}'.format(card_description), 
                    'swimlaneId': '{}'.format(board_swimlane_id)
                    }
                body = requests.post(request_url, data=post_data, headers=headers)
                last_added_card = body.json()

                # if there were URLs attached to the created card, add them as comments
                if card["url"]:
                    for link in card.get("url"):
                        request_url = wekan_url + api_boards + str(board_id) + s + cs + s + last_added_card.get("_id") + s + 'comments'
                        headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
                        post_data = {
                            'authorId': '{}'.format(user_id),
                            'comment': '{}'.format(link)
                        }
                        body = requests.post(request_url, data=post_data, headers=headers)

def pluck(lst, key):
    """Converte a list of dictionaries into a list of values corresponding to the specified key."""
    return [x.get(key) for x in lst]



data = {"username": username, "password": password}
body = requests.post(wekan_login_url, json=data)
d = body.json()
# if you already ussied a token and want to reuse it
#d = token

api_key = d.get('token')
user_id = d.get('id')

existing_boards = get_all_boards(user_id)

for board in new_boards:
    if (board.get('board_name') not in pluck(existing_boards, 'title')) or not existing_boards:
        request_url = wekan_url + api_boards
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
        post_data = {
            'title': '{}'.format(board.get('board_name')),
            'owner': '{}'.format(user_id),
            'color': '{}'.format(board_theme)
            }
        body = requests.post(request_url, data=post_data, headers=headers)
        created_board = body.json()
        board_id = created_board.get('_id')
        board_swimlane_id = created_board.get('defaultSwimlaneId')
        board_lists_ids = []
        
        for list_name in board.get('list_names'):
            last_added_list = add_list(board_id, list_name)
            board_lists_ids.append(get_added_list_info(list_name, last_added_list))
        
        add_cards(board_lists_ids, filtered_cards, user_id)
        
        for list_name in nesessary_lists:
            if list_name not in board.get('list_names'):
                last_added_list = add_list(board_id, list_name)
                board_lists_ids.append(get_added_list_info(list_name, last_added_list))
    else:
        board_info = [bi for bi in existing_boards if board.get('board_name') == bi.get('title')]
        board_id = board_info[0].get('_id')
        board_lists_ids = get_all_lists(board_id)
        board_swimlane_id = get_swimlane(board_id)
        created_lists = []
        
        for list_name in board.get('list_names'):
            if (list_name not in pluck(board_lists_ids, 'title')) or (not board_lists_ids):
                last_added_list = add_list(board_id, list_name)
                created_lists.append(get_added_list_info(list_name, last_added_list))
        
        if created_lists:        
            add_cards(created_lists, filtered_cards, user_id)    
        
        for list_name in nesessary_lists:
            if (list_name not in board.get('list_names')) and (list_name not in pluck(board_lists_ids, 'title')):
                last_added_list = add_list(board_id, list_name)
                created_lists.append(get_added_list_info(list_name, last_added_list))