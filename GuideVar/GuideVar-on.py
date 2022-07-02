"""
Modular prediction of off-target effects
@author: Wei He
@E-mail: whe3@mdanderson.org
@Date: 06/30/2021
"""

#################### Import all the packages #####################
from __future__ import division
from itertools import product
from keras import layers
from keras import models
from keras import optimizers
from keras import losses
from keras import metrics

import numpy as np
import pandas as pd
import os,sys,re,argparse,logging
##################################################################


logging.basicConfig(level=logging.DEBUG,  
                    format='%(levelname)s:%(asctime)s @%(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filemode='a')

parser = argparse.ArgumentParser(description = 'Predict on-target efficiency of sgRNAs for Cas9 variants')
parser.add_argument('-i','--inputfile',type=str,required=True, 
                    help= "Input file (.txt or .csv) with one sgRNA sequence (20bp) per line")
parser.add_argument('-p','--prefix',type=str,help='Prefix of the file to save the outputs,default: GuideVarOn_Test',default='GuideVarOn_Test',required=False)
parser.add_argument('-o','--outputdir',type=str,help="Directory to save output files,if no directory is given a folder named\nGuideVar_scores will be generated in current working directory",default='GuideVar_scores',required=False)

args = parser.parse_args()

from deephf_training_util import *
from deephf_prediction_util import *


def sgRNA2Vector(sg):
    vec = []
    for s in list(sg):
        if s == 'A': vec += [1,0,0,0]
        elif s == 'T': vec += [0,1,0,0]
        elif s == 'C': vec += [0,0,1,0]
        elif s == 'G': vec += [0,0,0,1]
    return vec


def SeqFeat(df_all):
    df_all.index = range(df_all.shape[0])
    vec_all = []
    for sg in df_all['sgRNA']:
        sg = sg[1:]
        vec = sgRNA2Vector(sg)
        vec_all.append(vec)
    
    df_seq = pd.DataFrame(vec_all,columns=col_ls) 
    df_all = pd.concat([df_all,df_seq],axis=1)

    count_all = []

    for sg in df_all['sgRNA']:
        sg = sg[1:]
        sg_di = [sg[i:i+2] for i in range(19)]
        di_count = []
        for di in di_ls:
            di_count.append(sg_di.count(di)/19)
        count_all.append(di_count)
    
    df_count = pd.DataFrame(count_all,columns=di_ls)
    df_all = pd.concat([df_all,df_count],axis=1)
    
    return df_all


def GuideVarOn(df_train,df_test,m,n):
    np.random.seed(2345)
    model_hf = models.load_model('/GuideVar/models/hf_rnn_model.hd5')
    model_wt = models.load_model('/GuideVar/models/DeepWt_U6.hd5')
    
    X,X_biofeat = get_embedding_data(df_train,feature_options)
    Y,Y_biofeat = get_embedding_data(df_test,feature_options)
    X_seq = df_train.loc[:,di_ls+col_ls]
    Y_seq = df_test.loc[:,di_ls+col_ls]

    base_model1 = models.Model([model_hf.layers[0].input,model_hf.layers[5].input],outputs=model_hf.layers[9].output)
    base_model2 = models.Model([model_wt.layers[0].input,model_wt.layers[5].input],outputs=model_wt.layers[7].output)
    base_model1.trainable = False
    base_model2.trainable = False
    
    sequence_input = layers.Input(shape=(22,))
    biological_input = layers.Input(shape=(X_biofeat.shape[1],))
    

    x = base_model1([sequence_input,biological_input])
    y = base_model2([sequence_input,biological_input])
    z = layers.concatenate([x, y])
    #x = keras.layers.concatenate([x, biological_input])
    seq_input = layers.Input(shape=(X_seq.shape[1],))
    i = layers.concatenate([z,seq_input])

    dense1 = layers.Dense(m,activation='relu')(i)
    outputs = layers.Dense(1)(dense1)
    
    df_test['DeepHF.score'] = model_hf.predict([Y,Y_biofeat])
    model = models.Model(inputs=[sequence_input, biological_input,seq_input], outputs=outputs)
    model.compile(loss='mean_squared_error', optimizer=optimizers.RMSprop(), metrics=[metrics.MeanSquaredError()])
    model.fit([X,X_biofeat,X_seq],np.array(df_train['VD20']),epochs=n)
    
    df_test['GuideVar.On'] = [s[0] for s in list(model.predict([Y,Y_biofeat,Y_seq]))]
    
    return df_test


col_ls =[] 
for j in range(1,20):
    for nt in ['A','T','C','G']:
        col_ls.append(nt+'_'+str(j))
            
di_ls = [s[0]+s[1] for s in list(product('ATGC', repeat=2))]
df_train = pd.read_csv('/GuideVar/data/GuideVar-onTrainingSet.csv')

Inputfile =  args.inputfile

try:
    os.mkdir(args.outputdir)
    logging.info('Creat the outputdir {} to place result files'.format(args.outputdir))
except OSError:
    logging.warning('outputdir {} already exist'.format(args.outputdir))

outputdir = os.path.join(os.getcwd(),args.outputdir) ## Set the path to outputdir
prefix = args.prefix

if Inputfile == None:
    parser.print_help()
    sys.exit(0)
        
logging.info('Reading the input files ...')
if '.txt' in Inputfile:
    df_in = pd.read_csv(Inputfile, delimiter="\t", header=None, names=['sgRNA'])
elif '.csv' in Inputfile:
    df_in = pd.read_csv(Inputfile, header=None, names=['sgRNA'])
else:
    logging.error('Oops! Something wrong with the input file formats, accepted files includes .csv and .txt are accepted, would you please check and provide correct file format.')
    sys.exit(-1)

print(df_in)

df_in['21mer'] = [(s+'G').upper() for s in df_in['sgRNA']]
df_test = SeqFeat(df_in)
df_out = GuideVarOn(df_train,df_test,6,8)
df_out.loc[:,['sgRNA','21mer','DeepHF.score','GuideVar.On']].to_csv(os.path.join(outputdir,prefix+'_GuideVarOn.csv'))

logging.info('^o^ Great! Job finished and results successfully saved, Check it in the output folder! Bye!')
