# Data Model
This first folder holds the data model for the given tables. Two quick things to note here!

1. Any column with another name in parantheses is going to be aliased after the data is uploaded. `_id` will become `brandId` in the **Brands** table, for example. This is just my personal preference! (I prefer to work with explicit keys)
2. The **Receipts** table is actually going to be a "flattened" view of the receipt json, where each row will be an *item* on the receipt. In **Snowflake** this would be accomplished with `lateral_flatten`.
    - This isn't technically necessary but I prefer this method to working with array columns over and over.
