import pandas as pd
import json

cidar = 'instructions/cidar.json'
chat = 'instructions/chat.json'
alpagasus = 'instructions/alpagasus.json'

with open(cidar, mode='r', encoding='utf-8') as file:
    cidar_data = json.load(file)
    cidar_df = pd.DataFrame(cidar_data)

with open(chat, mode='r', encoding='utf-8') as file:
    chat_data = json.load(file)
    chat_df = pd.DataFrame(chat_data)

with open(alpagasus, mode='r', encoding='utf-8') as file:
    alpagasus_data = json.load(file)
    alpagasus_df = pd.DataFrame(alpagasus_data)

alpagasus_df = alpagasus_df[['Sentence', 'Response']].rename(columns={'Sentence': 'instruction', 'Response': 'alpagasus_output'})

cidar_df.rename(columns={'model_output': 'cidar_output'}, inplace=True)
chat_df.rename(columns={'model_output': 'chat_output'}, inplace=True)
merged_df = pd.concat([cidar_df, alpagasus_df.drop(columns=['instruction']), chat_df.drop(columns=['instruction'])], axis=1)

merged_df.to_json('instructions/merged.json', orient='records', lines=False, force_ascii=False)
