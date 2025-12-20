--Find products where the average sale quantity in 'NY' is higher than in 'NJ'.

WITH ny_sales AS (
    SELECT prod, avg(quant) as ny_avg
    FROM sales
    WHERE state = 'NY'
    GROUP BY prod
), nj_sales AS (
    SELECT prod, avg(quant) as nj_avg
    FROM sales
    WHERE state = 'NJ'
    GROUP BY prod
)
SELECT ny_sales.prod, ny_avg, nj_avg
FROM ny_sales
JOIN nj_sales ON ny_sales.prod = nj_sales.prod
WHERE ny_avg > nj_avg;