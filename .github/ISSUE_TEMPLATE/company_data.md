---
name: Company data
about: Request data for a specific company
title: "Add data for <company>"
labels: "data collection, help wanted, good first issue"
---

#### Description

Add a file with data for [Company Name](https://fortune.com/company/company-name-here/fortune500/)

Use `companies-on-blm/examples/add-a-company.md` as a reference for how to add data for a company. If information for a field cannot be found, please delete that line.

#### Helpful tips

Fortune Rank: Search for the company [here](https://fortune.com/fortune500/2020/search/). If they aren't ranked by Fortune, take this field out.

Twitter: Use the [advanced search](https://www.twitter.com/search-advanced) feature.
First, find the Twitter handle of the company (sometimes there are several) & CEO. Googling `twitter account <company name>` usually works.
Replace `zillow` in the following url with the name of the handle you are searching for.

https://twitter.com/search?q=(from%3Azillow)%20min_faves%3A10%20until%3A2020-06-05%20since%3A2020-05-28%20-filter%3Areplies

How this url works:

- `(from%3Azillow)%20`: from the @zillow account
- `min_faves%3A10%20`: minimum 10 likes
- `since%3A2020-05-28%20`: since May 28, 2020
- `until%3A2020-06-05%20`: until June 5, 2020
- `-filter%3Areplies`: filter replies

You can change these values in the URL to expand or narrow your search.

Google:

The following Google searches are helpful for finding statements & relevant articles about a company:

- <company name> Black Lives Matter
- <company name> George Floyd
- <company name> Diversity
- <company name> Inclusion
