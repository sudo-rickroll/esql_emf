-- Find customers who spent more in total in 2020 than they did in 2019.

WITH sales_2019 AS (
    SELECT cust, sum(quant) as total_19
    FROM sales
    WHERE year = 2019
    GROUP BY cust
), sales_2020 AS (
    SELECT cust, sum(quant) as total_20
    FROM sales
    WHERE year = 2020
    GROUP BY cust
)
SELECT sales_2019.cust, total_19, total_20
FROM sales_2019
JOIN sales_2020 ON sales_2019.cust = sales_2020.cust
WHERE total_20 > total_19;