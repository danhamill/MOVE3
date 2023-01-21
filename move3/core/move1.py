#-------------------------------------------------------------------------------
# Name          MOVE1 method USGS
# Description:  Tool to conduct gauge extension on a short record
#               using data from a long record gage. Conducted based
#               on guidance in Guidelines for Determining Flood Flow Frequency
#               Bulletin 17C, version 1.1 USGS May 2019
# Author:       Daniel Hamill
#               US Army Corps of Engineers
#               Sacramento District
#               Daniel.D.Hamill@usace.army.mil
# Created:      09 January 2023
# Comments:     Tested against HEC tutorial
#               https://www.hec.usace.army.mil/confluence/display/SSPTutorialsGuides/Daily+Flow+Record+Extension+with+MOVE.1      
#-------------------------------------------------------------------------------

import numpy as np

class MOVE1(object):

    def __init__(self, merge_data, roundInt=True) -> None:
        
        self.merge_data = merge_data
        self.roundInt = roundInt
        
        #MOVE1 Constant Parameters
        self.long_record_flows = np.log10(
            list(
                self.merge_data.loc[self.merge_data.recordType == 'Long Record', 'FLOW']
            )
        )
        self.long_dates = list(
            self.merge_data.loc[
                self.merge_data.recordType == 'Long Record', 'date'
                ].dt.to_pydatetime()
            )

        assert all(x<y for x,y in zip(self.long_dates, self.long_dates[1:]))
        self.short_record_flows =np.log10(
            list(
                self.merge_data.loc[self.merge_data.recordType == 'Short Record', 'FLOW']
                )
        )
        self.short_dates = list(
            self.merge_data.loc[
                self.merge_data.recordType == 'Short Record', 'date'
                ].dt.to_pydatetime()
            )
        assert all(x<y for x,y in zip(self.short_dates, self.short_dates[1:]))
        
        self.concurrent_dates = [i for i in self.long_dates if i in self.short_dates]

        self._ind1 = [
            self.long_dates.index(date) for date in 
                        self.concurrent_dates if date in self.long_dates
            ]

        self._ind2 = [
            self.short_dates.index(date) for date in 
                        self.concurrent_dates if date in self.short_dates]

        self.con_long_flows = np.array(self.long_record_flows)[self._ind1]

        self.con_short_flows = np.array(self.short_record_flows)[self._ind2]

        self.additional_dates = [
            i for i in self.long_dates if i not in self.short_dates
        ]

        self._ind3 =  [
            self.long_dates.index(year) for year 
                in self.additional_dates if year in self.long_dates
        ]

        self.additional_flows  = np.array(self.long_record_flows)[self._ind3]

        self.n1 = len(self.con_short_flows)
        self.n2 = len(self.additional_flows)

        self.ybar1 = np.mean(self.con_short_flows)
        self.xbar1 = np.mean(self.con_long_flows)
        self.xbar2 = np.mean(self.additional_flows)

        #Calculation Parameters
        self.s_sq_y1 = None
        self.s_sq_x1 = None
        self.s_sq_x2 = None
        self._bhat_top = 0.0
        self._bhat_bottom = 0.0

    def comp_variance(self, record):
        if len(record)>1:
            n1 = len(record)
            ybar = np.mean(record)
            s_sq_y = sum([(yi-ybar)**2 for yi in record]) / (n1-1)
            return s_sq_y
        else:
            return 0
    # if computing the variance for ne=1 this fails

    def calculate(self):

        # Equation 8-4
        self.s_sq_y1 = self.comp_variance(self.con_short_flows) 

        # Equation 8-5
        self.s_sq_x1 = self.comp_variance(self.con_long_flows) 

        # Equation 8-6
        self.s_sq_x2 = self.comp_variance(self.additional_flows) 

        for _i, _xi in enumerate(self.con_long_flows):
            self._bhat_top += (_xi - self.xbar1)*(self.con_short_flows[_i]-self.ybar1)
            self._bhat_bottom += (_xi-self.xbar1)**2
        
        # Equation 8-10
        self.beta_hat = self._bhat_top/self._bhat_bottom 

        # Equation 8-9
        self.p_hat = self.beta_hat * (np.sqrt(self.s_sq_x1)/np.sqrt(self.s_sq_y1)) 

        if self.roundInt:
            self.short_record_flows = [int(round(10**x)) for x in self.short_record_flows]
        else:
            self.short_record_flows = [10**x for x in self.short_record_flows]
        
        missing_dates = [i for i in self.long_dates if i not in self.short_dates]
        idx_lus = [self.long_dates.index(i) for i in missing_dates]
        
        self.extension_flows = []
        self.extension_dates = []
        for idx_lu in idx_lus:
            self.extension_flows.append(self.long_record_flows[idx_lu])
            self.extension_dates.append(self.long_dates[idx_lu])

        self.slope = np.sqrt(self.s_sq_y1/self.s_sq_x1)
        self.intercept = self.ybar1

        self.extension_short_record = [
            float(
                round(
                    10**(
                        self.intercept+self.slope*(xi-self.xbar1)
                    )
                )
            ) for xi in self.extension_flows] 



