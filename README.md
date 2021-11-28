# olympic_data_wiki_scraper

This is the Python code for scraping Olympic swimming results data from Wikipedia. The scraper extracts the Olympic swimming events results between `start_year` and `end_year` inclusive. The relevant events for scraping is defined by the `swim_events` list. The data is output in individual `.csv` files by Olympic year and gender.

The parameters scraped are:
- Olympic year
- Gender (Men, Women)
- Swim events (freestyle, backstroke, breaststroke, butterfly, individual medley, freestyle relay, medley relay, marathon)
- Distance (50m, 100m, 200m, 400m, 1500m, 4 x 100m, 4 x 200m)
- Stage (heat, semi-finals, finals)
- Rank (placement in respective stage)
- Name (athelete name)
- Split time (only for relay events, otherwise 0:00)
- Total time (total elapse time during event)
- Nation
- Notes (see below)


The notes for records are:
- AF - African record
- AM - Americas record (NA and SA)
- AS - Asian record
- EU - European record
- NR - National record
- OC - Oceanian record
- OR - Olympic record
- SA - South American record
- WR - world record


The notes for participations are:
- DNS - Dis not finish
- DSQ - Disqualified
- Q - Qualified
- QSO - Qualified for a swimoff
- WD - Withdrew
