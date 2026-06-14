# 学校查询逻辑优化 - 产品需求文档

## Overview
- **Summary**: 优化学校查询API的代码结构，简化查询逻辑，提高代码可读性和维护性
- **Purpose**: 降低代码复杂度，提升API性能，便于后续扩展
- **Target Users**: 前端开发人员、后端维护人员

## Goals
- 简化SQL查询语句，减少重复代码
- 统一数据库连接管理
- 简化字段映射逻辑
- 提高代码可读性
- 保持API接口兼容性

## Non-Goals (Out of Scope)
- 修改API接口参数
- 改变数据返回格式
- 添加新功能

## Background & Context
- 当前schools.py有329行，包含大量重复的数据库操作代码
- `convert_school_row`函数处理复杂的字段名映射
- 多个接口有相似的异常处理逻辑

## Functional Requirements
- **FR-1**: 统一数据库连接管理
- **FR-2**: 简化SQL查询构建
- **FR-3**: 简化字段映射逻辑
- **FR-4**: 统一异常处理

## Acceptance Criteria

### AC-1: 代码行数减少
- **Given**: 优化前代码329行
- **When**: 完成优化
- **Then**: 代码行数减少30%以上
- **Verification**: `human-judgment`

### AC-2: API接口兼容性
- **Given**: 前端调用原API接口
- **When**: 优化后
- **Then**: 返回数据格式完全一致
- **Verification**: `programmatic`

### AC-3: 查询性能
- **Given**: 执行相同查询
- **When**: 优化前后对比
- **Then**: 查询时间不增加
- **Verification**: `programmatic`

## Constraints
- 保持API接口不变
- 保持数据返回格式不变