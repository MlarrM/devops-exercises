from variables import username, password, wekan_url, token, board_name
from parsing_script import filtered_cards, filtered_labels, filtered_lists
import requests

#prerequiesites: 
# - exported trello json which you can't import via official import-from-trello feature
# - if the board_name board and/or lists in it were created in advance, their names must be the same as the old ones (in trello)

#script imports in wekan:
# - board + all its lists as they were
# - labels (names, colors) - DOESN'T WORK BEACUSE OF SOME API PROBLEMS
# - cards (titles, descriptions, attached urls as comments)

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

def get_board_lables(board_id):
    """Get all labels from the board."""
    board_url = wekan_url + api_boards + str(board_id)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
    body = requests.get(board_url, headers=headers)
    board = body.json()
    return board.get('labels')

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

if (board_name in pluck(existing_boards, 'title')) or not existing_boards:
    board_info = [board for board in existing_boards if board.get('title') == board_name]
    new_board_id = board_info[0].get('_id')
    new_board_lists_ids = get_all_lists(new_board_id)
    new_board_swimlane_id = get_swimlane(new_board_id)
else:
    request_url = wekan_url + api_boards
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
    post_data = {
        'title': '{}'.format(board_name),
        'owner': '{}'.format(user_id),
        'color': '{}'.format("moderndark")
        }
    body = requests.post(request_url, data=post_data, headers=headers)
    created_board = body.json()
    
    new_board_id = created_board.get('_id')
    new_board_swimlane_id = created_board.get('defaultSwimlaneId')
    new_board_lists_ids = []

## MATCH WEKAN LABELS (NEW) AND TRELLO LABELS (OLD); CREATE IF NOT FOUND
#doesn't work; 200 Ok Response but no label on client;
#possible reason - PUT method, not POST.

#labels_info = get_board_lables(new_board_id)

#for trello_label in filtered_labels:
#    if labels_info:
#        if trello_label.get('name') not in pluck(labels_info, 'name'):
#            request_url = wekan_url + api_boards + str(new_board_id) + s + 'labels'
#            headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
#            label_data = {
#                'label': {
#                    'color': '{}'.format(trello_label.get('color')),
#                    'name': '{}'.format(trello_label.get('name'))
#                    }
#                }
#            body = requests.put(request_url, data=label_data, headers=headers)
#            #print(body.json())

for trello_board_list in filtered_lists:
    if trello_board_list.get('nameTrello') in pluck(new_board_lists_ids, 'title'):
        for wekan_board_list in new_board_lists_ids:
            if wekan_board_list.get('title') == trello_board_list.get('nameTrello'):
                wekan_board_list['idTrello'] = trello_board_list.get('idTrello')
    else:
        request_url = wekan_url + api_boards + str(new_board_id) + s + l
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
        post_data = {
            'title': trello_board_list.get('nameTrello')
        }
        body = requests.post(request_url, data=post_data, headers=headers)
        
        last_added_list = body.json()
        new_list = {
            '_id': last_added_list.get('_id'),
            'title': trello_board_list.get('nameTrello'),
            'idTrello': trello_board_list.get('idTrello')
        }
        new_board_lists_ids.append(new_list)

list_for_card = {}

for card in filtered_cards:
    for list in new_board_lists_ids:
        if list.get("idTrello") == card.get("idTrello"):
            list_id = list.get("_id")
    card_title = card.get("name")
    card_description = card.get("desc")
    card_to_list = wekan_url + api_boards + str(new_board_id) + s + l + s + list_id + s + cs

    headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
    post_data = {
        'authorId': '{}'.format(user_id), 
        'title': '{}'.format(card_title), 
        'description': '{}'.format(card_description), 
        'swimlaneId': '{}'.format(new_board_swimlane_id)
        }
    body = requests.post(card_to_list, data=post_data, headers=headers)
    last_added_card = body.json()
    
    # if there were URLs attached to the created card, add them as comments
    if card["url"]:
        for link in card.get("url"):
            comment_to_card = wekan_url + api_boards + str(new_board_id) + s + cs + s + last_added_card.get("_id") + s + 'comments'
            headers = {'Accept': 'application/json', 'Authorization': 'Bearer {}'.format(api_key)}
            post_data = {
                'authorId': '{}'.format(user_id),
                'comment': '{}'.format(link)
            }
            body = requests.post(comment_to_card, data=post_data, headers=headers)