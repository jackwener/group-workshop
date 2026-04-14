#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "=== 1. shared/ 4 文件齐全 ==="
for f in rubric-scale.md report-template.md score-schema.json evidence-requirements.md; do
  [ -f "skills/grading-shared/$f" ] || { echo "missing skills/grading-shared/$f"; exit 1; }
done
echo "OK"

echo "=== 2. score-schema.json 是合法 JSON ==="
node -e "JSON.parse(require('fs').readFileSync('skills/grading-shared/score-schema.json','utf8'))"
echo "OK"

echo "=== 3. 生成 sample summary 并过 ajv ==="
cat > /tmp/sample-fe.json <<'EOF'
{
  "team": "team-sample",
  "side": "frontend",
  "total": 78.4,
  "grade": "B",
  "dimensions": [
    {"name":"spec-conformance","score":8,"weight":20,"weighted":16.0},
    {"name":"theme-aesthetic","score":6,"weight":12,"weighted":7.2},
    {"name":"animation","score":7,"weight":10,"weighted":7.0},
    {"name":"state-completeness","score":8,"weight":10,"weighted":8.0},
    {"name":"code-quality","score":7,"weight":10,"weighted":7.0},
    {"name":"responsive","score":8,"weight":8,"weighted":6.4},
    {"name":"forms","score":9,"weight":8,"weighted":7.2},
    {"name":"performance","score":8,"weight":8,"weighted":6.4},
    {"name":"a11y","score":5,"weight":8,"weighted":4.0},
    {"name":"microcopy","score":8,"weight":6,"weighted":4.8}
  ],
  "top_fixes": ["补管理员页","加 error boundary","统一按钮 hover"],
  "evidence_count": 23,
  "graded_at": "2026-04-14T10:00:00Z"
}
EOF
npx --yes -p ajv-cli@5 -p ajv-formats@3 ajv validate -c ajv-formats -s skills/grading-shared/score-schema.json -d /tmp/sample-fe.json
echo "OK"

echo "=== 4. 前端 SKILL.md 10 维度 ==="
cnt=$(grep -c "^### [0-9]" skills/grading-frontend/SKILL.md)
[ "$cnt" -ge 10 ] || { echo "frontend dimensions = $cnt, expected 10"; exit 1; }
echo "OK ($cnt)"

echo "=== 5. 前端 SKILL.md 权重合计 100 ==="
sum=$(grep -oE "权重 [0-9]+" skills/grading-frontend/SKILL.md | awk '{s+=$2} END {print s}')
[ "$sum" = "100" ] || { echo "frontend weight sum = $sum, expected 100"; exit 1; }
echo "OK"

echo "=== 6. 后端 SKILL.md 9 维度 + 权重 100 ==="
cnt=$(grep -c "^### [0-9]" skills/grading-backend/SKILL.md)
[ "$cnt" -ge 9 ] || { echo "backend dimensions = $cnt, expected 9"; exit 1; }
sum=$(grep -oE "权重 [0-9]+" skills/grading-backend/SKILL.md | awk '{s+=$2} END {print s}')
[ "$sum" = "100" ] || { echo "backend weight sum = $sum, expected 100"; exit 1; }
echo "OK ($cnt dims, sum=$sum)"

echo "=== 7. anti-patterns 两个文件存在且非空 ==="
for f in skills/grading-frontend/anti-patterns.md skills/grading-backend/anti-patterns.md; do
  [ -s "$f" ] || { echo "missing or empty: $f"; exit 1; }
done
echo "OK"

echo "=== 8. probe 脚本 executable + 语法合法 ==="
for f in skills/grading-frontend/probes/*.sh skills/grading-backend/probes/*.sh; do
  [ -x "$f" ] || { echo "not executable: $f"; exit 1; }
  bash -n "$f" || { echo "syntax error: $f"; exit 1; }
done
echo "OK"

echo ""
echo "=== ALL OK ==="
