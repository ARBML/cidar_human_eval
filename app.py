import os
os.system("pip install pymongo")
from collections import defaultdict
from database import save_response
import gradio as gr
import pandas as pd
import random

css = """
    .rtl
    {
        text-align: right;
        dir: rtl;
    }
    #component-19
    {
        text-align: right;
        flex-direction: row-reverse; /* Makes the main-axis start from the right /
        justify-content: flex-start; / Aligns children to the right */
    }
    #component-17
    {
    text-align: right;
    float: right;
    }
    .svelte-1kzox3m{
    justify-content: end;
    }
    """

file_path = 'instructions/merged.json'
df = pd.read_json(file_path, orient='records', lines=False)

# that keeps track of how many times each question has been used
question_count = {index: 0 for index in df.index}
model_rankings = defaultdict(lambda: {'1st': 0, '2nd': 0, '3rd': 0})


def get_rank_suffix(rank):
    if 11 <= rank <= 13:
        return 'th'
    else:
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        return suffixes.get(rank % 10, 'th')


def process_rankings(user_rankings):
    print("Processing Rankings:", user_rankings)  # Debugging print
    for answer_id, rank in user_rankings:
        model = answer_id.split('_')[0]  # Extracting the model name from the answer_id
        rank_suffix = get_rank_suffix(rank)
        model_rankings[model][f'{rank}{rank_suffix}'] += 1  # Using the correct suffix based on the rank
        model_rankings_dict = dict(model_rankings)

    save_response(model_rankings_dict)
    print("Updated Model Rankings:", model_rankings)  # Debugging print
    return


def get_questions_and_answers():
    available_questions = [index for index, count in question_count.items() if count < 3]
    selected_indexes = random.sample(available_questions, min(4, len(available_questions)))
    for index in selected_indexes:
        question_count[index] += 1

    questions_and_answers = []
    for index in selected_indexes:
        question = df.loc[index, 'instruction']
        answers_with_models = [
            (df.loc[index, 'cidar_output'], 'CIDAR'),
            (df.loc[index, 'chat_output'], 'CHAT'),
            (df.loc[index, 'alpagasus_output'], 'ALPAGASUS')
        ]
        random.shuffle(answers_with_models)  # Shuffle answers with their IDs
        questions_and_answers.append((question, answers_with_models))

    return questions_and_answers


def rank_interface():
    def rank_fluency(*radio_selections):
            user_rankings = []
            
            for i in range(0, len(radio_selections), 4):  # Process each set of 3 dropdowns for a question
                selections = radio_selections[i+1:i+4]
                question_index = i // 4
                _, model_answers = questions[question_index]
                print(model_answers)
                for j, chosen_answer in enumerate(selections):
                    if chosen_answer == 'غير متوافق':
                        user_rankings.append((model_answers[j][1], 3))  # j is the rank (1, 2, or 3)
                    elif chosen_answer == 'متوافق جزئياً':
                        user_rankings.append((model_answers[j][1], 2))
                    elif chosen_answer == 'متوافق':
                        user_rankings.append((model_answers[j][1], 1))
            process_rankings(user_rankings)
            return "سجلنا ردك، ما قصرت =)"
    
    questions = get_questions_and_answers()
    
    # Create three dropdowns for each question for 1st, 2nd, and 3rd choices
    inputs = []
    with gr.Blocks(css=css) as demo:
        with gr.Row():
            with gr.Column():
                for question, answers in questions[0:2]:
                    inputs.append(gr.Markdown(rtl=True, value= question))
                    
                    answers_text = [answer for answer, _ in answers]
                    for i in range(0, 3):
                        inputs.append(gr.Radio(elem_classes = 'rtl', choices = ['متوافق', 'متوافق جزئياً', 'غير متوافق'], value = 'غير متوافق', label = answers_text[i]))
                        # inputs.append(gr.Markdown(answers_text[i]))
            
                outputs = gr.Markdown("", rtl = True)

                gr.Button("Submit").click(
                    fn=rank_fluency,
                    inputs=inputs,
                    outputs=outputs
                )
           
    return demo

iface = rank_interface()
iface.launch(share = True)
