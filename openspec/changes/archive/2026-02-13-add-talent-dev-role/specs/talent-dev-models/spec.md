## ADDED Requirements

### Requirement: Training model
The system SHALL provide a `Training` ORM model in `app/models/hr/training.py` representing both training records and training plans in a single table `trainings`.

Fields:
- `employee_id` (FK → employees.id, indexed)
- `course_name` (str, max 128)
- `category` (str, max 32): 专业技能/通用素质/管理能力/合规必修
- `hours` (Decimal): 学时
- `score` (int | None): 考试分数，无考试则为空
- `status` (str, max 16): 待开始/进行中/已完成/未通过
- `provider` (str, max 64): 培训机构或内训讲师
- `assigned_by` (str, max 64, default ""): 指派人，空字符串表示自主报名
- `deadline` (date | None): 截止日期
- `completed_date` (date | None): 完成日期

#### Scenario: Training model is registered
- **WHEN** application starts
- **THEN** `trainings` table SHALL exist with all specified columns and constraints

#### Scenario: Training seed data generated
- **WHEN** `scripts/generate_seed.py` is executed
- **THEN** system SHALL generate training records for existing employees, covering all 4 categories, with a mix of completed/in-progress/pending statuses

### Requirement: TalentReview model
The system SHALL provide a `TalentReview` ORM model in `app/models/hr/talent_review.py` representing annual talent review (nine-grid) results in table `talent_reviews`.

Fields:
- `employee_id` (FK → employees.id, indexed)
- `review_year` (int)
- `performance` (str, max 8): 高/中/低
- `potential` (str, max 8): 高/中/低
- `nine_grid_pos` (str, max 16): 明星/骨干/潜力股/中坚/待雕琢/守成者/专家/待观察/淘汰区
- `tag` (str, max 32): 高潜/关键岗位/继任候选/普通
- `reviewer` (str, max 64)
- `comment` (str, max 512, default "")

#### Scenario: TalentReview model is registered
- **WHEN** application starts
- **THEN** `talent_reviews` table SHALL exist with all specified columns

#### Scenario: TalentReview seed data consistent with performance
- **WHEN** seed data is generated
- **THEN** employees with performance rating A/B+ SHALL have `performance` = "高" in their talent review; employees with rating D SHALL have `performance` = "低"

### Requirement: DevelopmentPlan model
The system SHALL provide a `DevelopmentPlan` ORM model in `app/models/hr/development_plan.py` representing individual development plans (IDP) in table `development_plans`.

Fields:
- `employee_id` (FK → employees.id, indexed)
- `plan_year` (int)
- `goal` (str, max 256): 发展目标
- `category` (str, max 32): 技术深耕/管理转型/跨领域拓展/专业认证
- `actions` (str, max 512): 行动计划
- `status` (str, max 16): 进行中/已完成/已放弃
- `progress` (int): 0-100 百分比
- `deadline` (date)

#### Scenario: DevelopmentPlan model is registered
- **WHEN** application starts
- **THEN** `development_plans` table SHALL exist with all specified columns

#### Scenario: DevelopmentPlan seed data generated
- **WHEN** seed data is generated
- **THEN** system SHALL generate IDP records for a subset of employees with varied goals, categories, and progress values

### Requirement: Models exported in __init__
The `app/models/hr/__init__.py` SHALL export `Training`, `TalentReview`, and `DevelopmentPlan`.

#### Scenario: Models importable
- **WHEN** code imports from `app.models.hr`
- **THEN** `Training`, `TalentReview`, `DevelopmentPlan` SHALL be available
