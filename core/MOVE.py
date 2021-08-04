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
# Created:      14 February 2020
# Updated:      -
#               
#-------------------------------------------------------------------------------

import numpy as np

def comp_variance(record):
    
    n1 = len(record)
    
    ybar = np.mean(record)
    
    s_sq_y = sum([(yi-ybar)**2 for yi in record]) / (n1-1)
    
    return s_sq_y
     

def comp_extended_record(short_years, short_record, long_years, long_record):
    
    """MOVE method to extend short flow gage record using appropriate long record
    
    """
    
    long_record = np.log10(long_record)
    
    short_record = np.log10(short_record)
    
    suppress_params = False
    
    concurrent_years = list(set(short_years) & set(long_years))
    
    ind1 = [long_years.index(year) for year in concurrent_years if year in long_years]
    
    con_long_record = np.array(long_record)[ind1]
    
    ind2 = [short_years.index(year) for year in concurrent_years if year in short_years]
    
    con_short_record = np.array(short_record)[ind2]
 
      
    
    additional_years = list(set(long_years)-set(short_years))
    
    ind3 = [long_years.index(year) for year in additional_years if year in long_years]
    
    additional_record = np.array(long_record)[ind3]
    
    n1 = len(con_short_record)
    
    n2 = len(additional_record)
    
    
    
    ybar1 = np.mean(con_short_record)
    
    xbar1 = np.mean(con_long_record)
    
    xbar2 = np.mean(additional_record)
    
    s_sq_y1 = comp_variance(con_short_record)
    
    s_sq_x1 = comp_variance(con_long_record)
    
    s_sq_x2 = comp_variance(additional_record)
    
    
    alpha_sq = (n2*(n1-4)*(n1-1))/((n2-1)*(n1-3)*(n1-2))
    
    bhat_top = 0
    bhat_bottom = 0
    
    for i, xi in enumerate(con_long_record):
        bhat_top += (xi - xbar1)*(con_short_record[i]-ybar1)
        bhat_bottom += (xi-xbar1)**2
        
    beta_hat = bhat_top/bhat_bottom 
    
    p_hat = beta_hat * (np.sqrt(s_sq_x1)/np.sqrt(s_sq_y1))
    
    mu_hat_y = ybar1 + n2/(n1+n2)*beta_hat*(xbar2-xbar1)
    
    sigma_hat_y_sq = (1/(n1+n2-1))*((n1-1)*s_sq_y1 + (n2-1)*beta_hat**2*s_sq_x2 + (n2-1)*alpha_sq*(1-p_hat**2)*s_sq_y1+(n1*n2)/(n1+n2)*beta_hat**2*(xbar2-xbar1)**2)

    print('p_hat = '+str(p_hat))
    print('mu_hat_y = '+str(mu_hat_y))
    print('sigma_hat_y_sq = '+str(sigma_hat_y_sq))
    
   
    A1 = (n2+2)*(n1-6)*(n1-8)/(n1-5)
    A2 = n1-4
    A3 = (n1*n2*(n1-4)/((n1-3)*(n1-2)))
    A4 = 2*n2*(n1-4)/(n1-3)
    
    A = A1 + A2*(A3-A4-4)
    
    B1 = 6*(n2+2)*(n1-6)/(n1-5)
    B2 = 2*(n1**2-n1-14)
    B3 = n1-4
    B4 = 2*n2*(n1-5)/(n1-3)
    B5 = 2*(n1+3)
    B6 = (2*n1*n2*(n1-4))/((n1-3)*(n1-2))

    B = B1 + B2 + B3*(B4-B5-B6)   
      
    C1 = 2*(n1+1)
    C2 = 3*(n2+2)/(n1-5)
    C3 = (n1+1)*(2*n1+n2-2)*(n1-3)/(n1-1)
    C4 = n1-4
    C5 = 2*n2/(n1-3)
    C6 = 2*(n1+1)
    C7 = n1*n2*(n1-4)/((n1-3)*(n1-2))
    
    C = C1 + C2 - C3 + C4*(C5+C6+C7)
    
    ne = 2/ ( (2/(n1-1)) + (n2/(((n1+n2-1)**2) * (n1-3))) * (A*p_hat**4 +B*p_hat**2 + C )) + 1 - n1 
    
    ne_int = int(round(ne))
    
    extension_record = additional_record[-ne_int:]
    extension_years = additional_years[-ne_int:]
    
    xe_bar = np.mean(extension_record)
    s_sq_xe = comp_variance(extension_record)
    
    a = ((n1+ne_int)*mu_hat_y-n1*ybar1)/ne_int
    
    b_sq1 = (n1 + ne_int-1)*sigma_hat_y_sq 
    b_sq2 = (n1-1)*s_sq_y1
    b_sq3 = n1*(ybar1-mu_hat_y)**2
    b_sq4 = ne_int*(a-mu_hat_y)**2
    b_sq5 = (ne_int-1)*s_sq_xe
    
    b_sq = (b_sq1 - b_sq2 - b_sq3 - b_sq4)/b_sq5
    
    b = np.sqrt(b_sq)
    
    extension_short_record = [int(round(10**(a+b*(xi-xe_bar)))) for xi in extension_record] 
    
    if suppress_params == False:    
        print('a = '+str(a))
        print('b**2 = '+ str(b_sq))
        print('b = '+str(np.sqrt(b_sq)))
        print('xe_bar = '+str(xe_bar))
        print('s_sq_xe = '+str(s_sq_xe))
        print('A = '+str(A))
        print('B = ' +str(B))
        print('C = '+str(C))
        print('ne = '+str(ne))
        print('ne_int = '+str(ne_int))
        print('n1 = '+str(n1))
        print('n2 = '+str(n2))
        print('ybar1 = '+str(ybar1))
        print('xbar1 = '+str(xbar1))
        print('xbar2 = '+str(xbar2))
        print('sy1 = '+str(np.sqrt(s_sq_y1)))
        print('sx1 = '+str(np.sqrt(s_sq_x1)))
        print('sx2 = '+str(np.sqrt(s_sq_x2)))
    
    short_record_flows = [int(round(10**x)) for x in short_record]
    extended_short_record = extension_short_record + short_record_flows 
    
    extended_short_years = extension_years + short_years
    return extended_short_record, extended_short_years

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