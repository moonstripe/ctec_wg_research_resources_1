SELECT
    date_trunc('month', to_timestamp(date)) as trunc_date,
    min(neutral) as min_neutral,
    percentile_cont(0.25) within group(order by neutral) as first_quartile,
    percentile_cont(0.5) within group(order by neutral) as median,
    percentile_cont(0.75) within group(order by neutral)  as third_quartile,
    max(neutral) as max_neutral,
    count(id) as number
FROM
    all_pmcworld
WHERE
    argmax = 0
GROUP BY trunc_date
ORDER BY trunc_date