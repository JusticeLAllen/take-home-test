WITH most_recent_month AS (
-- This strftime manuever is necessary because sqlite doesn't have date_trunc as a function
SELECT strftime('%Y%m', MAX(dateScanned)) as yearMonth,
strftime('%Y-%m', MAX(dateScanned)) || '-01' AS dateTruncedMonth FROM receipt_items

-- If I don't include this filter the most recent month with data is March '21 but we won't have any brand info so it's not paricularly helpful
WHERE brandCode IN (SELECT brandCode FROM brands)
),

brand_agg AS (
SELECT
-- Not all rows in Brands have brandCode values attached, all have names
b.name
,strftime('%Y%m', r.dateScanned) AS yearMonth
,COUNT(DISTINCT r.receiptId) AS receiptsScanned
,SUM(r.finalPrice) AS amountSpent

FROM receipt_items r

JOIN brands b ON b.brandCode = r.brandCode

WHERE
-- This quote() function is here to fix data type issues introduced by sqlite's unicode handling
r.brandCode != QUOTE('NULL')

GROUP BY 1, 2
),

most_recent_data AS (
SELECT
*
FROM brand_agg

WHERE
yearMonth = (SELECT yearMonth FROM most_recent_month)
),

-- A shorter name might be better but I really like this word
penultimate_data AS (
SELECT
*
FROM brand_agg

WHERE
yearMonth = (SELECT strftime('%Y%m', date(dateTruncedMonth, '-1 month')) FROM most_recent_month)
),

final AS (
SELECT * FROM most_recent_data
-- This method of finding the top 5 includes anyone who tied (in Snowflake this would be akin to using RANK rather than ROW_NUMBER)
WHERE receiptsScanned IN (SELECT DISTINCT receiptsScanned FROM most_recent_data ORDER BY receiptsScanned DESC LIMIT 5)

UNION

SELECT * FROM penultimate_data
WHERE receiptsScanned IN (SELECT DISTINCT receiptsScanned FROM penultimate_data ORDER BY receiptsScanned DESC LIMIT 5)
)

SELECT * FROM final
ORDER BY yearMonth DESC, receiptsScanned DESC, name ASC
