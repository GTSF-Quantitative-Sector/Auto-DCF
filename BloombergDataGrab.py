#Jonathan Huang, Financial Analyst Quant Sector Spring 2022
#This is the back end for grabbing the data and inputting it into the DCF


import blpapi
import sys
import pdblp

def dataGrab(security, date):
    testCon = pdblp.BCon(debug=False, port=8194, timeout=5000)

    testCon.start()
    #This section will grab all the values needed from Bloomberg in order to make the DCF and is labeled the same way taught in mentorship
    print(security)
    print(date)

    WACC = testCon.bdh(security, 'VM011', date, date) #WACC
    Revenue = testCon.bdh(security, 'IS010', str((int(date)-30000)), date) #Revenue
    COGS = testCon.bdh(security, 'IS021', str((int(date)-30000)), date) #COGS
    GP = testCon.bdh(security, 'RR861', str((int(date)-30000)), date) #Gross Profit
    EBITDA = testCon.bdh(security, 'RR009', str((int(date)-30000)), date) #EBITDA
    DandA = testCon.bdh(security, 'A0122', str((int(date)-30000)), date) #Depreciation and Amortization
    ETR = testCon.bdh(security, 'RR037', date, date) #Effective Tax Rate
    ITX = testCon.bdh(security, 'IS038', str((int(date)-30000)), date) #Income Tax Expense
    EBIT = testCon.bdh(security, 'RR002', str((int(date)-30000)), date) #EBIT
    AR = testCon.bdh(security, 'BS296', str((int(date)-30000)), date) #Accounts Receivable
    Inv = testCon.bdh(security, 'BS013', str((int(date)-30000)), date) #Inventory
    AP = testCon.bdh(security, 'BS036', str((int(date)-30000)), date) #Accounts Payable
    NWC = testCon.bdh(security, 'F0918', str((int(date)-30000)), date) #Net Working Capital
    CapEx = testCon.bdh(security, 'RR014', str((int(date)-30000)), date) #Capex
    
    #These are different fields that are also needed to calculate the DCF
    NumShares = testCon.bdh(security, 'DS124', date, date) #Shares Outstandint
    Cash = testCon.bdh(security, 'BS010', date, date) #Cash and Cash Equivalents
    ExitMultiple = testCon.bdh(security, 'RR957', date, date) #EV/EBITDA
    
    return WACC, Revenue, COGS, GP, EBITDA, DandA, ETR, ITX, EBIT, AR, Inv, AP, NWC, CapEx, NumShares, Cash, ExitMultiple
    
    
    

#security = input("Enter the Security (Ticker i.e. Tesla = TSLA US Equity): ") #The security you want to get
#date = input("Enter the date (YYYYMMDD): ") #The date you want to value the security at

#print(dataGrab("TSLA US Equity", "20220412"))
