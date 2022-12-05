WITH most_recent_month AS (
SELECT date_trunc('month', dateScanned) AS dateTruncedMonth
FROM receipt_items

-- If I don't include this filter the most recent month with data is March '21 but we won't have any brand info so it's not paricularly helpful
WHERE brandCode IN (SELECT brandCode FROM brands)
),

brand_agg AS (
SELECT
-- Not all rows in Brands have brandCode values attached, all have names
b.name
,date_trunc('month', b.name) AS dateTruncedMonth
,COUNT(DISTINCT r.receiptId) AS receiptsScanned
,SUM(r.finalPrice) AS amountSpent

FROM receipt_items r

JOIN brands b
ON b.brandCode = r.brandCode

WHERE
r.brandCode IS NOT NULL

GROUP BY 1, 2
),

most_recent_data AS (
SELECT
*
-- This will be used to determine who's in the top 5 without missing out on ties
-- For this run I'll include any spots leading up to 5 but ultimately it would be up to the stakeholder
--    (That is, whether they want a RANK or a DENSE_RANK)
,RANK() OVER (ORDER BY receiptsScanned DESC) AS receiptRank
FROM brand_agg

WHERE
dateTruncedMonth = (SELECT dateTruncedMonth FROM most_recent_month)
),

penultimate_data AS (
SELECT
*
-- This will be used to determine who's in the top 5 without missing out on ties
-- For this run I'll include any spots leading up to 5 but ultimately it would be up to the stakeholder
--    (That is, whether they want a RANK or a DENSE_RANK)
,RANK() OVER (ORDER BY receiptsScanned DESC) AS receiptRank
FROM brand_agg

WHERE
dateTruncedMonth = (SELECT dateTruncedMonth - interval '1 month' FROM most_recent_month)
),

final AS (
SELECT * FROM most_recent_data WHERE receiptRank <= 5
UNION
SELECT * FROM penultimate_data WHERE receiptRank <= 5
)

SELECT * FROM final
ORDER BY dateTruncedMonth DESC, receiptsScanned DESC, name ASC
