WITH base AS (
    SELECT 
        category,
        monthly,
        total_bills
    FROM {{ ref('sales_values_by_category') }}
),

pivoted AS (
    SELECT 
        category,
        {% set pivoted_cols = dbt_utils.pivot(
            column='monthly',
            values=[
                '2018-08', '2018-07', '2018-06', '2018-05', '2018-04',
                '2018-03', '2018-02', '2018-01', '2017-12', '2017-11',
                '2017-10', '2017-09', '2017-08', '2017-07', '2017-06',
                '2017-05', '2017-04', '2017-03', '2017-02', '2017-01',
                '2016-12', '2016-10'
            ],  
            agg='sum',
            then_value='total_bills'
        ) %}
        {{ pivoted_cols }}
    FROM base
    GROUP BY category
)

SELECT * FROM pivoted