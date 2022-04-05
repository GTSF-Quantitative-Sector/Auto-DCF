'''
!pip install numpy
!pip install pandas
!pip install pandas_datareader
'''
import math
import multiprocessing as mp
from flask import Flask, request
import numpy as np
import pandas as pd
import json

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/api/v1/auto_dcf', methods=['POST', 'GET'])
def auto_dcf():
    """
    Endpoint for performing the Monte-Carlo Automated Discounted Cash Flow.
    Requires a json payload with all the variables included.
    :return: json dump of DCF performed.
    """
    iterations = 10000
    years = ['2020A', '2021B', '2022P', '2023P', '2024P', '2025P']
    sales_growth = 0.1
    depr_percent = 0.032
    capex_percent = depr_percent
    ebitda_margin = 0.14
    tax_rate = 0.25
    nwc_percent = 0.24
    cost_of_capital = 0.12

    # Create probability distributions
    sales_growth_dist = np.random.normal(loc=sales_growth, scale=0.01, size=iterations)
    ebitda_margin_dist = np.random.normal(loc=ebitda_margin, scale=0.02, size=iterations)
    nwc_percent_dist = np.random.normal(loc=nwc_percent, scale=0.01, size=iterations)

    sales = pd.Series(index=years)
    sales['2020A'] = 31.0

    results = run_mcs(0, iterations, sales, sales_growth_dist, ebitda_margin_dist, nwc_percent_dist, depr_percent,
                      capex_percent, tax_rate, cost_of_capital)

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
    return json.dumps(results)


def run_mcs(start, end, sales, sales_growth_dist, ebitda_margin_dist, nwc_percent_dist, depr_percent, capex_percent,
            tax_rate, cost_of_capital):
    """
    Runs a Monte-Carlo Simulation using the given parameters for DCF.
    :param start: starting index of series
    :param end: ending index of series
    :param sales: pandas dataframe with years as index
    :param sales_growth_dist: probability distribution for sales growth
    :param ebitda_margin_dist: probability distribution for ebitda margin
    :param nwc_percent_dist: probability distribution for net-weighted_capital percent
    :param depr_percent: float
    :param capex_percent: float
    :param tax_rate: float
    :param cost_of_capital: float
    :return: list of each iteration valuation
    """
    output_distribution = []
    for i in range(start, end):
        for year in range(1, len(year)):
            sales[year] = sales[year - 1] * (1 + sales_growth_dist[0])
        ebitda = sales * ebitda_margin_dist[i]
        depreciation = (sales * depr_percent)
        ebit = ebitda - depreciation
        nwc = sales * nwc_percent_dist[i]
        change_in_nwc = nwc.shift(1) - nwc
        capex = -(sales * capex_percent)
        tax_payment = -ebit * tax_rate
        tax_payment = tax_payment.apply(lambda x: min(x, 0))
        free_cash_flow = ebit + depreciation + tax_payment + capex + change_in_nwc

        # DCF valuation
        terminal_value = (free_cash_flow[-1] * 1.02) / (cost_of_capital - 0.02)
        free_cash_flow[-1] += terminal_value
        discount_factors = [(1 / (1 + cost_of_capital)) ** i for i in range(1, len(year))]
        dcf_value = sum(free_cash_flow[1:] * discount_factors)
        output_distribution.append(dcf_value)
    return output_distribution


if __name__ == '__main__':
    app.run()
