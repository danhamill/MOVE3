import pandas as pd
import numpy as np
from move3.core.move3 import MOVE3
from move3.core.move1 import MOVE1

DATA_URLS = {
    'long':'https://raw.githubusercontent.com/danhamill/MOVE3/master/move3/data/Etowah.csv',
    'short':'https://raw.githubusercontent.com/danhamill/MOVE3/master/move3/data/Suwanee.csv'
}

class TestClass:

    def merge_flow_data(self, short_data, long_data):

        merge = pd.concat([long_data, short_data])

        if 'WY' in merge.columns:
            merge.loc[:,'WY'] = pd.to_datetime(merge.WY, format = '%Y')
        return merge

    def getCSVdata(self, fpath, recordType):
        tmp = pd.read_csv(fpath, header=None, names = ['WY','FLOW'])
        tmp.loc[:,'recordType'] = recordType
        return tmp

    def test_move1(self):

        extendData = pd.read_feather(r"move3\data\move1_extended_data.feather")
        mergeData = pd.read_feather(r"move3\data\MOVE1_testData.feather")

        res = MOVE1(mergeData)
        res.calculate()

        outIdx = pd.Index(data = res.extension_dates, name ='date')
        output = pd.DataFrame(
            index = outIdx, 
            data={'FLOW':res.extension_short_record}
        ).sort_index()

        #slope
        assert np.allclose(res.slope, 0.767, rtol=1e-3) 

        #intercept
        assert np.allclose(res.intercept, 2.619, rtol=1e-3 )

        #linear correlation
        assert np.allclose(res.p_hat, 0.853, rtol=1e-3)
        
        #extension values
        assert np.allclose(output.FLOW.values, extendData.FLOW.values, rtol=1)

        print('MOVE1 passed all tests....')
        
    def test_move3(self):
        short_data = self.getCSVdata(DATA_URLS['short'], 'Short Record')
        long_data = self.getCSVdata(DATA_URLS['long'],  'Long Record')

        merge = self.merge_flow_data(short_data, long_data)

        res = MOVE3(merge)
        res.calculate()        

        assert np.allclose(res.ne_var, 13, rtol=1e-5)

        assert np.allclose(res.a_var, 3.43, rtol=1e-2)

        assert np.allclose(res.xe_bar_var, 4.14, rtol=1e-3)

        b17c_resluts = [
            2830,2010,2300,2200,4310,4510,3730,5180,3040,6070,
            1460,2440
        ]
        
        assert np.allclose(
            res.extended_short_record_var[:len(b17c_resluts)], 
            b17c_resluts, 
            rtol=10
            )
            
        print('MOVE3 passed all tests...')


if __name__ == '__main__':

    tc = TestClass()
    tc.test_move1()
    tc.test_move3()






        





