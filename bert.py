from ipywidgets import *
from IPython.display import display
from ipywidgets import widgets
from IPython.display import clear_output

from difflib import Differ


class CheckAnswers(object):
    def __init__(self, bert_file="res.txt", crf_file="res_crf_train_longer.txt"):
        with open(bert_file, 'r') as fin:
            bert_res = fin.readlines()
        with open(crf_file, 'r') as fin:
            crf_res = fin.readlines()
        self.cmp_res = []
        for i, bert in enumerate(bert_res):
            crf = crf_res[i]
            ctx, bert_pred = bert.split('|||')
            crf_pred = crf.split('|||')[1]
            bert_pred = bert_pred.strip()
            crf_pred = crf_pred.strip()
            if bert_pred == 'empty': bert_pred = ''
            if bert_pred != crf_pred:
                self.cmp_res.append([ctx, bert_pred, crf_pred])

        self.check_box = []

    def num_of_differs(self):
        '''return the number of different entries'''
        return len(self.cmp_res)

    def print_differ_to_html(self, n):
        ctx, bert_pred, crf_pred = self.cmp_res[n]
        print(ctx, '|||', bert_pred, '|||', crf_pred)

    def to_buttons(self, n):
        ctx, bert, crf = self.cmp_res[n]

        item_layout = Layout(width='790px')
        ctx_text = widgets.HTML(
            value="%s |||  %s  ||| %s" % (ctx, bert, crf),
            placeholder='',
            description='',
            layout=item_layout,
        )

        cb_bert = widgets.Checkbox(
            value=True,
            description='bert',
            disabled=False
        )

        cb_crf = widgets.Checkbox(
            value=False,
            description='crf',
            disabled=False
        )
        box_layout = Layout(
            border='3px solid black',
            width='800px',
            height='',
            flex_flow='row wrap',
            display='flex')
        items = [ctx_text, cb_bert, cb_crf]
        box = Box(children=items, layout=box_layout)
        self.check_box.append(box)
        display(box)

    def get_bert_values(self, n):
        '''return the checkbox value of
        the nth bert predition result'''
        return int(self.check_box[n].children[1].value)

    def get_crf_values(self, n):
        '''return the checkbox value of
        the nth crf predition result'''
        return int(self.check_box[n].children[2].value)

    def save_check_results(self):
        with open("bert_vs_crf_human_checked.txt", "w") as fout:
            fout.write("# bert_prediction,  crf_prediction\n")
            for n in range(len(self.check_box)):
                fout.write("#")
                fout.write(self.check_box[n].children[0].value)
                fout.write("\n")
                fout.write("%s" % self.get_bert_values(n))
                fout.write(" ")
                fout.write("%s" % self.get_crf_values(n))
                fout.write("\n")

ca = CheckAnswers()
ca.num_of_differs()
for n in range(ca.num_of_differs()):
    ca.to_buttons(n)

ca.get_bert_values(n=7)

ca.save_check_results()
import numpy as np

res = np.loadtxt("bert_vs_crf_human_checked.txt")

print(res[:, 0])
print(res[:, 1])
