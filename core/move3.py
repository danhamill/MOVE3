#-------------------------------------------------------------------------------
# Name          MOVE method USGS
# Description:  Tool to conduct gauge extension on a short record
#               using data from a long record gage. Conducted based
#               on guidance in Guidelines for Determining Flood Flow Frequency
#               Bulletin 17C, version 1.1 USGS May 2019
# Author:       Chandler Engel
#               US Army Corps of Engineers
#               Cold Regions Research and Engineering Laboratory (CRREL)
#               Chandler.S.Engel@usace.army.mil
# Author:       Daniel Hamill
#               US Army Corps of Engineers
#               Sacramento District
#               Chandler.S.Engel@usace.army.mil
# Created:      14 February 2020
# Updated:      5 August 2021
#               
#-------------------------------------------------------------------------------

import numpy as np


class MOVE3(object):

    def __init__(self):

        self.merge_data = merge_data

        #MOVE3 Constant Parameters
        self.long_record = list(self.merge_data.loc[self.merge_data.Record_Type == 'Long Record', 'FLOW'])
        self.long_years = list(self.merge_data.loc[self.merge_data.Record_Type == 'Long Record', 'WY'].dt.year)
        self.short_record =list(self.merge_data.loc[self.merge_data.Record_Type == 'Short Record', 'FLOW'])
        self.short_years = list(self.merge_data.loc[self.merge_data.Record_Type == 'Short Record', 'WY'].dt.year)
        self.concurrent_years = list(set(self.short_years) & set(self.long_years))

        self._ind1 = [self.long_years.index(year) for year in self.concurrent_years if year in self.long_years]
        self._ind2 = [self.short_years.index(year) for year in self.concurrent_years if year in self.short_years]

        self.con_long_record = np.array(self.long_record)[self.ind1]
        self.con_short_record = np.array(self.short_record)[self.ind2]
        self.additional_years = list(set(long_years)-set(short_years))
        self._ind3 =  [self.long_years.index(year) for year in self.additional_years if year in self.long_years]
        self.additonal_record = np.array(self.long_record)[self.ind3]

        self.n1 = len(self.con_short_record)
        self.n2 = len(self.additional_record)

        self.ybar1 = np.mean(self.con_short_record)
        self.xbar1 = np.mean(self.con_long_record)
        self.xbar2 = np.mean(self.additional_record)

        #Calculation Parameters
        self.s_sq_y1 = None
        self.s_sq_x1 = None
        self.s_sq_x2 = None
        self._bhat_top = 0
        self._bhat_bottom = 0
        self.bhat = None
        self.p_hat = None
        self.mu_hat_y = None
        self.sigma_hat_y_sq = None
        self.A1 = None
        self.A2 = None
        self.A3 = None
        self.A4 = None
        self.A = None
        self.B1 = None
        self.B2 = None
        self.B3 = None
        self.B4 = None
        self.B5 = None
        self.B6 = None
        self.B = None
        self.C1 = None
        self.C2 = None
        self.C3 = None
        self.C4 = None
        self.C5 = None
        self.C6 = None
        self.C7 = None
        self.C = None
        self.ne = None
        self.ne_int = None
        self.extension_record = None
        self.extension_years = None
        self.xe_bar = None
        self.s_sq_xe = None
        self.a = None
        self.b_sq1 = None
        self.b_sq2 = None
        self.b_sq3 = None
        self.b_sq4 = None
        self.b_sq5 = None
        self.b_sq = None
        self.b = None
        self.extension_short_record = None  

    def comp_variance(self, record):
        
        n1 = len(record)
        ybar = np.mean(record)
        s_sq_y = sum([(yi-ybar)**2 for yi in record]) / (n1-1)
        return s_sq_y

    def calculate(self):
        
        self.s_sq_y1 = self.comp_variance(self.con_short_record)
        self.s_sq_x1 = self.comp_variance(self.con_long_record)
        self.s_sq_x2 = self.comp_variance(self.additional_record)
        
        self.alpha_sq = (self.n2*(self.n1-4)*(self.n1-1))/((self.n2-1)*(self.n1-3)*(self.n1-2))

        for _i, _xi in enumerate(self.con_long_record):
            self._bhat_top += (_xi - self.xbar1)*(self.con_short_record[_i]-self.ybar1)
            self._bhat_bottom += (_xi-self.xbar1)**2

        self.beta_hat = self._bhat_top/self._bhat_bottom 
        self.p_hat = self.beta_hat * (np.sqrt(self.s_sq_x1)/np.sqrt(self.s_sq_y1))
        self.mu_hat_y = self.ybar1 + self.n2/(self.n1+self.n2)*self.beta_hat*(self.xbar2-self.xbar1)
        self.sigma_hat_y_sq = (1/(self.n1+self.n2-1))*((self.n1-1)*self.s_sq_y1 + (self.n2-1)*self.beta_hat**2*self.s_sq_x2 + self.n2-1)*self.alpha_sq*(1-self.p_hat**2)*self.s_sq_y1+(self.n1*self.n2)/(self.n1+self.n2)*self.beta_hat**2*(self.xbar2-self.xbar1)**2)

        self.A1 = (self.n2+2)*(self.n1-6)*(self.n1-8)/(self.n1-5)
        self.A2 = self.n1-4
        self.A3 = (self.n1*self.n2*(self.n1-4)/((self.n1-3)*(self.n1-2)))
        self.A4 = 2*self.n2*(self.n1-4)/(self.n1-3)
        
        self.A = self.A1 + self.A2*(self.A3-self.A4-4)
        
        self.B1 = 6*(self.n2+2)*(self.n1-6)/(self.n1-5)
        self.B2 = 2*(self.n1**2-self.n1-14)
        self.B3 = self.n1-4
        self.B4 = 2*self.n2*(self.n1-5)/(self.n1-3)
        self.B5 = 2*(self.n1+3)
        self.B6 = (2*self.n1*self.n2*(self.n1-4))/((self.n1-3)*(self.n1-2))

        self.B = self.B1 + self.B2 + self.B3*(self.B4-self.B5-self.B6)   
        
        self.C1 = 2*(self.n1+1)
        self.C2 = 3*(self.n2+2)/(self.n1-5)
        self.C3 = (self.n1+1)*(2*self.n1+self.n2-2)*(self.n1-3)/(self.n1-1)
        self.C4 = self.n1-4
        self.C5 = 2*self.n2/(self.n1-3)
        self.C6 = 2*(self.n1+1)
        self.C7 = self.n1*self.n2*(self.n1-4)/((self.n1-3)*(self.n1-2))
        
        self.C = self.C1 + self.C2 - self.C3 + self.C4*(self.C5+self.C6+self.C7)
        
        self.ne = 2/ ( (2/(self.n1-1)) + (self.n2/(((self.n1+self.n2-1)**2) * (self.n1-3))) * (self.A*self.p_hat**4 +self.B*self.p_hat**2 + self.C )) + 1 - self.n1 
        
        self.ne_int = int(round(self.ne))
        
        self.extension_record = self.additional_record[-self.ne_int:]
        self.extension_years = self.additional_years[-self.ne_int:]
        
        self.xe_bar = np.mean(self.extension_record)
        self.s_sq_xe = self.comp_variance(self.extension_record)
        
        self.a = ((self.n1+self.ne_int)*self.mu_hat_y-self.n1*self.ybar1)/self.ne_int
        
        self.b_sq1 = (self.n1 + self.ne_int-1)*self.sigma_hat_y_sq 
        self.b_sq2 = (self.n1-1)*self.s_sq_y1
        self.b_sq3 = self.n1*(self.ybar1-mu_hat_y)**2
        self.b_sq4 = self.ne_int*(self.a-mu_hat_y)**2
        self.b_sq5 = (self.ne_int-1)*self.s_sq_xe
        
        self.b_sq = (self.b_sq1 - self.b_sq2 - self.b_sq3 - self.b_sq4)/self.b_sq5
        
        self.b = np.sqrt(self.b_sq)
        
        self.extension_short_record = [int(round(10**(self.a+self.b*(xi-self.xe_bar)))) for xi in self.extension_record] 
        self.short_record_flows = [int(round(10**x)) for x in self.short_record]
        self.extended_short_record = self.extension_short_record + self.short_record_flows 
        self.extended_short_years = self.extension_years + self.short_years
        


def main():

    import csv
    with open('Suwanee.csv', 'r') as f:
        reader = csv.reader(f)
        y = list(reader)
        
        short_years = [int(y1[0]) for y1 in y]
        short_record = [int(y1[1]) for y1 in y]
    
    with open('Etowah.csv', 'r') as f:
        reader = csv.reader(f)
        x = list(reader)
        
        long_years = [int(x1[0]) for x1 in x]
        long_record = [int(x1[1]) for x1 in x]
    
    
    out = comp_extended_record(short_years, short_record, long_years, long_record)

    print(out)
    
if __name__ == "__main__":
    main()