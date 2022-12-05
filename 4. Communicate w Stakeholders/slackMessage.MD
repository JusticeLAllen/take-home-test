Hey A! Hope you had a wonderful weekend. 

Just wanted to update you on some recent developments with one of the data points for this week's EBR. 

Medium story short, while conducting QA we came across some unexpected gaps in the # of items from receipts that we can successfully tie to a brand. There are a couple of fields that can usually point us in the right direction but they seem to be missing from the most recent extract. 
For context: 
  - Of the **515 items** we saw scanned in Feb, **7** can be tied back to a brand
    * Only one of these has a **barcode** that matches
  - Jan is a little kinder thankfully, out of **6.7k items** we have **2.5k (38%)** that can be tied using the **brandCode**

As of right now I'm waiting to hear back from L on the Data Warehouse team, we've got a thread started ***here***. I'm thinking it's either from that week with the outage or the recent migration. Hopefully it'll be as simple as refreshing that extract after they push an update 🤞

We'll also be looking into setting up some proactive monitoring for that source in production - it would be wise to have some alerts in place before peak in Q4. 

I'll let you know if there are any developments today. In the meantime, feel free to ping me if you have any questions!
