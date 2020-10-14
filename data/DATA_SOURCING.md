# Data crowd-sourcing guidelines

DiversityCorp relies on crowd-sourced data on companies. You are most welcome if you want to contribute, as long as you follow the guidelines described here.

## Gather data

The DiversityCorp database is structured is several tables.

You can update any or all fields from a table by providing a properly formatted .csv file. Write `null` when you don't have the information. Some fields are required: they cannot be set to `null`.

Each .csv file **must** include a header and be named `[TARGET]_[USER]_[DATE].csv` where:
- [TARGET] is the name of the target table in the database,
- [USER] is your GitHub username,
- [DATE] is the creation date of the file, in YYYYMMDD format.

**Add your CSV files to /data/new in this repo**

### Intro to CSV files.

CSV files are tabular text files, where each line is a row of the table and the columns are separated by a comma. You can create them in any basic text editor. You can also create the table in your favourite spreadsheet then export it to CSV.

[A guide to CSV format](https://www.computerhope.com/issues/ch001356.htm)

:exclamation: When a field contains commas, please [enclose it between quotes](https://stackoverflow.com/questions/4617935/is-there-a-way-to-include-commas-in-csv-columns-without-breaking-the-formatting) so it's not split by the csv reader!

### Update the table with basic company information

This is the only table that accepts information on companies that are not in the database yet. Companies that already exist in the database will have their information updated (= overwritten), expect for fields where the new data is `null`.

Expected columns are:

| full_name | usual_name | created_at | country | category | detailed_category | sector | logo_url | last_full_update |
|-|-|-|-|-|-|-|-|-|
| Official registered name | Name the company is know by.<br>Cannot be null | Year of official registration | Using international country code | Main type.<br>One of the listed business categories | Detailed administrative category | One of the listed sectors | Link to the logo image | Current date if you are updating<br>all the info for the company, else null |

You can copy this as the header:
`full_name, usual_name, created_at, country, category, detailed_category, sector, logo_url, last_full_update`

List of valid business categories: sole_proprietorship, partnership, limited_liability_company, business_corporation.

List of valid business sectors (from https://www.ilo.org/global/industries-and-sectors/lang--en/index.htm): agriculture_plantations_other_rural, basic_metal_production, chemical_industries, commerce, construction, education, financial_and_professional_services, food_drink_tobacco, forestry_wood_pulp_paper, health_services, hotels_tourism_catering, mining_coal_and_others, mechanical_and_electrical_engineering, media_culture_graphical, oil_gas_production_and_refining, postal_and_telecommunication_services, public_services, shipping_ports_fishery_inland_waterways, textiles_clothing_leather_footwear, transport, transport_equipment_manufacturing, utilities_water_gaz_electricity.

### Update the tables with human resources information and executive teams information

These tables only accept information for companies that already are in the table for basic company information.

:exclamation: The error message listing inexistent companies has not been implemented yet.

| company_name | employee_count | part_time_employee_count | diversity_policy_url | diversity_report_url | ice_contract | mean_wages | median_wages | executive_team_size | executive_team_photo | executive_team_ceo_wages |
|-|-|-|-|-|-|-|-|-|-|-|
| Must be the same as the 'usual_name' in the companies table. Cannot be null | As counted by Fortune, fulltime + half of parttime | Sometimes available in the published annual report | Link to public diversity or inclusion policy | Link to public diversity or inclusion report | Do they currently have a contract with US Immigration and Customs Enforcements? true, false or null | In dollars, yearly, after taxes | In dollars, yearly, after taxes |  | Link to photo of the team, should be stored in GitHub repo | In thousand dollars, yearly, after taxes |

You can copy this as a header:
`company_name, employee_count, part_time_employee_count, diversity_policy_url, diversity_report_url, ice_contract, mean_wages, median_wages, executive_team_size, executive_team_photo, executive_team_ceo_wages`


### Update the table with financial information

This table only accepts information for companies that already are in the table for basic company information.

:exclamation: The error message listing inexistent companies has not been implemented yet.


| data_at | company_name | revenues | profits | market_value | assets | total_stockholder_equity | revenues_increase | profits_increase | earnings_per_share | total_return_for_investors_in_year | total_annual_return_for_investors_in_ten_years |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Year of report. Cannot be null | Must be the same as the 'usual_name' in the companies table. Cannot be null | In millions of dollars | In millions of dollars | In millions of dollars | In millions of dollars | In millions of dollars | In percents | In percents | In dollars | In percents | In percents |

You can copy this as a header:
`data_at, company_name, revenues, profits, market_value, assets, total_stockholder_equity, revenues_increase, profits_increase, earnings_per_share, total_return_for_investors_in_year, total_annual_return_for_investors_in_ten_years`

:information: The Fortune 500 website is a good information source for this.

### Update the table with fortune500 rankings

This table only accepts information for companies that already are in the table for basic company information.

:exclamation: The error message listing inexistent companies has not been implemented yet.

| ranked_at | ranking | company_name | fortune_summary |
|-|-|-|-|
| Year of the ranking. Cannot be null | Rank. Cannot be null | Must be the same as the 'usual_name' in the companies table. Cannot be null | The short text accompanying the financial data on the Fortune 500 website |


You can copy this as a header:
`ranked_at, ranking, company_name, fortune_summary`

### Update the table with notable events

:exclamation: For now events can only be added, not updated.

This table only accepts information for companies that already are in the table for basic company information.

:exclamation: The error message listing inexistent companies has not been implemented yet.

| event_at | commpany_name | keywords | description | statement_text | official_url | analysis_url |
|-|-|-|-|-|-|-|
| Timestamp | Must be the same as the 'usual_name' in the companies table. Cannot be null | A list of comma-separated keywords, in between quotes, e.g. "blm, diversity policy, website banner" | Short description if appropriate | Official statement of the company | Link to official website or press release | Link to an analysis article online |

You can copy this as a header:
`event_at, commpany_name, keywords, description, statement_text, official_url, analysis_url`

## Prepare for upload

:exclamation: Work in progress

## Upload

:exclamation: Work in progress
