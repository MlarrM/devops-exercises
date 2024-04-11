from variables import path_to_json
import json

#prerequiesites: 
# - exported trello json which you can't import via official import-from-trello feature

json_file = path_to_json

with open(json_file) as json_data:
  data = json.load(json_data)

unfiltered_cards = data.get("cards")
unfiltered_labels = data.get("labels")
unfiltered_lists = data.get("lists")

filtered_cards = []
filtered_labels = []
filtered_lists = []

for list in unfiltered_lists:
  list_data = {
    'idTrello': list.get('id'),
    'nameTrello': list.get('name')
  }
  filtered_lists.append(list_data)

for label in unfiltered_labels:
  label_data = {
    'idTrello': label.get('id'),
    'name': label.get('name'),
    'color': label.get('color')
  }
  filtered_labels.append(label_data)

for card in unfiltered_cards:
  cards_data = {
    'idTrello': card.get('idList'),
    'name': card.get('name'),
    'desc': card.get('desc'),
    'url': []
    }
  if card.get('attachments'):
    for link in card.get('attachments'):
      cards_data['url'].append(link.get('url'))
  filtered_cards.append(cards_data)