select 
    min(dist.negative) as minimum,
    max(dist.negative) as maximum, 
    width_bucket(dist.negative, 0, 1, 99) as buckets,
    count(*)
from (
    select distinct on (text)
        negative, date
    from all_pmcworld
    where argmax != 0 and negative > positive and negative > neutral
    order by text
) as dist
group by buckets
order by buckets;