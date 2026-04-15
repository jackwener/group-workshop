---
name: spec-document-generator
description: Generate spec documents from requirements following a structured template. Use when creating software specification documents, filling spec templates, or generating documentation based on requirements.
---

# Spec Document Generator

## Overview

This skill helps generate comprehensive spec documents by following a structured template and filling in required sections based on existing requirements and specifications.

## Instructions

1. **Understand the template structure**: The spec template consists of 14 documents (01-14) covering different aspects of software specification.

2. **Follow the generation order**:
   - First: Fill 03-立项提案与范围说明.md based on 02-需求来源与采集记录.md
   - Second: Fill 05-用户故事与验收标准.md and 09-API接口规格.md based on 03 and 04
   - Third: Fill R4 design layer documents in order: 08+10+06+07+11

3. **Ask for target directory**: Always ask the user where to place the spec files before starting.

4. **Preserve existing content**: Only fill in areas marked with 【填写】,【请填写】,【请补充】 etc., keeping existing content unchanged.

## Generation Workflow

### Phase 1: Foundation Documents
- Use 02-需求来源与采集记录.md to fill 03-立项提案与范围说明.md
- Use 03 and 04 to fill 05-用户故事与验收标准.md and 09-API接口规格.md

### Phase 2: Architecture & Data Model (08 & 10)
For 08-系统架构与技术选型.md:
- Complete architecture style decisions with rationale
- Add frontend styling approach selection
- Define storage evolution for P1/P2 phases
- Write complete ADR-002 and ADR-003 decisions
- Complete security architecture layers

For 10-数据模型与存储规格.md:
- Complete method signatures and behaviors with associated TCs
- Ensure field types match 09-API response types
- Verify TC numbers are defined in 13-测试策略与质量门禁.md

### Phase 3: Functional & Non-Functional Specs (06 & 07)
For 06-功能规格说明.md:
- Complete interaction behaviors for session selection
- Fill state B and C UI elements
- Add frontend display text for error codes
- Complete State variables (at least 4 more)
- Complete US→FSD alignment table for US-003~006

For 07-非功能需求与约束.md:
- Add latency metrics for page load, file I/O
- Complete failure modes and recovery methods
- Add sensitive data protection measures
- Complete session title default constraints
- Label each constraint with source document number

### Phase 4: Security Design (11)
For 11-安全设计规格.md:
- Complete security objectives with compliance basis
- Fill authentication mechanism status
- Complete role and permission matrix
- Fill encryption strategy with production recommendations
- Complete CSRF protection implementation
- Complete LLM security acceptance criteria
- Complete STRIDE threat model entries
- Add deployment security requirements

## Key Requirements

- Maintain consistency across all documents
- Cross-reference related sections properly
- Ensure technical specifications align between documents
- Validate that all 【填写】 areas are completed
- Ask for spec file placement directory before generation

## Output Format

Generate complete markdown files following the spec template format, preserving existing structure while filling designated areas.
