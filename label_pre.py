from history import talks
from ipywidgets import *
from IPython.display import display
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import clear_output
import json
import ast
import tkinter
from box import Box
# from tkinter import *
# displaying the labelling widget
##text = widgets.Text(description="Label the speaker by clicking buttons", width=200)
##display(text)

def check_existence(sentence, idx, saved_file="label_history.txt"):

    speakers = []
    contexts = []
    combined_res = []
    # combine N speakers with M contexts to get N*M examples
    with open(saved_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            # res = json.loads(line)
            res = ast.literal_eval(line)
            speakers.append(res['speaker'])
            ctx = res['context']
            ctx_left = ctx[:res["istart"]]
            ctx_right = ctx[res["iend"]:]
            contexts.append([ctx_left, ctx_right, res["istart"]])

    for speaker in speakers:
        for ctx in contexts:
            try:
                new_ctx = ctx[0] + speaker + ctx[1]
                istart = ctx[2]
                new_iend = istart + len(speaker)
                res = {'uid':0,
                   'context':new_ctx,
                   'speaker':speaker,
                   'istart':istart,
                   'iend':new_iend}
                combined_res.append(res)
#                 print(res)

                if sentence == res['context']:

                    res['uid'] = idx
                    return True, res
            except:
                continue

#     print(combined_res)
    return False, None


class ToButtons(object):
    def __init__(self, input_str):
        self.input_str = input_str
        self.res = None
        self.buttons = []
        self.pos_labels = []
        item_layout = Layout(height='40px', min_width='40px', max_width='40px')
        items = [Button(layout=item_layout,
                        description=input_str[i],
                        value=i,
                        button_style='info')
                 for i in range(len(input_str))]

        box_layout = Layout(
            border='3px solid black',
            width='800px',
            height='',
            flex_flow='row wrap',
            display='flex')
        carousel = Box(children=items, layout=box_layout)
        display(carousel)
        #         print(items)
        for value, item in enumerate(items[:-2]):
            item.value = value
            item.on_click(self.on_button_clicked)

    # function to deal with the checkbox update button
    def on_button_clicked(self, b):
        print("@on_button_clicked")
        self.pos_labels.append(b.value)
        print(self.pos_labels)
        if len(self.pos_labels) > 2:
            # raise ValueError("only click the start and the end word")
            print("Warning: click more than 2 times, will use the last click \
                  as the end of the label position")

    def return_results(self):
        print("@return_results")
        if len(self.pos_labels) == 0:
            self.pos_labels.append(-1)
        return self.input_str, self.pos_labels[0], self.pos_labels[-1] + 1


class LabelSpeaker(object):
    def __init__(self, talk_list, progress=0, save_to='label_history.txt'):
        self.progress = progress
        self.saving_path = save_to
        self.talk_list = talk_list
        self.sentence_buttons = ToButtons(talk_list[self.progress]['context'])
        self.submit_layout = Layout(height='40px', min_width='40px')
        self.submit = Button(layout=self.submit_layout,
                             description="submit",
                             button_style='warning')
        self.submit.on_click(self.on_button_submit)
        display(self.submit)

    def save_one_item(self, progress, sentence, istart, iend):
        speaker = None
        print("@save_one_item")
        if istart != -1: speaker = sentence[istart:iend]
        res = {'uid': progress, 'context': sentence,
               'speaker': speaker,
               'istart': istart, 'iend': iend}
        print(self.saving_path)
        with open(self.saving_path, 'a') as f:
            f.write(res.__repr__())
            f.write('\n')

    def on_button_submit(self, b):
        print("@on_button_submit")
        sentence, istart, iend = self.sentence_buttons.return_results()
        clear_output()
        print("@on_button_submit", sentence[istart:iend])
        self.save_one_item(self.progress, sentence, istart, iend)
        while True:
            print("@on_button_submit")
            self.progress = self.progress + 1
            print("@on_button_submit", self.progress)
            print("@on_button_submit", len(self.talk_list))
            if len(self.talk_list) == self.progress:
                return
            new_sentence = self.talk_list[self.progress]['context']
            existed, res = check_existence(new_sentence, self.progress)

            if existed:
                self.save_one_item(self.progress, new_sentence,
                                   res['istart'], res['iend'])
            else:
                print("！" * 10)
                break
        #### after check exist
        self.sentence_buttons = ToButtons(new_sentence)
        self.submit = Button(layout=self.submit_layout,
                             description="submit",
                             button_style='warning')
        self.submit.on_click(self.on_button_submit)
        print("@after check exist")
        display(self.submit)

b1 = LabelSpeaker(talks, progress=0)


def data_augmentation(saved_file="label_history.txt"):
    speakers = []
    contexts = []
    combined_res = []
    # combine N speakers with M contexts to get N*M examples
    with open(saved_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            res = ast.literal_eval(line)
            speakers.append(res['speaker'])
            ctx = res['context']
            ctx_left = ctx[:res["istart"]]
            ctx_right = ctx[res["iend"]:]
            contexts.append([ctx_left, ctx_right, res["istart"]])

    uid = 0
    len_truncate = 128
    for speaker in speakers:
        for ctx in contexts:
            try:
                new_ctx = ctx[0] + speaker + ctx[1]
                istart = ctx[2]
                new_iend = istart + len(speaker)
                new_speaker = speaker
                # truncate the input if the speaker is contained in the last 128 words
                if len(new_ctx) > len_truncate and (len(new_ctx) - istart) < len_truncate:
                    truncated_ctx = new_ctx[-len_truncate:]
                    istart = ctx[2] - (len(new_ctx) - len_truncate)
                    new_iend = istart + len(speaker)
                    new_speaker = truncated_ctx[istart:new_iend]
                res = {'uid': uid,
                       'context': new_ctx,
                       'speaker': new_speaker,
                       'istart': istart,
                       'iend': new_iend}
                combined_res.append(res)
                uid = uid + 1
            except:
                continue
    return combined_res

augmented_data = data_augmentation()
print(augmented_data[0],len(augmented_data))
from tqdm import tqdm
with open("augmented_history_speaker.py", "w") as fout:
    fout.write("speakers=[")
    for item in tqdm(augmented_data):
        fout.write(item.__repr__())
        fout.write(',\n')
    fout.write(']')



from augment_data import speakers
print(len(speakers))
