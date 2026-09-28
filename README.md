# cs418-Fitness-Analytics

Personal Exercise and Fitness Analytics group repository.



GROUP MEMBERS: Hashim, Shriya, Yumna, G, Guillermo



First Question:
**How do daily steps, active minutes, and sleep relate to each other? Are the patterns different on weekends compared to weekdays?**



Second Question:

**How does measured physical activity vary by age, sex, and BMI?**



Third Question:

**Does self-reported activity match data collected from wearable fitness trackers/devices?**



Fourth Question:

**How do income and education relate to daily physical activity and sedentary time?** 




Primary Datasets:
Fitbit Fitness Tracker Data: https://www.kaggle.com/datasets/arashnic/fitbit

Physical Activity Monitor - Day: https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Examination\&Cycle=2011-2012 (PAXDAY\_G)



Secondary Datasets:

Demographic Variables \& Sample Weights: https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Demographics\&Cycle=2011-2012 (DEMO\_G)

2011 BRFSS Data (SAS Transport Format): https://www.cdc.gov/brfss/annual\_data/annual\_2011.htm



Fitbit Fitness Tracker Data - Download 4.12.16-5.12.16 dailyActivity\_merged.csv(https://www.kaggle.com/datasets/arashnic/fitbit)

Shape - 940 rows and 15 columns

One row represents one recorded day of a single participant for up to a month (4.12.16 - 5.12.16)

The columns that we care about from this data are:

Id - int64

ActivityDate - String

TotalSteps - Int64

TotalDistance - Int64

VeryActiveMinutes - Int64

FairlyActiveMinutes - Int64

LightlyActiveMinutes - Int64

SedentaryMinutes - Int64

Calories - Int64



Physical Activity Monitor - Day Data - Download PAXDAY\_G Data \[XPT - 6.2 MB] (https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Examination\&Cycle=2011-2012)

Shape - 61168 rows and 15 columns

One row represents one day of a single participant wearing the recording device and each participant is recorded for 7 days and 2 partial days so they will each have 9 rows.
The columns that we care about from this data are:
SEQN - Float64

PAXDAYD - String

PAXDAYWD - String

PAXMTSD - Float64

PAXWWMD - Float64

PAXSWMD	- Float64

PAXNWMD - Float64

PAXVMD - Float64

PAXQFD - Float64



Demographic Variables \& Sample Weight Data - Download DEMO\_G \[XPT - 3.6 MB] (https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Demographics\&Cycle=2011-2012)

Shape - 9756 rows and 48 Columns

One row represents one participant of the survey

The columns that we care about are:

SEQN - Float64

RIAGENDR - Float64

RIDAGEYR - Float64

RIDRETH1 - Float64

INDFPMIR - Float64

DMDEDUC2 - Float64

WTMEC2YR - Float64

WTINT2YR - Float64



2011 BRFSS Data (SAS Transport Format)

Shape - 506467 rows and 454 columns (we will only use 7 columns)

One row represents one participant of the survey. For this survey, the adults were all over the age of 18.

The columns that we care about are:

\_STATE - Float64

SEX - Float64

\_AGEG5YR - Float64

\_BMI5 - Float64

\_TOTINDA - Float64

EXERANY2 - Float64

\_LLCPWT - Float64



The full data for the 2011 BRFSS file is over 1GB unzipped, so it will not be in the REPO. It can be downloaded from the following link: https://www.cdc.gov/brfss/annual\_data/annual\_2011.htm

Unzip it into data/cdc/ and run the notebook. In the REPO, we include a 1000 row sample found in samples/brfss\_2011\_sample.csv

