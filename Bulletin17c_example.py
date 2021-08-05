import pandas as pd
import numpy as np
from core.move3 import MOVE3



DATA_URLS = {'long':'https://raw.githubusercontent.com/danhamill/MOVE3/master/data/Etowah.csv',
             'short': 'https://raw.githubusercontent.com/danhamill/MOVE3/master/data/Suwanee.csv'}

def merge_flow_data(short_data, long_data):
    #Merge short and long data for chart plotting
    short_data.loc[:,'Record_Type'] = 'Short Record'
    long_data.loc[:, 'Record_Type'] = 'Long Record'
    merge = pd.concat([long_data, short_data])
    merge.loc[:,'WY'] = pd.to_datetime(merge.WY, format = '%Y')
    return merge

def load_data(fpath):
    data = pd.read_csv(fpath, header=None, names = ['WY','FLOW'])
    return data

def main():
    short_data = load_data(DATA_URLS['short'])
    long_data = load_data(DATA_URLS['long'])


    merge = merge_flow_data(short_data, long_data)

    res = MOVE3(merge)
    res.calculate()


if __name__ == '__main__':
    main()