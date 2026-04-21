SELECT
    date,
    inflow,
    outflow,
    balance,
    transaction_count,
    liquidity_ratio,
    inflow - outflow AS net_cash_flow
FROM staging_treasury;
