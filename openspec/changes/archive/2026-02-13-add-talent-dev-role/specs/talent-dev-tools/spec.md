## ADDED Requirements

### Requirement: Talent dev role identity extraction
`app/tools/hr/utils.py` SHALL provide `get_talent_dev_id(run_context)` that extracts employee_id and verifies `"talent_dev"` is in roles. SHALL raise `ValueError` if role is missing. `_MOCK_EMPLOYEES` SHALL include at least one user with `"talent_dev"` role.

#### Scenario: Valid talent_dev user
- **WHEN** `get_talent_dev_id` is called with a run_context whose session_state roles contain `"talent_dev"`
- **THEN** it SHALL return the employee_id

#### Scenario: Non talent_dev user
- **WHEN** `get_talent_dev_id` is called with a run_context whose roles do NOT contain `"talent_dev"`
- **THEN** it SHALL raise `ValueError` with message indicating the function is restricted to talent development role

### Requirement: Individual data query tools
`app/tools/hr/talent_dev_query.py` SHALL provide the following tools, each gated by `get_talent_dev_id`:

1. `td_get_employee_profile(run_context, employee_id)` — full profile including salary and social insurance (reuse `get_any_employee_profile` service)
2. `td_get_employee_training(run_context, employee_id, status?)` — training records, optionally filtered by status
3. `td_get_employee_talent_review(run_context, employee_id, review_year?)` — talent review history
4. `td_get_employee_idp(run_context, employee_id, plan_year?)` — development plans
5. `td_get_employee_performance(run_context, employee_id)` — performance review history with full details (score, comment)
6. `td_get_employee_history(run_context, employee_id)` — employment history (job changes)
7. `td_get_employee_attendance(run_context, employee_id, start_date?, end_date?)` — attendance records

All tools SHALL return JSON string. All tools SHALL reject non-talent_dev users.

#### Scenario: Query employee training as talent_dev
- **WHEN** talent_dev user calls `td_get_employee_training` with a valid employee_id
- **THEN** system SHALL return JSON array of that employee's training records

#### Scenario: Query blocked for non talent_dev
- **WHEN** a user without talent_dev role calls any `td_*` tool
- **THEN** system SHALL return an error message string (not raise exception)

### Requirement: Training summary report
`td_training_summary(run_context, year?)` SHALL return per-department training statistics: department name, total employees, completed count, completion rate, total hours, average hours per person, mandatory completion rate.

#### Scenario: Training summary output
- **WHEN** talent_dev user calls `td_training_summary`
- **THEN** system SHALL return JSON array with one entry per department containing completion rate and hour statistics

### Requirement: Nine-grid distribution report
`td_nine_grid_distribution(run_context, review_year?, department_id?)` SHALL return nine-grid position distribution. Optionally filtered by department. SHALL also include a list of high-potential employees (tag = "高潜" or "继任候选").

#### Scenario: Company-wide nine-grid
- **WHEN** talent_dev user calls `td_nine_grid_distribution` without department filter
- **THEN** system SHALL return distribution counts for all 9 positions plus high-potential employee list

#### Scenario: Department-filtered nine-grid
- **WHEN** talent_dev user calls `td_nine_grid_distribution` with a specific department_id
- **THEN** system SHALL return nine-grid distribution for employees in that department only

### Requirement: Performance distribution report
`td_performance_distribution(run_context, year?, half?)` SHALL return per-department performance rating distribution: department name, counts and percentages for each rating (A/B+/B/C/D).

#### Scenario: Performance distribution output
- **WHEN** talent_dev user calls `td_performance_distribution`
- **THEN** system SHALL return JSON array with rating counts and percentages per department

### Requirement: Turnover analysis report
`td_turnover_analysis(run_context)` SHALL return per-department turnover statistics: department name, total headcount, active count, resigned count, turnover rate, probation-to-regular conversion rate, average tenure in years.

#### Scenario: Turnover analysis output
- **WHEN** talent_dev user calls `td_turnover_analysis`
- **THEN** system SHALL return JSON array with turnover and tenure statistics per department

### Requirement: Promotion statistics report
`td_promotion_stats(run_context, year?)` SHALL return per-department promotion/transfer statistics: department name, promotion count, transfer-in count, transfer-out count, promotion rate.

#### Scenario: Promotion stats output
- **WHEN** talent_dev user calls `td_promotion_stats`
- **THEN** system SHALL return JSON array with promotion and transfer counts per department

### Requirement: IDP summary report
`td_idp_summary(run_context, plan_year?)` SHALL return IDP statistics: total plans, completion rate, category distribution, average progress.

#### Scenario: IDP summary output
- **WHEN** talent_dev user calls `td_idp_summary`
- **THEN** system SHALL return JSON with IDP completion and category statistics

### Requirement: Tools export
`app/tools/hr/__init__.py` SHALL export `talent_dev_tools` list containing all 13 tools. `all_tools` SHALL include `talent_dev_tools`.

#### Scenario: Tools importable
- **WHEN** code imports `talent_dev_tools` from `app.tools.hr`
- **THEN** it SHALL be a list of 13 callable tool functions
