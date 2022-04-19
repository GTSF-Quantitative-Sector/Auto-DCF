from blp import blp


def getData(security, fields, start_date, end_date):
    bquery = blp.BlpQuery().start()
    return bquery.bdh(["{} US Equity".format(security)], fields, start_date=start_date, end_date=end_date)


if __name__ == '__main__':
    # print(getData(security="AAPL", fields=["WACC", "CF_FREE_CASH_FLOW", "PX_LAST"], start_date="20201223",
    #               end_date="20210330"))
    # print(getData(security="AAPL", fields=["WACC", "CF_FREE_CASH_FLOW", "PX_LAST"], start_date="20201223",
    #               end_date="20210330"))

    fields = ["BS_SH_OUT", "SALES_REV_TURN", "IS_COGS_TO_FE_AND_PP_AND_G", "EBITDA", "CF_DEPR_AMORT",
              "CF_CAP_EXPEND_PRPTY_ADD", "BS_INVENTORIES", "BS_ACCTS_REC_EXCL_NOTES_REC", "BS_ACCT_PAYABLE",
              "CURRENT_MARKET_CAP_SHARE_CLASS", "BEST_EV", "COUNTRY_RISK_RFR", "COUNTRY_RISK_PREMIUM",
              "SALES_3YR_AVG_GROWTH", "EFF_TAX_RATE", "EBITDA_TO_REVENUE", "EV_EBITDA_ADJUSTED", "BETA_ADJ_OVERRIDABLE"]

    results = \
        getData(security="KO", fields=fields, start_date="20201223", end_date="20220330").fillna(method="ffill").iloc[
            -1]
    for x in ["BS_SH_OUT", "SALES_REV_TURN", "IS_COGS_TO_FE_AND_PP_AND_G", "EBITDA", "CF_DEPR_AMORT",
              "CF_CAP_EXPEND_PRPTY_ADD", "BS_INVENTORIES", "BS_ACCTS_REC_EXCL_NOTES_REC", "BS_ACCT_PAYABLE",
              "CURRENT_MARKET_CAP_SHARE_CLASS", "BEST_EV"]:
        results[x] *= 1000000
    for y in ["COUNTRY_RISK_RFR", "COUNTRY_RISK_PREMIUM", "SALES_3YR_AVG_GROWTH",
              "EFF_TAX_RATE", "EBITDA_TO_REVENUE"]:
        results[y] /= 100
    print(results.to_string())
