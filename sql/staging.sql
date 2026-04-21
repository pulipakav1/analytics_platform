SELECT
    DATE(date) AS date,
    CAST(inflow AS REAL) AS inflow,
    CAST(outflow AS REAL) AS outflow,
    CAST(balance AS REAL) AS balance,
    CAST(transaction_count AS INTEGER) AS transaction_count,
    CAST(liquidity_ratio AS REAL) AS liquidity_ratio
FROM raw_treasury;
