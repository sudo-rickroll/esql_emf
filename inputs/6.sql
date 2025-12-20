-- For each product, calculate the percentage of its total sales 
-- that came from 'NY' compared to its total sales across all states.

WITH ny_sales AS (
    SELECT prod, sum(quant) as sum_1
    FROM sales
    WHERE state = 'NY'
    GROUP BY prod
), total_sales AS (
    SELECT prod, sum(quant) as sum_2
    FROM sales
    GROUP BY prod
)
SELECT 
    t2.prod, 
    COALESCE(sum_1, 0) as sum_1, 
    sum_2, 
    COALESCE(sum_1, 0) / NULLIF(sum_2, 0) as ratio
FROM total_sales t2
LEFT JOIN ny_sales t1 ON t1.prod = t2.prod;