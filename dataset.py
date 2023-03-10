from augment_data import new_data
import random
speakers = new_data
random.shuffle(speakers)
num = len(speakers)
ntrain = int(num*0.7)
nvalid = int(num*0.2)
ntest  = num - ntrain -nvalid

def construct_dataset(kind='training', start_idx=0, end_idx=ntrain, save_to_disk=True):
    xtrain = []
    ytrain = []
    for speaker in speakers[:ntrain]:
        ctx = speaker['context']
        xtrain.append(speaker['context'])
        res = ctx[speaker['istart']: speaker['iend']]
        ytrain.append([speaker['istart'], speaker['iend'], res])
    
    if save_to_disk:
        with open("%s_large_sentence.csv"%kind, "w") as fxtrain:
            for x in xtrain:
                fxtrain.write(x)
                fxtrain.write('\n')
        
        with open("%s_large_labels.csv"%kind, "w") as fytrain:
            for y in ytrain:
                fytrain.write('%s ||| %s ||| %s'%(y[0], y[1], y[2]))
                fytrain.write('\n')

    return xtrain, ytrain

xtrain, ytrain = construct_dataset(kind='training', start_idx=0, end_idx=ntrain)

#### use the unlabelled data for testing
##xvalid, yvalid = construct_dataset(kind='validation', start_idx=ntrain, end_idx=ntrain+nvalid)
##xtest,  ytest  = construct_dataset(kind='testing', start_idx=ntrain+nvalid, end_idx=ntrain+nvalid+ntest)
