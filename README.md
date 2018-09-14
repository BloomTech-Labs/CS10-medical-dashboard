# AIMLDS1/CS10-Medical Data Dashboard & Prescription Insurance Claim Analysis
A [Lambda School](https://lambdaschool.com/) AIMLDS1 Capstone Project

## Members:
- [Joanne Jordan](https://github.com/jojordan3) 
- [Qiping Sun](https://github.com/shellysun)
- [Troy Bradley](https://github.com/bitcointroy)
- [Clayton Swafford](https://github.com/waterFlowin)
- [Mariano Scandizzo](https://github.com/mscandizzo) 


# Medical Claims Data Analysis and Price Comparisons

## Data

The data for this project consists of gigabytes de-identified medical claims data from a single health plan. It represents 6 months of medical claims data from ~ 100,000 individuals.

Data for this project has been provided by a helpful third party with the following stipulations:

The raw data is not to be published in whole or in part anywhere on the internet that could be accessed by a third-party.

Team members will not retain access to the data after the project has ended and will destroy any local copies of the dataset after the capstone period is over.

I (Ryan A.) will need to collect the email addresses of the team members in order to distribute a compressed version of the files to you.

## MVP Objectives:

Identify the cheapest pharmacy in each zip code for a given drug

Identify the cheapest PBM for a given drug

Identify the cheapest PBM Overall

Display your findings in a visually compelling dashboard that will allow non-technical stakeholders to interpret the analysis.

### Initial Ideas for dashboard application by Qiping
Deploying a Flask application on AWS - using Amazon's Elastic Beanstalk and RDS
AWS — Amazon Web Services. A collection of services for hosting and running websites provided by the company Amazon. We will use their EC2 service and Elastic Beanstalk service.
RDS - is a web service that makes it easier to set up, operate, and scale a relational database in the cloud. It provides cost-efficient, resizable capacity for an industry-standard relational database and manages common database administration tasks.
Elastic Beanstalk — A service offered by Amazon which simplifies deploying your code from your local computer to your EC2 instance on AWS.
Ideally, we will launch Flask application to AWS Elastic Beanstalk. It also uses AWS RDS for a database backend.

## Challenges

The data is vast and finding visualization solutions that allow for easily digestible browsing of the data will take some creativity.

The data will be hosted in a SQL database to be interacted with via SQL queries.

The data is in the form of 15 different pipe-delimited CSV files all of different sizes which will need to be managed appropriately.

Specific drug information is not listed in the dataset, rather the NDC (National Drug Code) is given. These will need to be matched with the appropriate drug information.

Drug prices should be compared on a price-per-pill basis, however, this feature is not found in the dataset.

## The Deliverable

A web-accessible report/dashboard that makes plain the 3 MVP objectives.

CSV files can be uploaded to something like MySQL Workbench for easier sharing and querying. 

Dashboarding tools like Plotly Dash could be a good python-based graphing solution. 

All code for data cleaning and analysis should be available in a REPRODUCIBLE Github Repository.

## The Business Case:

Analysis of this kind is big business, and is applicable to 10 or so different sub-industries in the healthcare industry.

### Pharmacy Benefit Management (PBM)

Optum - Optum is owned by UnitedHealth Group a company with a market capitalization of ~ $260B.

### Medical Analytics/Dashboarding Companies 

Truven Health Analytics - Acquired by IBM Watson Health in 2016 for $2.6B

Artemis Healthcare Analytics - Currently valued at $150M

Health Catalyst -  Healthcare Analytics for Hospitals 

### Benefits/Actuarial Consulting:

Milliman 

### Any Large Insurance Provider - [Article](https://healthitanalytics.com/news/93-of-payers-providers-say-predictive-analytics-is-the-future)

### Population Health Management Companies

Lumere

Zeomaga

Athena Health

#### Healthcare makes up 18% of the US economy. There is a lot of opportunity for cost savings.This kind of analysis and reporting is a key component to addressing runaway medical costs.


**References:**

[Markdown Cheat Sheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
