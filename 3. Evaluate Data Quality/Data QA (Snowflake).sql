-- Determining if we have enough data to capture an insight about the most recent month
SELECT
date_trunc('month', r.dateScanned) AS dateTruncedMonth
,COUNT(r.barcode) AS itemsScanned
,COUNT(IFF(r.brandCode IS NOT NULL, r.barcode, NULL)) AS itemsWithValidbrandCodes
,COUNT(IFF(r.brandCode IN (SELECT brandCode FROM brands), r.barcode, NULL)) AS brandCodeFound
,COUNT(IFF(r.barcode IN (SELECT barcode FROM brands), r.barcode, NULL)) AS barCodeFound

FROM receipt_items r

GROUP BY 1
ORDER BY 1
;

-- This query seemed to indicate that we have very little brand matching with the receipt items based on brandCode
--    And even less based on barcode!

-- Confirming with a deeper dive on the brandCode portion

-- Receipt items with a brandCode that's not in Brands:
SELECT DISTINCT
brandCode
FROM receipt_items
WHERE
brandCode IS NOT NULL
AND brandCode NOT IN (SELECT brandCode FROM brands)
;

-- From here I did some spot checking to confirm that these brands are in fact missing from the brands.json
--  If this were a real assignment I would follow up with the relevant Data Warehouse/Data Admin/Data Science team, whoever owns said pipeline

-- ... I would also check with my teammates/manager to make sure my query isn't somehow malfunctioning or that a table reference isn't wrong
