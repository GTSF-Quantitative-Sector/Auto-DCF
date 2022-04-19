import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from blp import blp
from flask import Flask, request

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/api/v1/auto_dcf', methods=['POST', ])
def auto_dcf():
    """
    Endpoint for performing the Monte-Carlo Automated Discounted Cash Flow.
    Requires a json payload with all the variables included.
    :return: json dump of DCF performed.
    """

    """
    assuming payload looks like
    {
    "ticker": "TSLA",
    "ref_date": "20190101",
    "num_years": 3,
    "iterations": 1000,
    "sales_SD": 0.037,
    "ebitda_SD": 0.2,
    "nwc_SD": 0.223
    }
    """

    ticker = request.json["ticker"]
    if type(ticker) != str:
        raise AttributeError("Given input not string.")
    security = str.upper(ticker).strip()

    ref_date = request.json["ref_date"]
    try:
        ref_date = datetime.strptime(ref_date, "%Y%m%d")
    except ValueError:
        print("Date should be in the format 'YYYYMMDD'")

    num_years = request.json["num_years"]
    if num_years <= 2 or num_years >= 10:
        raise ValueError("Number of years should be between 2 and 10.")

    iterations = request.json["iterations"]
    if iterations <= 1 or iterations >= 20000:
        raise ValueError("Number of iterations should be between 1 and 20000.")

    sales_SD = request.json["sales_SD"]
    ebitda_SD = request.json["ebitda_SD"]
    nwc_SD = request.json["nwc_SD"]
    if not (0 < (sales_SD or ebitda_SD or nwc_SD) < 10):
        raise ValueError("Incorrect Standard Deviation provided.")

    data = get_ticker_data(security=security, start_date=str((ref_date - timedelta(365)).strftime("%Y%m%d")),
                           end_date=str(ref_date.strftime("%Y%m%d")))

    print(data.to_string())

    sales_growth_dist = np.random.normal(loc=data["SALES_3YR_AVG_GROWTH"], scale=sales_SD, size=iterations)
    ebitda_margin_dist = np.random.normal(loc=data["EBITDA_TO_REVENUE"], scale=ebitda_SD, size=iterations)
    nwc_percent_dist = np.random.normal(loc=(data["WORKING_CAPITAL"] / data["SALES_REV_TURN"]), scale=nwc_SD,
                                        size=iterations)

    years = []
    for i in range(0, num_years):
        years.append(str(int(ref_date.year) + i))

    sales = pd.Series(index=years, dtype=float)
    sales[str(ref_date.year)] = data["SALES_REV_TURN"]  # needs to be changed to the current years sales

    estimate, results = run_mcs(start=0, end=iterations, num_shares=data["BS_SH_OUT"], sales=sales,
                      capex_percent=(data["CAPEX_ABSOLUTE_VALUE"] / data["SALES_REV_TURN"]),
                      depr_percent=(data["CAPEX_ABSOLUTE_VALUE"] / data["SALES_REV_TURN"]), wacc=data["WACC"],
                      tax_rate=data["EFF_TAX_RATE"], sales_growth_dist=sales_growth_dist,
                      ebitda_margin_dist=ebitda_margin_dist, nwc_percent_dist=nwc_percent_dist, data = data)

    '''
    print("Number of processors: ", mp.cpu_count())
        pool = mp.Pool(mp.cpu_count())
    
        results = [pool.apply(run_mcs, args=(count * math.ceil(iterations / mp.cpu_count()),
                                             (count + 1) * math.ceil(iterations / mp.cpu_count()), sales, sales_growth_dist,
                                             ebitda_margin_dist, nwc_percent_dist,
                                             depr_percent,
                                             capex_percent,
                                             tax_rate,
                                             cost_of_capital)) for count in range(mp.cpu_count() - 1)]
    
        pool.close()
    '''
    return json.dumps([estimate, results])


def get_ticker_data(security, start_date, end_date):
    fields = ["BS_SH_OUT", "SALES_REV_TURN", "IS_COGS_TO_FE_AND_PP_AND_G", "EBITDA", "CF_DEPR_AMORT",
              "CAPEX_ABSOLUTE_VALUE", "BS_INVENTORIES", "BS_ACCTS_REC_EXCL_NOTES_REC", "BS_ACCT_PAYABLE",
              "WORKING_CAPITAL", "CURRENT_MARKET_CAP_SHARE_CLASS", "COUNTRY_RISK_RFR",
              "COUNTRY_RISK_PREMIUM", "SALES_3YR_AVG_GROWTH", "EFF_TAX_RATE", "WACC", "EBITDA_TO_REVENUE",
              "EV_EBITDA_ADJUSTED", "BETA_ADJ_OVERRIDABLE"]
    query = blp.BlpQuery().start()
    data = query.bdh(["{} US Equity".format(security)], fields, start_date=start_date, end_date=end_date).fillna(
        method="ffill").iloc[-1]
    #print(data.to_string())
    for x in ["BS_SH_OUT", "SALES_REV_TURN", "IS_COGS_TO_FE_AND_PP_AND_G", "EBITDA", "CF_DEPR_AMORT",
              "CAPEX_ABSOLUTE_VALUE", "BS_INVENTORIES", "BS_ACCTS_REC_EXCL_NOTES_REC", "BS_ACCT_PAYABLE",
              "WORKING_CAPITAL", "CURRENT_MARKET_CAP_SHARE_CLASS"]:
        data[x] *= 1000000
    for y in ["COUNTRY_RISK_RFR", "COUNTRY_RISK_PREMIUM", "SALES_3YR_AVG_GROWTH",
              "EFF_TAX_RATE", "WACC", "EBITDA_TO_REVENUE"]:
        data[y] /= 100
    return data


def run_mcs(start, end, num_shares, sales, capex_percent, depr_percent, wacc, tax_rate, sales_growth_dist,
            ebitda_margin_dist, nwc_percent_dist, data):
    """
    Runs a Monte-Carlo Simulation using the given parameters for DCF.
    :param num_shares:
    :param start: starting index of series
    :param end: ending index of series
    :param sales: pandas dataframe with years as index
    :param sales_growth_dist: probability distribution for sales growth
    :param ebitda_margin_dist: probability distribution for ebitda margin
    :param nwc_percent_dist: probability distribution for net-weighted_capital percent
    :param depr_percent: float
    :param capex_percent: float
    :param tax_rate: float
    :param wacc: float
    :return: list of each iteration valuation
    """

    output_distribution = []
    for i in range(start, end):
        for year in range(1, len(sales)):
            sales[year] = sales[year - 1] * (1 + sales_growth_dist[i])
        ebitda = sales * ebitda_margin_dist[i]
        depr = sales * depr_percent
        ebit = ebitda - depr
        nwc = sales * nwc_percent_dist[i]
        change_in_nwc = nwc.shift(1) - nwc
        capex = -(sales * capex_percent)
        tax_payment = -ebit * tax_rate
        tax_payment = tax_payment.apply(lambda x: min(x, 0))
        free_cash_flow = ebitda + tax_payment + capex + change_in_nwc
        # print(free_cash_flow)
        # DCF valuation
        terminal_value = (free_cash_flow[-1] * (1 + sales_growth_dist[i])) / (wacc - sales_growth_dist[i])
        free_cash_flow[-1] += terminal_value
        discount_factors = [1 / (1 + wacc ** i) for i in range(1, len(sales))]
        dcf_value = free_cash_flow[1:] * discount_factors
        # print(dcf_value)
        output_distribution.append((sum(dcf_value)/num_shares) * data["EV_EBITDA_ADJUSTED"])
    estimate_value = sum(output_distribution)/len(output_distribution)
    return estimate_value, output_distribution


if __name__ == '__main__':
    app.run()
