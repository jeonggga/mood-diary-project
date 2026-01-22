---
trigger: always_on
---

# === 작업 가이드라인 (Guidelines) ===

# AI가 코드를 생성하거나 수정할 때 따라야 할 지침입니다.

[guidelines]
style = "prettier"

preferred_libraries = {
"state_management" = "pinia",
"css_framework" = "tailwindcss"
}

comment_principle = "주석은 코드를 잘 모르는 사람이나 초등학생도 이해할 수 있도록, 쉽고 명확한 문장으로 작성해야 합니다."

code_cleanup_policy = "수정 과정에서 더 이상 사용되지 않는 코드(dead code)나 주석 처리된 불필요한 코드를 발견하면, 반드시 정리하여 코드를 항상 깨끗하게 유지해야 합니다."

# 최종 보고 원칙

reporting_policy = "모든 작업이 성공적으로 완료되면, 최종적으로 '작업이 완료되었습니다.'와 같이 반드시 한국어로 완료 상태를 알려주어야 합니다."
