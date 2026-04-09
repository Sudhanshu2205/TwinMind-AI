# TwinMind AI Educational Content Generator & Reviewer

This project is a simple AI assessment submission built exactly around the assignment brief.

It has only two AI agents:

1. `GeneratorAgent`
2. `ReviewerAgent`

There is no heavy agent framework, no LangChain setup, and no unnecessary abstraction. The goal is to show clear thinking, clear responsibilities, and clear structured output.

## What this app does

A user enters:

- a school grade
- a learning topic

Example:

```json
{
  "grade": 4,
  "topic": "Types of angles"
}
```

Then the app does three things:

1. The `GeneratorAgent` creates draft educational content.
2. The `ReviewerAgent` checks whether the content is suitable.
3. If the review fails, the app runs the generator one more time using the reviewer feedback.

That second try is the only refinement pass. It does not keep retrying again and again.

## In plain English

If someone nontechnical is reading this, the system works like this:

- Think of the Generator Agent as a teacher writing the first draft of a lesson.
- Think of the Reviewer Agent as another teacher checking whether the lesson is clear and age-appropriate.
- If the second teacher finds a problem, the first teacher gets one chance to improve the lesson.
- The screen shows each step clearly so you can see what happened.

## Why this matches the assignment

The assignment asked for:

- two AI agents
- clear responsibility for each agent
- structured input
- structured output
- lightweight refinement logic
- a UI that makes the agent flow obvious

This project matches that exactly.

## Agent 1: Generator Agent

Responsibility:

- Generate draft educational content for a given grade and topic.

Structured input:

```json
{
  "grade": 4,
  "topic": "Types of angles"
}
```

Structured output:

```json
{
  "explanation": "...",
  "mcqs": [
    {
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "B"
    }
  ]
}
```

What it tries to do well:

- use language that matches the selected grade
- keep concepts correct
- always return the same structure

## Agent 2: Reviewer Agent

Responsibility:

- Evaluate the Generator Agent output.

Reviewer input:

- the content produced by the generator
- the grade and topic already selected in the app, so the reviewer can judge age level and topic relevance

Structured output:

```json
{
  "status": "pass",
  "feedback": []
}
```

or

```json
{
  "status": "fail",
  "feedback": [
    "Explanation too long for Grade 4.",
    "Question 2 is too complex for Grade 4."
  ]
}
```

What the reviewer checks:

- age appropriateness
- conceptual correctness
- clarity

## Refinement logic

The assignment asked for a lightweight refinement loop.

This project does exactly this:

1. Generate content
2. Review content
3. If the review fails, generate once more using the reviewer feedback
4. Stop there

There is no separate refiner agent because the assignment says that is not required.

## UI behavior

The UI is designed so the flow is obvious.

It shows:

- the structured input
- the Generator Agent output
- the Reviewer Agent feedback
- the refined output, only if refinement was needed

This makes it easy for an interviewer to understand the pipeline quickly.

## Files in this project

- `app.py`
  This is the full application. It contains the two agents, the pipeline, and the small local web server.

- `tests/test_pipeline.py`
  This contains simple tests that prove the pipeline works and that refinement happens when expected.

- `README.md`
  This file explains the project in a simple and nontechnical way.

## How to run the project

Open PowerShell in the project folder and run:

```powershell
python .\app.py
```

If `python` does not work on your machine, try:

```powershell
py .\app.py
```

Then open this in your browser:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

## How to run the tests

```powershell
python -m unittest discover -s tests -v
```

## Example of the full flow

Input:

```json
{
  "grade": 4,
  "topic": "Types of angles"
}
```

Step 1:
The Generator Agent creates an explanation and MCQs.

Step 2:
The Reviewer Agent checks whether the explanation and questions fit Grade 4.

Step 3:
If the reviewer says `fail`, the Generator Agent tries one more time using that feedback.

Step 4:
The UI displays everything clearly.

## Design choice: why no framework

The assessment clearly says:

- simple Python classes or functions are sufficient
- a full agent framework is not required

So this project intentionally uses plain Python classes.

That keeps the work:

- easier to understand
- easier to explain in an interview
- closer to the assignment
- less likely to feel over-engineered

## Short summary

This submission is built to show good judgment:

- exactly two agents
- structured input and output
- one refinement pass
- clear UI
- simple Python implementation
- easy explanation for both technical and nontechnical readers
