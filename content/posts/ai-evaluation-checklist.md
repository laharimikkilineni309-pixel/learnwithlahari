---
title: "A Practical LLM Evaluation Checklist for QA Engineers"
slug: ai-evaluation-checklist
category: AI
summary: "Test correctness, grounding, tool behavior, safety, and reliability without relying on one accuracy score."
date: 2026-11-16
published: true
---

# A Practical LLM Evaluation Checklist for QA Engineers

AI responses are probabilistic, so testing only whether one expected sentence appears is brittle. Start by defining what **good behavior** means for each user task.

## 1. Define the use case

Write down the user goal, expected source of truth, permitted tools, and unacceptable behaviors. Keep a small golden dataset with typical, ambiguous, and adversarial prompts.

## 2. Evaluate output quality

- **Correctness:** Is the answer factually accurate for the task?
- **Groundedness:** Are claims supported by retrieved documents or trusted context?
- **Completeness:** Did the assistant answer the actual question?
- **Format compliance:** Did it follow the required schema or output contract?

## 3. Test retrieval and tool use

For RAG, assess whether the relevant documents were retrieved before judging the generated answer. For agents, check tool selection, arguments, permissions, retry behavior, and what happens when tools fail.

## 4. Cover reliability and safety

Test prompt injection, sensitive-data exposure, missing context, timeouts, rate limits, duplicate tool calls, and multi-turn state handling. Include both expected successes and safe failures.

## 5. Make results repeatable

Record prompt versions, model versions, dataset versions, evaluation criteria, and traces. Use human review for high-impact cases and calibrate any LLM-as-judge scoring against reviewed examples.

## Starter test case

**Scenario:** The incident assistant summarizes a ticket with no matching knowledge article.

**Expected:** It summarizes supported ticket facts, does not invent a KB citation, and clearly states when a resolution is uncertain.

**Signals:** Groundedness, citation validity, tool trace, latency, and error handling.

The goal is not a single perfect score. It is an evaluation system that makes regressions visible and helps engineers fix the right layer.
