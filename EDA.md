**Exploratory Data Analysis**

This summarizes eda.ipynb.

**1. Dataset profile**

The data has 940 rows and 15 columns, one row per person per day. ActivityDate loaded as text, so we converted it to a date. There are no nulls, but some missing data is hiding as zeros (see section 2).

| Column | Mean | Median | Min | Max |
|---|---|---|---|---|
| TotalSteps | 7,638 | 7,412 | 0 | 36,019 |
| VeryActiveMinutes | 21.2 | 4 | 0 | 210 |
| FairlyActiveMinutes | 13.6 | 6 | 0 | 143 |
| LightlyActiveMinutes | 192.8 | 199 | 0 | 518 |
| SedentaryMinutes | 991 | 1,058 | 0 | 1,440 |
| Calories | 2,304 | 2,135 | 0 | 4,900 |

What stood out: steps and calories have a minimum of 0, which is odd for someone wearing a tracker. The max steps (36,019) is far above the 75th percentile (10,725). Also, describe() gave a wrong max date (5/9/2016) because the date was still text and got sorted alphabetically.

**2. Anomalies**

| Anomaly | Rows | What we did |
|---|---|---|
| Zero steps | 77 | Flagged, plan to drop the non-wear days |
| Zero calories | 4 | Flagged, all inside the 72 below |
| 1,440 sedentary minutes and zero steps (tracker probably not worn) | 72 | Flagged, plan to drop |
| 1,440 sedentary minutes but steps above 0 (contradictory) | 7 | Flagged, still deciding |
| Date stored as text | 940 | Fixed |
| Duplicates, negatives, nulls | 0 | Nothing to do |

The 4 zero-calorie days also have zero steps and 1,440 sedentary minutes, so we think the tracker wasn't worn or didn't record. Most of the 72 non-wear days still show a calorie number (like 1,347), so sedentary minutes is a better way to spot them than calories. Of the 7 contradictory days, 5 belong to one participant. We haven't removed any rows yet, but we plan to drop the 72 non-wear days because they pull averages down.

**3. Distributions**

These use all 940 rows. Daily steps are mostly between 2,500 and 15,000 with a mild right skew and a long tail to 36,000, plus a spike near 0 from the zero-step days. Very active and fairly active minutes are heavily right-skewed (medians of 4 and 6 minutes). Lightly active minutes are roughly symmetric around 200. Sedentary minutes have two humps (around 700 to 750 and 1,100 to 1,200) plus a spike at 1,440. Total active minutes (light + fairly + very) form a wide hump around 250 to 350 with a spike at 0. Almost every plot has a spike at 0, probably from the same non-wear days.

**4. Relationships**

Steps vs. total active minutes: active minutes rise with steps, but flatten out above roughly 8,000 to 10,000 steps, and the points spread out a lot. This was expected at low step counts but not the flattening, so one correlation number won't describe it well. Next we want to try very active minutes alone and check whether the flattening happens within a person or only between people.

Weekday vs. weekend steps per participant: across 32 participants the averages were almost the same (7,650 on weekdays, 7,607 on weekends), and 15 of 32 walked more on weekends. People who walk a lot on weekdays also walk a lot on weekends, but individual differences were big (about -7,435 to +5,146 steps). So the person matters more than the day. Next we want to split Saturday and Sunday and look at the people far from the diagonal. These averages still include the zero days, so they will likely change once those are removed.

**5. Revised research questions**

Question 1: how are daily steps and active minutes related, and why does it flatten at high step counts?

Question 2: do people walk differently on weekdays and weekends, or does it depend more on the person?

Question 3: how does NHANES measure movement, and can we compare it to the Fitbit data? Unchanged until we profile NHANES.

We changed the first two because the steps plot isn't a straight line and the weekday and weekend averages were almost identical.

**NHANES Exploratory Data Analysis**

1. Dataset Profile

The NHANES 2011–2012 Physical Activity Monitor Day dataset contains 61,168 rows and 15 columns. Each row represents one participant's monitoring data for a particular day. The dataset includes monitoring day (PAXDAYD), weekday (PAXDAYWD), valid monitoring minutes (PAXVMD), movement measurements (PAXMTSD), and valid wake wear minutes (PAXWWMD).

Initial profiling showed no null values. However, further investigation identified suspicious extremely small numeric values that required vleaning.

2. Anomalies

Several numeric columns contained values of approximately 5.39e-79, which are extremely close to zero. These suspicious values appeared in 60,267 of the 61,168 records. Since zero is a valid value for these measurements, we treated the near-zero values as likely artifacts associated with reading the SAS dataset. We created a cleaned copy of the dataset and replaced positive numeric values smaller than 1e-70 with zero.

After cleaning, no suspicious near-zero values remained. All 61,168 rows and 15 columns were retained. This approach assumes that these values represent zeros rather than meaningful measurements.

3. Distributions

We examined the distribution of daily valid monitoring minutes (PAXVMD)

The histogram showed that most records contain approximately 1,440 valid monitoring minutes, equivalent to nearly 24 hours. However, some records contain considerably fewer valid minutes, producing a tail toward lower values. This pattern is consistent with the NHANES monitoring protocol, where the first and last monitoring days are partial days.

These differences matter because shorter monitoring periods provide less opportunity to record movement.

4. Relationships

We compared average valid monitoring minutes across the nine monitoring days. Days 2-8 consistently averaged approximately 1,431-1,436 valid minutes. In contrast, day 1 averaged approximately 501 minutes, and day 9 averaged approximately 944 minutes.

This confirms that monitoring duration varies considerably across days, particularly at the beginning and end of data collection.

The result was expected based on the NHANES monitoring protocol.

What next? Focus subsequent analyses on days 2-8 to reduce the influence of partial monitoring days.

We also compared movement measurements using PAXMTSD, which represents the daily sum of MIMS triaxial movement values. To account for differences in valid monitoring duration, we divided PAXMTSD by PAXVMD.

Weekdays averaged approximately 9.58 MIMS per valid minute, while weekends averaged approximately 8.83. This represents approximately 8.5% higher average movement per valid minute on weekdays.

The result was noteworthy because the difference remained after adjusting for valid monitoring duration. However, these descriptive averages do not establish statistical significance.

What next? Investigate whether the weekday-weekend difference remains consistent across individual participants.

5. Revised Research Questions

How does monitoring duration vary across the nine monitoring days, and how does this influence comparisons of daily movement?

Do participants have different wake wear times on weekdays compared with weekends?

Is average movement per valid monitoring minute higher on weekdays than weekends, and does this pattern remain consistent across individuals?

Can NHANES MIMS movement measurements and Fitbit step counts reveal similar weekday-weekend movement patterns, despite measuring activity differently?