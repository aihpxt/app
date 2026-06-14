# 数据库架构报告

## 基本信息
- 数据库路径: e:\aiphxt-app\ai-service\sqlite\data\unified_school_data.db
- SQLite版本: 3.50.4

## 表统计: 16 个业务表

### user_activities
- 记录数: 20
- 字段数: 5
- 索引数: 3

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| username | TEXT | 是 |  |  |
| activity_type | TEXT | 是 |  |  |
| details | TEXT | 否 |  |  |
| timestamp | TIMESTAMP | 否 | CURRENT_TIMESTAMP |  |

### collections
- 记录数: 4
- 字段数: 5
- 索引数: 3

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| username | TEXT | 是 |  |  |
| item_type | TEXT | 是 |  |  |
| item_id | INTEGER | 是 |  |  |
| created_at | TIMESTAMP | 否 | CURRENT_TIMESTAMP |  |

### notification_settings
- 记录数: 453
- 字段数: 7
- 索引数: 1

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| username | TEXT | 是 |  |  |
| policy_update | BOOLEAN | 是 | 1 |  |
| volunteer_reminder | BOOLEAN | 是 | 1 |  |
| event_notification | BOOLEAN | 是 | 1 |  |
| system_message | BOOLEAN | 是 | 1 |  |
| recommend_message | BOOLEAN | 是 | 1 |  |

### test_history
- 记录数: 5
- 字段数: 9
- 索引数: 2

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| username | TEXT | 是 |  |  |
| test_id | INTEGER | 是 |  |  |
| test_name | TEXT | 是 |  |  |
| score | INTEGER | 是 |  |  |
| total_questions | INTEGER | 是 |  |  |
| correct_answers | INTEGER | 是 |  |  |
| time_used | INTEGER | 是 |  |  |
| created_at | TIMESTAMP | 否 | CURRENT_TIMESTAMP |  |

### chat_sessions
- 记录数: 1
- 字段数: 5
- 索引数: 2

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| user_id | TEXT | 是 |  |  |
| title | TEXT | 否 |  |  |
| created_at | TIMESTAMP | 否 | CURRENT_TIMESTAMP |  |
| updated_at | TIMESTAMP | 否 | CURRENT_TIMESTAMP |  |

### version
- 记录数: 1
- 字段数: 4
- 索引数: 1

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| table_name | TEXT | 是 |  |  |
| version | INTEGER | 是 |  |  |
| last_updated | TIMESTAMP | 否 | CURRENT_TIMESTAMP |  |

### school_admission_history
- 记录数: 56
- 字段数: 9
- 索引数: 2

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| school_id | INTEGER | 否 |  |  |
| year | INTEGER | 否 |  |  |
| min_score | REAL | 否 |  |  |
| max_score | REAL | 否 |  |  |
| avg_score | REAL | 否 |  |  |
| one_rate | REAL | 否 |  |  |
| student_count | INTEGER | 否 |  |  |
| min_rank | INTEGER | 否 |  |  |

### schools
- 记录数: 2090
- 字段数: 31
- 索引数: 12

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| name | TEXT | 是 |  |  |
| city | TEXT | 否 |  |  |
| district | TEXT | 否 |  |  |
| prefecture | TEXT | 否 |  |  |
| type | INTEGER | 否 |  |  |
| type_name | TEXT | 否 |  |  |
| school_type | TEXT | 否 |  |  |
| level | TEXT | 否 |  |  |
| is_public | INTEGER | 否 | 1 |  |
| is_key | INTEGER | 否 | 0 |  |
| address | TEXT | 否 |  |  |
| phone | TEXT | 否 |  |  |
| website | TEXT | 否 |  |  |
| description | TEXT | 否 |  |  |
| features | TEXT | 否 |  |  |
| logo | TEXT | 否 |  |  |
| min_score | REAL | 否 |  |  |
| min_rank | INTEGER | 否 |  |  |
| max_score | REAL | 否 |  |  |
| avg_score | REAL | 否 |  |  |
| one_rate | REAL | 否 |  |  |
| student_count | INTEGER | 否 |  |  |
| teacher_count | INTEGER | 否 |  |  |
| area | TEXT | 否 |  |  |
| tuition | INTEGER | 否 |  |  |
| boarding | INTEGER | 否 | 0 |  |
| view_count | INTEGER | 否 | 0 |  |
| style | TEXT | 否 |  |  |
| created_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |
| updated_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |

### users
- 记录数: 21
- 字段数: 7
- 索引数: 2

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| username | TEXT | 否 |  |  |
| email | TEXT | 否 |  |  |
| hashed_password | TEXT | 否 |  |  |
| role | TEXT | 否 |  |  |
| created_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |
| updated_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |

### policies
- 记录数: 3
- 字段数: 6
- 索引数: 2

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| title | TEXT | 否 |  |  |
| content | TEXT | 否 |  |  |
| category | TEXT | 否 |  |  |
| publish_date | TEXT | 否 |  |  |
| created_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |

### notifications
- 记录数: 2265
- 字段数: 7
- 索引数: 2

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| username | TEXT | 否 |  |  |
| title | TEXT | 否 |  |  |
| content | TEXT | 否 |  |  |
| type | TEXT | 否 |  |  |
| is_read | TEXT | 否 |  |  |
| created_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |

### favorites
- 记录数: 0
- 字段数: 5
- 索引数: 2

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| username | TEXT | 否 |  |  |
| school_id | TEXT | 否 |  |  |
| note | TEXT | 否 |  |  |
| created_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |

### chat_messages
- 记录数: 0
- 字段数: 5
- 索引数: 2

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| session_id | TEXT | 否 |  |  |
| role | TEXT | 否 |  |  |
| content | TEXT | 否 |  |  |
| created_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |

### school_news
- 记录数: 100
- 字段数: 7
- 索引数: 3

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| school_name | TEXT | 否 |  |  |
| news_type | TEXT | 否 |  |  |
| content | TEXT | 否 |  |  |
| publish_time | TEXT | 否 |  |  |
| source | TEXT | 否 |  |  |
| created_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |

### user_feedbacks
- 记录数: 0
- 字段数: 7
- 索引数: 0

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| school_name | TEXT | 否 |  |  |
| feedback_type | TEXT | 否 |  |  |
| content | TEXT | 否 |  |  |
| contact_info | TEXT | 否 |  |  |
| status | TEXT | 否 | 'pending' |  |
| created_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |

### db_statistics
- 记录数: 7
- 字段数: 5
- 索引数: 1

| 字段名 | 类型 | 可空 | 默认值 | 主键 |
|--------|------|------|--------|------|
| id | INTEGER | 否 |  | ✓ |
| stat_key | TEXT | 是 |  |  |
| stat_value | TEXT | 否 |  |  |
| description | TEXT | 否 |  |  |
| updated_at | DATETIME | 否 | CURRENT_TIMESTAMP |  |
