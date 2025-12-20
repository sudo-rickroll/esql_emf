SELECT 
    cust, 
    prod, 
    month, 
    year, 
    day, 
    SUM(quant) as sum_1_quant, 
    MAX(quant) as max_1_quant,
    SUM(quant) as sum_2_quant, 
    MAX(quant) as max_2_quant
FROM sales
GROUP BY cust, prod, month, year, day;