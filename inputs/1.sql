-- For each customer find all the aggregates in "NY",
-- find all the aggregates in "CT"

WITH t1 as (
    SELECT cust, sum(quant), avg(quant), max(quant), min(quant), count(quant)
    FROM sales
    WHERE state = 'NY'
    GROUP BY cust
), t2 as (
    SELECT cust, sum(quant), avg(quant), max(quant), min(quant), count(quant)
    FROM sales
    WHERE state = 'CT'
    GROUP BY cust
) select * from t1 inner join t2 on t1.cust = t2.cust;