# Seattle City Light Pole Attachments
This is pole attachment data from the City of Seattle, specifically Seattle City Light. It is used
to bill other entities rent for attach to SCL owned poles. Some poles are jointly owned and the
other owner(s) attachments may not be tracked.

The data is acquired through a public records request. (It costs $1.25.)

> I'd like a copy of the wireline attachments data. It is stored in wireline attachment data from City Light’s Work and Asset Management system (WAMS) and can be exported to Excel. I'd like the excel copy. I'd also like the pole joint ownership data. These two data sources are documented in the SCL pole attachments audit here: http://www.seattle.gov/Documents/Departments/CityAuditor/auditreports/SCLPoleAudit.pdf The process with this data is Exhibit 2 on page 5. I'd like the data used in the first two steps.

## Updating

Convert xlsx files to csv using:

```ssconvert <file>.xlsx <file>.csv```

Upsert them into the exist db file:

```sqlite-utils upsert --pk ATTACHMENTNUMBER --alter -d --csv attachments.db  All_Active_and_Inactive_Joint_Use_Assets_2021-05-15 2022-08-30/JU\ ATT\ Inventory\ for\ Billing\ \(as\ of\ 2022-08-08\).csv```
