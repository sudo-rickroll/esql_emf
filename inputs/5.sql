-- Find customers whose personal average sale size is strictly greater than the global average sale size of all transactions in the database.

WITH cust_stats AS (
    SELECT cust, avg(quant) as my_avg
    FROM sales
    GROUP BY cust
), global_stats AS (
    SELECT avg(quant) as global_avg
    FROM sales
)
SELECT cust, my_avg, global_avg
FROM cust_stats, global_stats
WHERE my_avg > global_avg;