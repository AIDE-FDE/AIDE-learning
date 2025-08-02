SELECT monthly
FROM analytics.sales_values_by_category
group by monthly
order by monthly desc 