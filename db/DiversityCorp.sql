CREATE TYPE "business_sectors" AS ENUM (
  'agriculture_plantations_other_rural',
  'basic_metal_production',
  'chemical_industries',
  'commerce',
  'construction',
  'education',
  'financial_and_professional_services',
  'food_drink_tobacco',
  'forestry_wood_pulp_paper',
  'health_services',
  'hotels_tourism_catering',
  'mining_coal_and_others',
  'mechanical_and_electrical_engineering',
  'media_culture_graphical',
  'oil_gas_production_and_refining',
  'postal_and_telecommunication_services',
  'public_services',
  'shipping_ports_fishery_inland_waterways',
  'textiles_clothing_leather_footwear',
  'transport',
  'transport_equipment_manufacturing',
  'utilities_water_gaz_electricity'
);

CREATE TYPE "business_category" AS ENUM (
  'sole_proprietorship',
  'partnership',
  'limited_liability_company',
  'business_corporation'
);

CREATE TABLE "companies" (
  "id" SERIAL PRIMARY KEY,
  "full_name" varchar,
  "usual_name" varchar NOT NULL,
  "created_at" smallint,
  "country" varchar,
  "category" business_category,
  "detailed_category" varchar,
  "sector" business_sectors,
  "last_full_update" date NOT NULL
);

CREATE TABLE "fortune_rankings" (
  "ranked_at" smallint NOT NULL,
  "ranking" smallint NOT NULL,
  "company_id" int NOT NULL,
  "fortune_summary" text,
  PRIMARY KEY ("ranked_at", "ranking")
);

CREATE TABLE "financials" (
  "data_at" smallint NOT NULL,
  "company_id" int NOT NULL,
  "revenues" int,
  "profits" int,
  "market_value" int,
  "assets" int,
  "total_stockholder_equity" int,
  "revenues_increase" numeric,
  "profits_increase" numeric,
  "earnings_per_share" smallint,
  "total_return_for_investors_in_year" numeric,
  "total_annual_return_for_investors_in_ten_years" numeric,
  PRIMARY KEY ("data_at", "company_id")
);

CREATE TABLE "hr" (
  "company" int PRIMARY KEY,
  "last_updated" timestamp NOT NULL,
  "employee_count" int,
  "part_time_employee_count" int,
  "excutive_team" int UNIQUE,
  "diversity_policy_url" varchar,
  "diversity_report_url" varchar,
  "ice_contract" bool,
  "mean_wages" int,
  "median_wages" int
);

CREATE TABLE "executive_teams" (
  "id" SERIAL PRIMARY KEY,
  "size" smallint,
  "photo_url" varchar,
  "ceo_wages" int
);

CREATE TABLE "notable_events" (
  "id" SERIAL PRIMARY KEY,
  "event_at" timestamp NOT NULL,
  "company" int,
  "keywords" varchar,
  "description" varchar,
  "statement_text" text,
  "official_url" varchar,
  "analysis_url" varchar
);

ALTER TABLE "fortune_rankings" ADD FOREIGN KEY ("company_id") REFERENCES "companies" ("id");

ALTER TABLE "financials" ADD FOREIGN KEY ("company_id") REFERENCES "companies" ("id");

ALTER TABLE "hr" ADD FOREIGN KEY ("company") REFERENCES "companies" ("id");

ALTER TABLE "hr" ADD FOREIGN KEY ("excutive_team") REFERENCES "executive_teams" ("id");

ALTER TABLE "notable_events" ADD FOREIGN KEY ("company") REFERENCES "companies" ("id");


COMMENT ON COLUMN "companies"."full_name" IS 'Official registered name';

COMMENT ON COLUMN "companies"."created_at" IS 'Year of official registration';

COMMENT ON COLUMN "companies"."country" IS 'Using international country code';

COMMENT ON COLUMN "companies"."category" IS 'Main type';

COMMENT ON COLUMN "companies"."detailed_category" IS 'Detailed administrative category';

COMMENT ON COLUMN "companies"."last_full_update" IS 'Last time the company info was fully updated in the database';

COMMENT ON COLUMN "fortune_rankings"."fortune_summary" IS 'The short text accompanying the financial data.';

COMMENT ON COLUMN "financials"."revenues" IS 'In millions of dollars';

COMMENT ON COLUMN "financials"."profits" IS 'In millions of dollars';

COMMENT ON COLUMN "financials"."market_value" IS 'In millions of dollars';

COMMENT ON COLUMN "financials"."assets" IS 'In millions of dollars';

COMMENT ON COLUMN "financials"."total_stockholder_equity" IS 'In millions of dollars';

COMMENT ON COLUMN "financials"."revenues_increase" IS 'In percents';

COMMENT ON COLUMN "financials"."profits_increase" IS 'In percents';

COMMENT ON COLUMN "financials"."earnings_per_share" IS 'In dollars';

COMMENT ON COLUMN "financials"."total_return_for_investors_in_year" IS 'In percents';

COMMENT ON COLUMN "financials"."total_annual_return_for_investors_in_ten_years" IS 'In percents';

COMMENT ON COLUMN "hr"."last_updated" IS 'Last time the HR data was updated for this company';

COMMENT ON COLUMN "hr"."employee_count" IS 'As counted by Fortune, fulltime + half of parttime';

COMMENT ON COLUMN "hr"."part_time_employee_count" IS 'Sometimes available in published annual report';

COMMENT ON COLUMN "hr"."diversity_policy_url" IS 'Link to public diversity or inclusion policy';

COMMENT ON COLUMN "hr"."diversity_report_url" IS 'Link to public diversity or inclusion report';

COMMENT ON COLUMN "hr"."ice_contract" IS 'Do they currently have a contract with US Immigration and Customs Enforcements?';

COMMENT ON COLUMN "hr"."mean_wages" IS 'In dollars, yearly, after taxes';

COMMENT ON COLUMN "hr"."median_wages" IS 'In dollars, yearly, after taxes';

COMMENT ON COLUMN "executive_teams"."photo_url" IS 'url to photo of the team, should be stored in GitHub repo';

COMMENT ON COLUMN "executive_teams"."ceo_wages" IS 'In thousand dollars, yearly, after taxes';

COMMENT ON COLUMN "notable_events"."keywords" IS 'Keywords separated by commas';

COMMENT ON COLUMN "notable_events"."description" IS 'Short description if appropriate';

COMMENT ON COLUMN "notable_events"."statement_text" IS 'Official statement of the company';

COMMENT ON COLUMN "notable_events"."official_url" IS 'Link to official website or press release';

COMMENT ON COLUMN "notable_events"."analysis_url" IS 'Link to an analysis article online';
