| constraint_name                             | table_name               | column_name     | foreign_table_name | foreign_column_name |
| ------------------------------------------- | ------------------------ | --------------- | ------------------ | ------------------- |
| africa_intelligence_feed_type_id_fkey       | africa_intelligence_feed | type_id         | funding_types      | id                  |
| fk_africa_intelligence_feed_funding_type_id | africa_intelligence_feed | funding_type_id | funding_types      | id                  |
| fk_africa_intelligence_feed_type_id         | africa_intelligence_feed | funding_type_id | funding_types      | id                  |

| column_name                     | data_type                   | character_maximum_length | column_default                                       | is_nullable |
| ------------------------------- | --------------------------- | ------------------------ | ---------------------------------------------------- | ----------- |
| id                              | integer                     | null                     | nextval('africa_intelligence_feed_id_seq'::regclass) | NO          |
| title                           | character varying           | 255                      | null                                                 | YES         |
| description                     | text                        | null                     | null                                                 | YES         |
| amount_min                      | numeric                     | null                     | null                                                 | YES         |
| amount_max                      | numeric                     | null                     | null                                                 | YES         |
| application_deadline            | date                        | null                     | null                                                 | YES         |
| application_url                 | character varying           | 255                      | null                                                 | YES         |
| eligibility_criteria            | jsonb                       | null                     | null                                                 | YES         |
| ai_domains                      | jsonb                       | null                     | null                                                 | YES         |
| geographic_scopes               | jsonb                       | null                     | null                                                 | YES         |
| funding_type_id                 | integer                     | null                     | null                                                 | YES         |
| provider_organization_id        | integer                     | null                     | null                                                 | YES         |
| recipient_organization_id       | integer                     | null                     | null                                                 | YES         |
| grant_duration_months           | integer                     | null                     | null                                                 | YES         |
| grant_renewable                 | boolean                     | null                     | null                                                 | YES         |
| equity_percentage               | double precision            | null                     | null                                                 | YES         |
| valuation_cap                   | numeric                     | null                     | null                                                 | YES         |
| interest_rate                   | double precision            | null                     | null                                                 | YES         |
| expected_roi                    | double precision            | null                     | null                                                 | YES         |
| status                          | character varying           | 50                       | null                                                 | YES         |
| additional_resources            | jsonb                       | null                     | null                                                 | YES         |
| equity_focus_details            | jsonb                       | null                     | null                                                 | YES         |
| women_focus                     | boolean                     | null                     | null                                                 | YES         |
| underserved_focus               | boolean                     | null                     | null                                                 | YES         |
| youth_focus                     | boolean                     | null                     | null                                                 | YES         |
| created_at                      | timestamp with time zone    | null                     | null                                                 | YES         |
| updated_at                      | timestamp with time zone    | null                     | null                                                 | YES         |
| funding_type                    | character varying           | 100                      | null                                                 | YES         |
| funding_amount                  | character varying           | 200                      | null                                                 | YES         |
| application_process             | text                        | null                     | null                                                 | YES         |
| contact_information             | text                        | null                     | null                                                 | YES         |
| additional_notes                | text                        | null                     | null                                                 | YES         |
| source_url                      | character varying           | 2000                     | null                                                 | YES         |
| source_type                     | character varying           | 50                       | null                                                 | YES         |
| collected_at                    | timestamp without time zone | null                     | null                                                 | YES         |
| keywords                        | jsonb                       | null                     | null                                                 | YES         |
| content_category                | character varying           | 50                       | 'general'::character varying                         | YES         |
| relevance_score                 | numeric                     | null                     | 0.5                                                  | YES         |
| ai_extracted                    | boolean                     | null                     | false                                                | YES         |
| geographic_focus                | character varying           | 100                      | null                                                 | YES         |
| sector_tags                     | ARRAY                       | null                     | null                                                 | YES         |
| currency                        | character varying           | 10                       | 'USD'::character varying                             | YES         |
| amount_exact                    | double precision            | null                     | null                                                 | YES         |
| type_id                         | integer                     | null                     | null                                                 | YES         |
| is_excluded                     | boolean                     | null                     | false                                                | YES         |
| exclude_reason                  | text                        | null                     | null                                                 | YES         |
| human_last_reviewed_on          | timestamp with time zone    | null                     | null                                                 | YES         |
| human_last_reviewed_by          | text                        | null                     | null                                                 | YES         |
| comments                        | text                        | null                     | null                                                 | YES         |
| recommendation                  | text                        | null                     | null                                                 | YES         |
| total_funding_pool              | numeric                     | null                     | null                                                 | YES         |
| min_amount_per_project          | numeric                     | null                     | null                                                 | YES         |
| max_amount_per_project          | numeric                     | null                     | null                                                 | YES         |
| exact_amount_per_project        | numeric                     | null                     | null                                                 | YES         |
| estimated_project_count         | integer                     | null                     | null                                                 | YES         |
| project_count_range             | jsonb                       | null                     | null                                                 | YES         |
| application_deadline_type       | character varying           | 20                       | 'fixed'::character varying                           | YES         |
| announcement_date               | date                        | null                     | null                                                 | YES         |
| funding_start_date              | date                        | null                     | null                                                 | YES         |
| project_duration                | character varying           | 100                      | null                                                 | YES         |
| selection_criteria              | jsonb                       | null                     | null                                                 | YES         |
| target_audience                 | jsonb                       | null                     | null                                                 | YES         |
| ai_subsectors                   | jsonb                       | null                     | null                                                 | YES         |
| development_stage               | jsonb                       | null                     | null                                                 | YES         |
| collaboration_required          | boolean                     | null                     | null                                                 | YES         |
| gender_focused                  | boolean                     | null                     | null                                                 | YES         |
| youth_focused                   | boolean                     | null                     | null                                                 | YES         |
| reporting_requirements          | jsonb                       | null                     | null                                                 | YES         |
| interim_reporting_required      | boolean                     | null                     | null                                                 | YES         |
| final_report_required           | boolean                     | null                     | null                                                 | YES         |
| financial_reporting_frequency   | character varying           | 20                       | null                                                 | YES         |
| intellectual_property_rights    | text                        | null                     | null                                                 | YES         |
| publication_requirements        | text                        | null                     | null                                                 | YES         |
| liquidation_preference          | text                        | null                     | null                                                 | YES         |
| board_representation            | boolean                     | null                     | null                                                 | YES         |
| anti_dilution_protection        | text                        | null                     | null                                                 | YES         |
| drag_along_rights               | boolean                     | null                     | null                                                 | YES         |
| tag_along_rights                | boolean                     | null                     | null                                                 | YES         |
| competition_phases              | jsonb                       | null                     | null                                                 | YES         |
| judging_criteria                | jsonb                       | null                     | null                                                 | YES         |
| submission_format               | text                        | null                     | null                                                 | YES         |
| presentation_required           | boolean                     | null                     | null                                                 | YES         |
| team_size_limit                 | integer                     | null                     | null                                                 | YES         |
| intellectual_property_ownership | text                        | null                     | null                                                 | YES         |
| urgency_level                   | character varying           | 10                       | null                                                 | YES         |
| days_until_deadline             | integer                     | null                     | null                                                 | YES         |
| is_deadline_approaching         | boolean                     | null                     | false                                                | YES         |
| suitable_for_startups           | boolean                     | null                     | false                                                | YES         |
| suitable_for_researchers        | boolean                     | null                     | false                                                | YES         |
| suitable_for_smes               | boolean                     | null                     | false                                                | YES         |
| suitable_for_individuals        | boolean                     | null                     | false                                                | YES         |
| renewable                       | boolean                     | null                     | null                                                 | YES         |
| is_active                       | boolean                     | null                     | true                                                 | YES         |
| is_accepting_applications       | boolean                     | null                     | true                                                 | YES         |
| requires_registration           | boolean                     | null                     | true                                                 | YES         |