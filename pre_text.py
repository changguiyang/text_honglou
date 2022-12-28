import os
from tqdm import tqdm_notebook

from tqdm import tqdm

def get_conversations(sentence):
    '''get the start and end position of the conversation in the
    input sentence
    Returns:
      start_index: int, the starting index in the sentence
      end_index: int, the ending index in the sentence
      conversation: str, the conversation'''
    end_symbols = ['"', '“', '”','"',"“",'"']
    istart, iend = -1, -1
    talks = []
    ### get the start and end position for conversation
    for i in range(1, len(sentence)):
        if (not istart == -1) and sentence[i] in end_symbols:
            iend = i
            conversation = {'istart':istart, 'iend':iend, 'talk':sentence[istart+1:iend]}
            talks.append(conversation)
            istart = -1
        if sentence[i-1] in [':', '：'] and sentence[i] in end_symbols:
            istart = i
    ### get the context from where one can extract speaker
    contexts = []
    if len(talks):
        for i in range(len(talks)):
            if i == 0:
                contexts.append(sentence[:talks[i]['istart']])
            else:
                contexts.append(sentence[talks[i-1]['iend']+1:talks[i]['istart']])
        # append the paragraph after the conversation if iend != len(sentence)
        if talks[-1]['iend'] != len(sentence):
            contexts.append(sentence[talks[-1]['iend']+1:])
        else:
            contexts.append(' ')
        ### the situation is not considered if the speaker comes after the talk
        for i in range(len(talks)):
            talks[i]['context'] = contexts[i] #+ 'XXXXX' + contexts[i+1]

    return talks, contexts

def extract_corpus_json(book_name="history.txt", save_as="history.py"):
    fout = open(save_as, "w")
    count = 0
    with open(book_name, "r") as fin:
        # fout.write('#!/usr/bin/env python\n')
        fout.write('talks = [')
        lines = fin.readlines()
        for line in tqdm(lines):
            talks, contexts = get_conversations(line.strip())
            if len(talks) > 0:
                for talk in talks: #print(talk, '|||\n')
                    fout.write(talk.__repr__())
                    fout.write(',\n')
                    count += 1
        fout.write(']')
        print(count)
    fout.close()


extract_corpus_json()
