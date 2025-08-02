select
    *
    , {{ classify_bills ('total_bills')}} as class
from {{ ref ("sales_values_by_category")}}