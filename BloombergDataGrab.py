#Jonathan Huang, Financial Analyst Quant Sector Spring 2022
#This is the back end for grabbing the data and inputting it into the DCF


import blpapi
import sys
import pdblp

def dataGrab(security, date):
    testCon = pdblp.BCon(debug=False, port=8194, timeout=5000)

    testCon.start()
    #This section will grab all the values needed from Bloomberg in order to make the DCF and is labeled the same way taught in mentorship
    WACC = testCon.bdh(security, 'VM011', str(int(date)-10000), date).iloc[-1, 0] #WACC
    Revenue = testCon.bdh(security, 'IS010', str(int(date)-10000), date).iloc[-1, 0] #Revenue in millions
    COGS = testCon.bdh(security, 'IS021', str(int(date)-10000), date).iloc[-1, 0] #COGS in millions
    GP = testCon.bdh(security, 'RR861', str(int(date)-10000), date).iloc[-1, 0] #Gross Profit in millions
    EBITDA = testCon.bdh(security, 'RR009', str(int(date)-10000), date).iloc[-1, 0] #EBITDA in millions
    DandA = testCon.bdh(security, 'A0122', str(int(date)-10000), date).iloc[-1, 0] #Depreciation and Amortization in millions
    ETR = testCon.bdh(security, 'RR037', str(int(date)-10000), date).iloc[-1, 0] #Effective Tax Rate in percent
    ITX = testCon.bdh(security, 'IS038', str(int(date)-10000), date).iloc[-1, 0] #Income Tax Expense in millions
    EBIT = testCon.bdh(security, 'RR002', str(int(date)-10000), date).iloc[-1, 0] #EBIT in millions
    #AR = testCon.bdh(security, 'BS296', str(int(date)-10000), date) #Accounts Receivable 
    Inv = testCon.bdh(security, 'BS013', str(int(date)-10000), date).iloc[-1, 0] #Inventory in millions
    AP = testCon.bdh(security, 'BS036', str(int(date)-10000), date).iloc[-1, 0] #Accounts Payable in millioins
    NWC = testCon.bdh(security, 'F0918', str(int(date)-10000), date).iloc[-1, 0] #Net Working Capital in millions
    CapEx = testCon.bdh(security, 'RR014', str(int(date)-10000), date).iloc[-1, 0] #CapEx in millions
    TotalDepreciation = testCon.bdh(security, 'BS031', str(int(date)-10000), date).iloc[-1, 0]
    SalesGrowth = testCon.bdh(security, 'RR003', str(int(date)-10000), date).iloc[-1, 0]
    
    #These are different fields that are also needed to calculate the DCF
    NumShares = testCon.bdh(security, 'DS124', str(int(date)-10000), date).iloc[-1, 0] #Shares Outstanding 
    Cash = testCon.bdh(security, 'BS010', str(int(date)-10000), date).iloc[-1, 0] #Cash and Cash Equivalents
    ExitMultiple = testCon.bdh(security, 'RR957', str(int(date)-10000), date).iloc[-1, 0] #EV/EBITDA
    MarketCap = testCon.bdh(security, 'RR902', str(int(date) - 10000), date).iloc[-1, 0] #Market Cap
    
    return WACC, Revenue, COGS, GP, EBITDA, DandA, ETR, ITX, EBIT, Inv, AP, NWC, CapEx, NumShares, Cash, ExitMultiple, MarketCap, TotalDepreciation, SalesGrowth
    
    
    

#security = input('Enter the Security (Ticker i.e. Tesla = TSLA US Equity): ') #The security you want to get
#date = input('Enter the date (YYYYMMDD): ') #The date you want to value the security at

if __name__ == '__main__':
    print(dataGrab('AAPL US Equity', '20220412'))
