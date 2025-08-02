{% macro classify_bills(column_name) %}
    CASE
        WHEN {{ column_name }} < 100 THEN 'D'
        WHEN {{ column_name }} >= 100 AND {{ column_name }} < 200 THEN 'C'
        WHEN {{ column_name }} >= 200 AND {{ column_name }} < 300 THEN 'B'
        ELSE 'A'
    END
{% endmacro %}
