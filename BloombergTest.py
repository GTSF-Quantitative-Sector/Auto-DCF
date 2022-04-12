import blpapi
import sys
import pdblp

testCon = pdblp.BCon(debug=False, port=8194, timeout=5000)

testCon.start()

print(testCon.bdh('TSLA US Equity', 'IS010', '20190307', '20220307'))