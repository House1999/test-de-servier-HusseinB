-- Hypothèse format de date mal formatté comme dans l'échantillon DD/MM/YY => DD/MM/YYYY
SELECT
    DATE AS DATE,
    -- format date?
    SUM(prod_price * prod_qty) AS ventes
FROM
    `test_sevrier.TRANSACTIONS`
WHERE
    DATE BETWEEN "2019-01-01"
    AND "2019-12-31" -- check format of date
GROUP BY
    DATE
ORDER BY
    DATE ASC
