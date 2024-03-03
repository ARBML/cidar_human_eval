import os
from collections import defaultdict
from database import save_response, read_responses
import gradio as gr
import pandas as pd
import random

css = """
    .rtl
    {
        text-align: right;
    }
    .usr-inst{
    text-align:center;
    background-color: #3e517e;
    border: solid 1px;
    border-radius: 5px;
    padding: 10px;
    }
    .svelte-1kzox3m{
    justify-content: end;
    }
    .svelte-sfqy0y{
    border:none; 
    }
    .svelte-90oupt{
    background-color: #0b0f19;
    padding-top: 0px;
    }
    #component-4{
    border: 1px solid;
    padding: 5px;
    background-color: #242433;
    border-radius: 5px;
    }
    
    """

file_path = 'instructions/merged.json'
df = pd.read_json(file_path, orient='records', lines=False)

# that keeps track of how many times each question has been used
question_count = {index: 0 for index in df.index}
model_rankings = defaultdict(lambda: {'1st': 0, '2nd': 0, '3rd': 0})
curr_order = ['CIDAR', 'CHAT', 'ALPAGASUS']

def get_rank_suffix(rank):
    if 11 <= rank <= 13:
        return 'th'
    else:
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        return suffixes.get(rank % 10, 'th')


def process_rankings(user_rankings):
    print("Processing Rankings:", user_rankings)  # Debugging print
    save_response(user_rankings)
    print(read_responses())
    return


def get_questions_and_answers():
    available_questions = [index for index, count in question_count.items() if count < 3]
    index  = random.sample(available_questions, min(1, len(available_questions)))[0]
    question_count[index] += 1

    question = df.loc[index, 'instruction']
    answers_with_models = [
        (df.loc[index, 'cidar_output'], 'CIDAR'),
        (df.loc[index, 'chat_output'], 'CHAT'),
        (df.loc[index, 'alpagasus_output'], 'ALPAGASUS')
    ]
    random.shuffle(answers_with_models)  # Shuffle answers with their IDs
    curr_order = [model for _, model in answers_with_models]
    return (question, answers_with_models)

def reload_components():
    question, answers = get_questions_and_answers()
    user_instructions_txt = " في الصفحة التالية ستجد طلب له ثلاث إجابات مختلفة. من فضلك اختر مدي توافق كل إجابة مع الثقافة العربية."
    radios = []
    user_instructions = gr.Markdown(rtl=True, value= f'<h1 class="usr-inst">{user_instructions_txt}</h1>')

    question_md = gr.Markdown(rtl=True, value= f'<b> {question} </b>')
                
    for answer, model in answers:
        radios.append(gr.Markdown(rtl = True, value= answer))
        radios.append(gr.Radio(elem_classes = 'rtl', choices = ['متوافق', 'متوافق جزئياً', 'غير متوافق'], value = 'غير متوافق', label = ""))            
    
    return [user_instructions, question_md] + radios

def rank_interface():
    def rank_fluency(*radio_selections):
        user_rankings = {}
        for i in range(0, len(radio_selections), 3):  # Process each set of 3 dropdowns for a question
            selections = radio_selections[i:i+3]
            for j, chosen_answer in enumerate(selections):
                model_name = curr_order[j]
                if chosen_answer == 'غير متوافق':
                    user_rankings[model_name] =  3 
                elif chosen_answer == 'متوافق جزئياً':
                    user_rankings[model_name] =  2
                elif chosen_answer == 'متوافق':
                    user_rankings[model_name] =  1
        process_rankings(user_rankings)
        return "سجلنا ردك، ما قصرت =)"
        
    # Create three dropdowns for each question for 1st, 2nd, and 3rd choices
    inputs = []
    with gr.Blocks(css=css) as demo:
        with gr.Row():
            with gr.Column():
                outptus= reload_components()
                out_text = gr.Markdown("", rtl = True)

                gr.Button("Submit").click(
                    fn=rank_fluency,
                    inputs=outptus[1:],
                    outputs=out_text
                ).then(
                    fn=reload_components,
                    outputs = outptus
                )

                gr.Button("Skip").click(
                    fn=reload_components,
                    outputs=outptus
                )
           
    return demo

questions = get_questions_and_answers()
iface = rank_interface()
iface.launch(share = True)
