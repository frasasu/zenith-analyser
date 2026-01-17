
---

## **Fichier 6: .github/ISSUE_TEMPLATE/question.md**
```markdown
---
name: Question
about: Ask a question about using Zenith Analyser
title: '[QUESTION] '
labels: ['question', 'support']
assignees: ''
---

## Question
What is your question about Zenith Analyser?

## Context
What are you trying to accomplish? Please provide context for your question.

## Code Example
If applicable, provide a code example that demonstrates your question:
```python
from zenith_analyser import ZenithAnalyser

code = """
law example:
    start_date:2024-01-01 at 10:00
    period:1.0
    Event:
        TASK:"Example task"
    GROUP:(TASK 1.0^0)
end_law
"""

analyser = ZenithAnalyser(code)
# Your question relates to this code...
