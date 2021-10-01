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
#               Added mean and variance based record extensions
#               Object Oriented MOVE.3
#-------------------------------------------------------------------------------

import numpy as np


class MOVE3(object):

    def __init__(self, merge_data):

        self.merge_data = merge_data

        #MOVE3 Constant Parameters
        self.long_record = np.log10(list(self.merge_data.loc[self.merge_data.Record_Type == 'Long Record', 'FLOW']))
        self.long_years = list(self.merge_data.loc[self.merge_data.Record_Type == 'Long Record', 'WY'].dt.year)
        self.short_record =np.log10(list(self.merge_data.loc[self.merge_data.Record_Type == 'Short Record', 'FLOW']))
        self.short_years = list(self.merge_data.loc[self.merge_data.Record_Type == 'Short Record', 'WY'].dt.year)
        self.concurrent_years = list(set(self.short_years) & set(self.long_years))

        self._ind1 = [self.long_years.index(year) for year in self.concurrent_years if year in self.long_years]
        self._ind2 = [self.short_years.index(year) for year in self.concurrent_years if year in self.short_years]

        self.con_long_record = np.array(self.long_record)[self._ind1]
        self.con_short_record = np.array(self.short_record)[self._ind2]
        self.additional_years = list(set(self.long_years)-set(self.short_years))
        self._ind3 =  [self.long_years.index(year) for year in self.additional_years if year in self.long_years]
        self.additional_record  = np.array(self.long_record)[self._ind3]

        self.n1 = len(self.con_short_record)
        self.n2 = len(self.additional_record )

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

        self.short_record_flows = None

        #Mean based Estimates
        self.ne_n1_mean = None
        self.ne_n1_mean_int = None
        self.extension_record_mean = None
        self.extension_years_mean = None
        self.xe_bar_mean = None
        self.s_sq_xe_mean = None
        self.a_mean = None
        self._b_sq1_mean = None
        self._b_sq2_mean = None
        self._b_sq3_mean = None
        self._b_sq4_mean = None
        self._b_sq5_mean = None
        self.b_sq_mean = None
        self.b_mean = None
        self.extension_short_record_mean = None 
        self.extended_short_years_mean = None 
        self.mean_extension_equation = None


        #Variance Based Estimates
        self.ne_n1_var = None
        self.ne_n1_var_int = None
        self.extension_record_var = None
        self.extension_years_var = None
        self.xe_bar_var = None
        self.s_sq_xe_var = None
        self.a_var = None
        self._b_sq1_var = None
        self._b_sq2_var = None
        self._b_sq3_var = None
        self._b_sq4_var = None
        self._b_sq5_var = None
        self._b_sq_var = None
        self.b_var = None
        self.extension_short_record_var = None
        self.extended_short_years_var = None
        self.var_extension_equation = None  

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
        self.sigma_hat_y_sq = (1/(self.n1+self.n2-1))*((self.n1-1)*self.s_sq_y1 + (self.n2-1)*self.beta_hat**2*self.s_sq_x2 + (self.n2-1)*self.alpha_sq*(1-self.p_hat**2)*self.s_sq_y1+(self.n1*self.n2)/(self.n1+self.n2)*self.beta_hat**2*(self.xbar2-self.xbar1)**2)

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

        self.short_record_flows = [int(round(10**x)) for x in self.short_record]

        
        #ne_mean
        self.ne_n1_mean = self.n1/(1- self.n2/(self.n1 + self.n2)*(self.p_hat**2 - (1-self.p_hat**2/(self.n1-3))))
        self.ne_n1_mean_int = int(round(self.ne_n1_mean))

        idx_lu = self.long_years.index(self.concurrent_years[0])
        if idx_lu - self.ne_n1_mean_int < 0:
            #mean extension record (years to add)
            self.extension_record_mean = self.additional_record[:idx_lu]
            self.extension_years_mean = self.additional_years[:idx_lu]
        else:
            self.extension_record_mean = self.additional_record[idx_lu - self.ne_n1_mean_int:idx_lu]
            self.extension_years_mean = self.additional_years[idx_lu - self.ne_n1_mean_int:idx_lu]

        #mean extension record
        self.xe_bar_mean = np.mean(self.extension_record_mean)
        self.s_sq_xe_mean = self.comp_variance(self.extension_record_mean)       
        self.a_mean = ((self.n1+self.ne_n1_mean_int)*self.mu_hat_y-self.n1*self.ybar1)/self.ne_n1_mean_int
        
        #mean slope calculation
        self._b_sq1_mean = (self.n1 + self.ne_n1_mean_int-1)*self.sigma_hat_y_sq 
        self._b_sq2_mean = (self.n1-1)*self.s_sq_y1
        self._b_sq3_mean = self.n1*(self.ybar1-self.mu_hat_y)**2
        self._b_sq4_mean = self.ne_n1_mean_int*(self.a_mean-self.mu_hat_y)**2
        self._b_sq5_mean = (self.ne_n1_mean_int-1)*self.s_sq_xe_mean
        self.b_sq_mean = (self._b_sq1_mean - self._b_sq2_mean - self._b_sq3_mean - self._b_sq4_mean)/self._b_sq5_mean
        self.b_mean = np.sqrt(self.b_sq_mean)

        self.extension_short_record_mean = [int(round(10**(self.a_mean+self.b_mean*(xi-self.xe_bar_mean)))) for xi in self.extension_record_mean] 
        self.mean_extension_equation = fr"y = 10^{chr(123)}{np.round(self.a_mean,4)} + {np.round(self.b_mean,4)}(x_i-{chr(92)}overline{chr(123)}{np.round(self.xe_bar_mean,3)}{chr(125)}){chr(125)}"
        
        
        self.extended_short_record_mean = self.extension_short_record_mean + self.short_record_flows
        self.extended_short_years_mean = self.extension_years_mean + self.short_years



        #ne_var
        self.ne_n1_var = 2/ ( (2/(self.n1-1)) + (self.n2/(((self.n1+self.n2-1)**2) * (self.n1-3))) * (self.A*self.p_hat**4 +self.B*self.p_hat**2 + self.C )) + 1 - self.n1 
        
        self.ne_n1_var_int = int(round(self.ne_n1_var))
        
        if idx_lu - self.ne_n1_var_int < 0:
            #mean extension record (years to add)
            self.extension_record_mean = self.additional_record[:idx_lu]
            self.extension_years_mean = self.additional_years[:idx_lu]
        else:
            self.extension_record_mean = self.additional_record[idx_lu - self.ne_n1_var_int:idx_lu]
            self.extension_years_mean = self.additional_years[idx_lu - self.ne_n1_var_int:idx_lu]
        
        self.xe_bar_var = np.mean(self.extension_record_var)
        self.s_sq_xe_var = self.comp_variance(self.extension_record_var)
        
        self.a_var = ((self.n1+self.ne_n1_var_int)*self.mu_hat_y-self.n1*self.ybar1)/self.ne_n1_var_int
        
        self._b_sq1_var = (self.n1 + self.ne_n1_var_int-1)*self.sigma_hat_y_sq 
        self._b_sq2_var = (self.n1-1)*self.s_sq_y1
        self._b_sq3_var = self.n1*(self.ybar1-self.mu_hat_y)**2
        self._b_sq4_var = self.ne_n1_var_int*(self.a_var-self.mu_hat_y)**2
        self._b_sq5_var = (self.ne_n1_var_int-1)*self.s_sq_xe_var
        
        self.b_sq_var = (self._b_sq1_var - self._b_sq2_var - self._b_sq3_var - self._b_sq4_var)/self._b_sq5_var
        self.b_var = np.sqrt(self.b_sq_var)
        
        self.extension_short_record_var = [int(round(10**(self.a_var+self.b_var*(xi-self.xe_bar_var)))) for xi in self.extension_record_var] 
        self.extended_short_record_var = self.extension_short_record_var + self.short_record_flows 
        self.extended_short_years_var = self.extension_years_var + self.short_years
        self.var_extension_equation = fr"y = 10^{chr(123)}{np.round(self.a_var,4)} + {np.round(self.b_var,4)}(x_i-{chr(92)}overline{chr(123)}{np.round(self.xe_bar_var,3)}{chr(125)}){chr(125)}"
        