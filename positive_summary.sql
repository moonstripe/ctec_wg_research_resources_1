SELECT
    date_trunc('week', to_timestamp(date)) as trunc_date,
    min(negative) as min_negative,
    percentile_cont(0.25) within group(order by negative) as first_quartile,
    percentile_cont(0.5) within group(order by negative) as median,
    percentile_cont(0.75) within group(order by negative)  as third_quartile,
    max(negative) as max_negative,
    count(id) as number
FROM
    all_pmcworld
WHERE
    argmax = 2
GROUP BY trunc_date
ORDER BY trunc_date
