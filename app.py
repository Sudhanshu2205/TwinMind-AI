from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


HOST = "127.0.0.1"
PORT = 8000


@dataclass(frozen=True)
class MCQ:
    question: str
    options: tuple[str, str, str, str]
    answer: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "options": list(self.options),
            "answer": self.answer,
        }


@dataclass(frozen=True)
class TopicProfile:
    canonical_topic: str
    aliases: tuple[str, ...]
    keywords: tuple[str, ...]
    rich_explanation: str
    simple_explanation: str
    rich_mcqs: tuple[MCQ, ...]
    simple_mcqs: tuple[MCQ, ...]


@dataclass(frozen=True)
class GenerationRequest:
    grade: int
    topic: str

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "GenerationRequest":
        grade = int(payload.get("grade", 4))
        if grade < 1 or grade > 8:
            raise ValueError("Grade must be between 1 and 8.")

        topic = str(payload.get("topic", "")).strip()
        if not topic:
            raise ValueError("Topic is required.")

        return cls(grade=grade, topic=topic)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReviewResult:
    status: str
    feedback: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_topic(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


TOPIC_LIBRARY: tuple[TopicProfile, ...] = (
    TopicProfile(
        canonical_topic="Types of Angles",
        aliases=("types of angles", "angles", "angle types"),
        keywords=("angle", "angles", "acute", "right", "obtuse"),
        rich_explanation=(
            "An angle is formed when two rays meet at one point, and its size "
            "shows how much turning happens between them. Acute angles are small, "
            "right angles make a square corner, and obtuse angles open wider."
        ),
        simple_explanation=(
            "An angle is made when two lines meet. Acute angles are small, right "
            "angles make a square corner, and obtuse angles are wide."
        ),
        rich_mcqs=(
            MCQ(
                question="Which angle is smaller than a right angle?",
                options=("Acute angle", "Obtuse angle", "Straight angle", "Full turn"),
                answer="A",
            ),
            MCQ(
                question="Which angle looks like the corner of a book?",
                options=("Acute angle", "Right angle", "Obtuse angle", "Reflex angle"),
                answer="B",
            ),
            MCQ(
                question="Which angle is wider than a right angle?",
                options=("Acute angle", "Zero angle", "Obtuse angle", "Half turn"),
                answer="C",
            ),
        ),
        simple_mcqs=(
            MCQ(
                question="What do we call a small angle?",
                options=("Acute angle", "Right angle", "Circle", "Line"),
                answer="A",
            ),
            MCQ(
                question="Which angle makes a square corner?",
                options=("Obtuse angle", "Right angle", "Acute angle", "Curved line"),
                answer="B",
            ),
            MCQ(
                question="Which angle is wide?",
                options=("Right angle", "Straight line", "Obtuse angle", "Point"),
                answer="C",
            ),
        ),
    ),
    TopicProfile(
        canonical_topic="Fractions",
        aliases=("fractions", "fraction", "parts of a whole"),
        keywords=("fraction", "fractions", "whole", "half", "equal"),
        rich_explanation=(
            "A fraction shows equal parts of one whole. The top number tells how "
            "many parts we have, and the bottom number tells how many equal parts "
            "make the whole."
        ),
        simple_explanation=(
            "A fraction shows parts of a whole. One half means one of two equal parts."
        ),
        rich_mcqs=(
            MCQ(
                question="What does the bottom number in a fraction show?",
                options=(
                    "How many parts are shaded",
                    "How many equal parts make the whole",
                    "The biggest piece",
                    "The answer only",
                ),
                answer="B",
            ),
            MCQ(
                question="Which fraction means one out of two equal parts?",
                options=("1/4", "2/2", "1/2", "3/2"),
                answer="C",
            ),
            MCQ(
                question="If a pizza is cut into 4 equal parts and you eat 1 part, what fraction is eaten?",
                options=("1/4", "4/1", "2/4", "3/4"),
                answer="A",
            ),
        ),
        simple_mcqs=(
            MCQ(
                question="What does a fraction show?",
                options=("Parts of a whole", "A color", "A letter", "A shape"),
                answer="A",
            ),
            MCQ(
                question="Which fraction means one half?",
                options=("1/3", "1/2", "2/3", "3/3"),
                answer="B",
            ),
            MCQ(
                question="If a cake has 4 equal parts and you take 1, what do you have?",
                options=("1/4", "4/4", "2/4", "3/4"),
                answer="A",
            ),
        ),
    ),
    TopicProfile(
        canonical_topic="States of Matter",
        aliases=("states of matter", "matter", "solid liquid gas"),
        keywords=("solid", "liquid", "gas", "matter"),
        rich_explanation=(
            "Matter is anything that takes up space, and it can be a solid, liquid, "
            "or gas. Solids keep their shape, liquids flow to fit a container, and "
            "gases spread out to fill the space around them."
        ),
        simple_explanation=(
            "Matter can be a solid, liquid, or gas. Solids keep shape, liquids pour, "
            "and gases spread out."
        ),
        rich_mcqs=(
            MCQ(
                question="Which state of matter keeps its own shape?",
                options=("Gas", "Liquid", "Solid", "Steam"),
                answer="C",
            ),
            MCQ(
                question="Which state of matter takes the shape of its container but stays together?",
                options=("Liquid", "Solid", "Rock", "Ice"),
                answer="A",
            ),
            MCQ(
                question="Which state of matter spreads out to fill a room?",
                options=("Solid", "Liquid", "Gas", "Metal"),
                answer="C",
            ),
        ),
        simple_mcqs=(
            MCQ(
                question="Which one is a solid?",
                options=("Milk", "Air", "Rock", "Steam"),
                answer="C",
            ),
            MCQ(
                question="Which one can be poured?",
                options=("Chair", "Water", "Book", "Ball"),
                answer="B",
            ),
            MCQ(
                question="Which one is a gas?",
                options=("Juice", "Air", "Ice", "Spoon"),
                answer="B",
            ),
        ),
    ),
    TopicProfile(
        canonical_topic="Parts of a Plant",
        aliases=("parts of a plant", "plant parts", "plant"),
        keywords=("plant", "root", "stem", "leaf", "flower"),
        rich_explanation=(
            "Plants have different parts that do different jobs. Roots hold the plant "
            "and take in water, the stem supports it, leaves help make food, and "
            "flowers can help make seeds."
        ),
        simple_explanation=(
            "Plants have roots, stems, leaves, and flowers. Each part helps the plant live."
        ),
        rich_mcqs=(
            MCQ(
                question="Which plant part takes in water from the soil?",
                options=("Leaf", "Flower", "Root", "Fruit"),
                answer="C",
            ),
            MCQ(
                question="Which part helps hold the plant upright?",
                options=("Stem", "Seed", "Petal", "Soil"),
                answer="A",
            ),
            MCQ(
                question="Which plant part helps make food from sunlight?",
                options=("Leaf", "Root", "Flower", "Bark"),
                answer="A",
            ),
        ),
        simple_mcqs=(
            MCQ(
                question="Which part drinks water for the plant?",
                options=("Root", "Leaf", "Flower", "Petal"),
                answer="A",
            ),
            MCQ(
                question="Which part holds the plant up?",
                options=("Stem", "Seed", "Fruit", "Soil"),
                answer="A",
            ),
            MCQ(
                question="Which part uses sunlight to help make food?",
                options=("Leaf", "Root", "Pot", "Stone"),
                answer="A",
            ),
        ),
    ),
    TopicProfile(
        canonical_topic="Multiplication",
        aliases=("multiplication", "times tables", "multiply"),
        keywords=("multiply", "multiplication", "groups", "equal"),
        rich_explanation=(
            "Multiplication is a fast way to add equal groups. If there are 3 groups "
            "with 4 apples in each group, then 3 times 4 means 12 apples altogether."
        ),
        simple_explanation=(
            "Multiplication means adding equal groups. Two groups of three make six."
        ),
        rich_mcqs=(
            MCQ(
                question="What does 3 x 4 mean?",
                options=(
                    "3 groups of 4",
                    "4 groups of 7",
                    "3 less than 4",
                    "4 more than 3",
                ),
                answer="A",
            ),
            MCQ(
                question="What is 2 x 5?",
                options=("7", "10", "12", "15"),
                answer="B",
            ),
            MCQ(
                question="Which picture matches 4 x 2?",
                options=(
                    "4 groups of 2",
                    "2 groups of 5",
                    "1 group of 8",
                    "4 groups of 4",
                ),
                answer="A",
            ),
        ),
        simple_mcqs=(
            MCQ(
                question="What does multiplication help us count?",
                options=("Equal groups", "Only letters", "Colors", "Weather"),
                answer="A",
            ),
            MCQ(
                question="What is 2 x 3?",
                options=("5", "6", "7", "8"),
                answer="B",
            ),
            MCQ(
                question="Which one means 3 groups of 2?",
                options=("3 x 2", "3 + 1", "2 - 3", "5 - 2"),
                answer="A",
            ),
        ),
    ),
)


GRADE_RULES: dict[int, dict[str, int]] = {
    1: {"max_words": 12, "max_question_words": 6},
    2: {"max_words": 14, "max_question_words": 7},
    3: {"max_words": 18, "max_question_words": 8},
    4: {"max_words": 24, "max_question_words": 9},
    5: {"max_words": 30, "max_question_words": 11},
    6: {"max_words": 34, "max_question_words": 12},
    7: {"max_words": 38, "max_question_words": 14},
    8: {"max_words": 42, "max_question_words": 16},
}


def resolve_topic_profile(topic: str) -> TopicProfile:
    normalized = normalize_topic(topic)
    for profile in TOPIC_LIBRARY:
        if normalized == normalize_topic(profile.canonical_topic):
            return profile
        if any(alias in normalized for alias in profile.aliases):
            return profile
    return build_fallback_profile(topic)


def build_fallback_profile(topic: str) -> TopicProfile:
    title = topic.strip().title()
    normalized = normalize_topic(topic)
    keyword = normalized.split(" ")[0] if normalized else "topic"
    return TopicProfile(
        canonical_topic=title,
        aliases=(normalized,),
        keywords=(keyword,),
        rich_explanation=(
            f"{title} can be learned step by step. Start with the main idea, look at "
            f"simple examples, and then practice explaining {topic.strip().lower()} "
            "in your own words."
        ),
        simple_explanation=(
            f"{title} is a topic you can learn with easy examples and practice."
        ),
        rich_mcqs=(
            MCQ(
                question=f"What is a good first step when learning {title}?",
                options=(
                    "Start with the main idea",
                    "Skip examples",
                    "Memorize random facts",
                    "Avoid practice",
                ),
                answer="A",
            ),
            MCQ(
                question=f"What helps students understand {title} better?",
                options=("Easy examples", "No questions", "Only guessing", "Silence"),
                answer="A",
            ),
            MCQ(
                question=f"What should students do after learning the main idea of {title}?",
                options=("Practice", "Forget it", "Change topic", "Stop reading"),
                answer="A",
            ),
        ),
        simple_mcqs=(
            MCQ(
                question=f"What helps you learn {title}?",
                options=("Practice", "Guessing", "Rushing", "Skipping"),
                answer="A",
            ),
            MCQ(
                question=f"What should come first in {title}?",
                options=("Main idea", "Hard quiz", "Final test", "Nothing"),
                answer="A",
            ),
            MCQ(
                question=f"What makes {title} easier?",
                options=("Examples", "Noise", "Speed only", "Random answers"),
                answer="A",
            ),
        ),
    )


def adapt_explanation_for_grade(explanation: str, grade: int) -> str:
    if grade <= 2:
        return explanation.replace("because", "so").replace("between them", "there")
    return explanation


class GeneratorAgent:
    def generate(
        self,
        grade: int,
        topic: str,
        feedback: list[str] | None = None,
    ) -> dict[str, Any]:
        profile = resolve_topic_profile(topic)
        feedback = feedback or []
        feedback_text = " ".join(feedback).lower()

        should_simplify = bool(feedback) or grade <= 3
        explanation = (
            profile.simple_explanation if should_simplify else profile.rich_explanation
        )
        explanation = adapt_explanation_for_grade(explanation, grade)

        if "too long" in feedback_text or "too complex" in feedback_text:
            explanation = profile.simple_explanation

        mcq_source = profile.simple_mcqs if should_simplify else profile.rich_mcqs
        if "question" in feedback_text or "mcq" in feedback_text:
            mcq_source = profile.simple_mcqs

        return {
            "explanation": explanation,
            "mcqs": [mcq.to_dict() for mcq in mcq_source],
        }


class ReviewerAgent:
    def review(self, request: GenerationRequest, content: dict[str, Any]) -> ReviewResult:
        feedback: list[str] = []
        grade_limits = GRADE_RULES[request.grade]
        explanation = str(content.get("explanation", "")).strip()
        mcqs = list(content.get("mcqs") or [])
        normalized_explanation = normalize_topic(explanation)
        keywords = resolve_topic_profile(request.topic).keywords

        if not explanation:
            feedback.append("Explanation is missing.")
        elif len(explanation.split()) > grade_limits["max_words"]:
            feedback.append(
                f"Explanation too long for Grade {request.grade}; keep it under "
                f"{grade_limits['max_words']} words."
            )

        if explanation.count(".") > 2:
            feedback.append(f"Use fewer sentences for Grade {request.grade}.")

        if not any(keyword in normalized_explanation for keyword in keywords):
            feedback.append("Explanation does not stay clearly focused on the topic.")

        if len(mcqs) < 3:
            feedback.append("Include at least 3 MCQs.")

        for index, mcq in enumerate(mcqs, start=1):
            question = str(mcq.get("question", "")).strip()
            options = mcq.get("options") or []
            answer = str(mcq.get("answer", "")).strip()

            if not question:
                feedback.append(f"Question {index} is missing text.")
            elif len(question.split()) > grade_limits["max_question_words"]:
                feedback.append(
                    f"Question {index} is too complex for Grade {request.grade}."
                )

            if len(options) != 4:
                feedback.append(f"Question {index} must have exactly 4 options.")

            if answer not in {"A", "B", "C", "D"}:
                feedback.append(f"Question {index} has an invalid answer key.")

        return ReviewResult(
            status="pass" if not feedback else "fail",
            feedback=feedback,
        )


class EducationalContentPipeline:
    def __init__(self) -> None:
        self.generator = GeneratorAgent()
        self.reviewer = ReviewerAgent()

    def run(self, request: GenerationRequest) -> dict[str, Any]:
        generated = self.generator.generate(request.grade, request.topic)
        review = self.reviewer.review(request, generated)
        refined_output: dict[str, Any] | None = None

        if review.status == "fail":
            refined = self.generator.generate(
                request.grade,
                request.topic,
                feedback=review.feedback,
            )
            # One refinement pass only, as requested in the assessment.
            refined_output = refined

        return {
            "generator_output": generated,
            "reviewer_output": review.to_dict(),
            "refined_output": refined_output,
        }


PIPELINE = EducationalContentPipeline()


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TwinMind AI Educational Content Generator & Reviewer</title>
  <style>
    :root {
      --paper: #f7f3ea;
      --ink: #15243a;
      --muted: #52627d;
      --teal: #1d7f7a;
      --teal-soft: rgba(29, 127, 122, 0.14);
      --sun: #e59c2e;
      --rose: #c45b4d;
      --panel: rgba(255, 255, 255, 0.82);
      --border: rgba(21, 36, 58, 0.12);
      --shadow: 0 24px 60px rgba(18, 29, 47, 0.12);
      --radius: 24px;
    }

    * { box-sizing: border-box; }

    html {
      scroll-behavior: smooth;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Trebuchet MS", "Gill Sans", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(229, 156, 46, 0.18), transparent 32%),
        radial-gradient(circle at bottom right, rgba(29, 127, 122, 0.22), transparent 28%),
        linear-gradient(135deg, #f4efe2 0%, #f6f0e8 52%, #efe8dc 100%);
      padding: 28px;
    }

    .shell {
      max-width: 1180px;
      margin: 0 auto;
      display: grid;
      gap: 22px;
    }

    .hero, .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }

    .hero {
      position: relative;
      padding: 28px 30px;
      overflow: hidden;
    }

    .hero::after {
      content: "";
      position: absolute;
      top: -80px;
      right: -60px;
      width: 260px;
      height: 260px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(29, 127, 122, 0.14), transparent 68%);
      pointer-events: none;
    }

    .hero-grid {
      position: relative;
      z-index: 1;
      display: grid;
      grid-template-columns: minmax(0, 1.45fr) minmax(300px, 0.95fr);
      gap: 26px;
      align-items: center;
    }

    .hero-copy {
      display: grid;
      gap: 14px;
      align-content: start;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      width: fit-content;
      padding: 9px 14px;
      border-radius: 999px;
      background: var(--teal-soft);
      color: var(--teal);
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      font-size: 0.8rem;
    }

    h1, h2, h3 {
      margin: 0;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
    }

    h1 {
      font-size: clamp(2.3rem, 4.8vw, 4.4rem);
      line-height: 0.92;
      letter-spacing: -0.04em;
      max-width: 9.5ch;
    }

    .hero p {
      margin: 0;
      color: var(--muted);
      max-width: 58ch;
      font-size: 1rem;
      line-height: 1.58;
    }

    .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 4px;
    }

    .hero-link,
    .hero-link-secondary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 46px;
      padding: 12px 18px;
      border-radius: 999px;
      text-decoration: none;
      font-weight: 700;
      transition: transform 180ms ease, background 180ms ease, box-shadow 180ms ease;
    }

    .hero-link {
      color: white;
      background: linear-gradient(135deg, var(--teal), #166a66);
      box-shadow: 0 12px 24px rgba(29, 127, 122, 0.18);
    }

    .hero-link-secondary {
      color: var(--ink);
      background: rgba(21, 36, 58, 0.05);
      border: 1px solid var(--border);
    }

    .hero-link:hover,
    .hero-link-secondary:hover {
      transform: translateY(-1px);
    }

    .hero-side {
      display: grid;
      gap: 14px;
    }

    .hero-kpis {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }

    .hero-kpi,
    .hero-card {
      border-radius: 20px;
      border: 1px solid var(--border);
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(247, 243, 234, 0.82));
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75);
    }

    .hero-kpi {
      padding: 14px;
    }

    .hero-kpi strong {
      display: block;
      margin-bottom: 6px;
      font-size: 1.35rem;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
    }

    .hero-kpi span {
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.4;
    }

    .hero-card {
      padding: 18px;
    }

    .hero-card h3 {
      margin-bottom: 12px;
      font-size: 1.05rem;
    }

    .hero-mini-flow {
      display: grid;
      gap: 12px;
    }

    .hero-mini-item {
      display: grid;
      grid-template-columns: 32px 1fr;
      gap: 12px;
      align-items: start;
    }

    .hero-step {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: rgba(29, 127, 122, 0.14);
      color: var(--teal);
      font-weight: 800;
    }

    .hero-mini-item strong {
      display: block;
      margin-bottom: 3px;
      font-size: 0.98rem;
    }

    .hero-mini-item p {
      margin: 0;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.45;
    }

    .layout {
      display: grid;
      grid-template-columns: 360px minmax(0, 1fr);
      gap: 22px;
      align-items: start;
    }

    .panel {
      padding: 24px;
      scroll-margin-top: 18px;
    }
    .form-grid, .results, .stack, .flow { display: grid; gap: 16px; }

    label {
      display: grid;
      gap: 8px;
      font-weight: 700;
      color: var(--ink);
    }

    input, select, button { font: inherit; }

    input, select {
      width: 100%;
      border: 1px solid rgba(21, 36, 58, 0.14);
      border-radius: 16px;
      padding: 14px 16px;
      background: rgba(255, 255, 255, 0.92);
      color: var(--ink);
    }

    input:focus, select:focus {
      outline: 3px solid rgba(29, 127, 122, 0.2);
      border-color: var(--teal);
    }

    .topic-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .chip {
      border: none;
      border-radius: 999px;
      padding: 10px 14px;
      background: rgba(21, 36, 58, 0.06);
      color: var(--ink);
      cursor: pointer;
      transition: transform 140ms ease, background 140ms ease;
    }

    .chip:hover {
      transform: translateY(-1px);
      background: rgba(29, 127, 122, 0.14);
    }

    .primary-btn {
      border: none;
      border-radius: 18px;
      padding: 14px 18px;
      background: linear-gradient(135deg, var(--teal), #166a66);
      color: white;
      font-weight: 700;
      cursor: pointer;
      transition: transform 180ms ease, box-shadow 180ms ease;
      box-shadow: 0 12px 24px rgba(29, 127, 122, 0.22);
    }

    .primary-btn:hover { transform: translateY(-1px); }

    .note {
      font-size: 0.93rem;
      color: var(--muted);
      line-height: 1.5;
      margin: 0;
    }

    .flow-step {
      position: relative;
      border-radius: 18px;
      padding: 16px;
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(247, 243, 234, 0.82));
      border: 1px solid var(--border);
    }

    .flow-step + .flow-step::before {
      content: "";
      position: absolute;
      top: -16px;
      left: 28px;
      width: 2px;
      height: 16px;
      background: linear-gradient(180deg, rgba(21, 36, 58, 0.12), rgba(29, 127, 122, 0.4));
    }

    .flow-step strong {
      display: block;
      margin-bottom: 6px;
      font-size: 1rem;
    }

    .flow-step span {
      color: var(--muted);
      font-size: 0.95rem;
      line-height: 1.5;
    }

    .results-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 14px;
      border-radius: 999px;
      font-weight: 700;
    }

    .status-pass {
      background: rgba(29, 127, 122, 0.14);
      color: var(--teal);
    }

    .status-fail {
      background: rgba(196, 91, 77, 0.14);
      color: var(--rose);
    }

    .card {
      border-radius: 20px;
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.74);
      overflow: hidden;
    }

    .card header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 16px 18px;
      border-bottom: 1px solid var(--border);
      background: rgba(247, 243, 234, 0.8);
    }

    .card header p {
      margin: 0;
      color: var(--muted);
      font-size: 0.92rem;
    }

    pre {
      margin: 0;
      padding: 18px;
      overflow-x: auto;
      background: rgba(18, 29, 47, 0.97);
      color: #edf6ff;
      font: 0.92rem/1.6 "Consolas", "Courier New", monospace;
    }

    .empty {
      padding: 22px;
      border-radius: 20px;
      border: 1px dashed rgba(21, 36, 58, 0.18);
      background: rgba(255, 255, 255, 0.46);
      color: var(--muted);
      line-height: 1.6;
    }

    .loading, .error { font-weight: 700; }
    .loading { color: var(--teal); }
    .error { color: var(--rose); }

    @media (max-width: 960px) {
      body { padding: 16px; }
      .hero-grid { grid-template-columns: 1fr; }
      .hero-kpis { grid-template-columns: 1fr 1fr 1fr; }
      .layout { grid-template-columns: 1fr; }
      .hero, .panel { padding: 20px; }
      h1 {
        max-width: 11ch;
        font-size: clamp(2.2rem, 11vw, 3.6rem);
      }
    }

    @media (max-width: 640px) {
      .hero-kpis { grid-template-columns: 1fr; }
      .hero-actions {
        display: grid;
        grid-template-columns: 1fr;
      }
      .hero-link,
      .hero-link-secondary {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="hero-grid">
        <div class="hero-copy">
          <div class="eyebrow">TwinMind Assessment Submission</div>
          <h1>Two clear AI agents, one visible workflow.</h1>
          <p>
            The Generator Agent writes the first draft. The Reviewer Agent checks
            grade-fit, clarity, and correctness. If needed, the app runs one
            focused rewrite and shows every step on screen.
          </p>
          <div class="hero-actions">
            <a class="hero-link" href="#pipeline-panel">Start With Input</a>
            <a class="hero-link-secondary" href="#output-panel">Jump to Output</a>
          </div>
        </div>

        <div class="hero-side">
          <div class="hero-kpis">
            <div class="hero-kpi">
              <strong>2</strong>
              <span>Explicit AI agents</span>
            </div>
            <div class="hero-kpi">
              <strong>1</strong>
              <span>Refinement pass maximum</span>
            </div>
            <div class="hero-kpi">
              <strong>JSON</strong>
              <span>Structured input and output</span>
            </div>
          </div>

          <div class="hero-card">
            <h3>What you will see</h3>
            <div class="hero-mini-flow">
              <div class="hero-mini-item">
                <span class="hero-step">1</span>
                <div>
                  <strong>Input</strong>
                  <p>Choose a grade and topic.</p>
                </div>
              </div>
              <div class="hero-mini-item">
                <span class="hero-step">2</span>
                <div>
                  <strong>Generation</strong>
                  <p>The first draft appears in structured JSON.</p>
                </div>
              </div>
              <div class="hero-mini-item">
                <span class="hero-step">3</span>
                <div>
                  <strong>Review</strong>
                  <p>The evaluator returns <code>pass</code> or <code>fail</code> with feedback.</p>
                </div>
              </div>
              <div class="hero-mini-item">
                <span class="hero-step">4</span>
                <div>
                  <strong>Refinement</strong>
                  <p>If needed, the generator tries one more time.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="layout">
      <aside id="pipeline-panel" class="panel">
        <div class="form-grid">
          <div>
            <h2>Run the pipeline</h2>
            <p class="note">Pick a grade, enter a topic, and see the exact agent flow the assignment asks for.</p>
          </div>

          <label>
            Grade
            <select id="grade">
              <option value="1">Grade 1</option>
              <option value="2">Grade 2</option>
              <option value="3">Grade 3</option>
              <option value="4" selected>Grade 4</option>
              <option value="5">Grade 5</option>
              <option value="6">Grade 6</option>
              <option value="7">Grade 7</option>
              <option value="8">Grade 8</option>
            </select>
          </label>

          <label>
            Topic
            <input id="topic" type="text" value="Types of angles" placeholder="Example: Fractions" />
          </label>

          <div>
            <div class="note" style="margin-bottom: 10px;">Quick picks</div>
            <div class="topic-chips">
              <button class="chip" data-topic="Types of angles" type="button">Types of angles</button>
              <button class="chip" data-topic="Fractions" type="button">Fractions</button>
              <button class="chip" data-topic="States of matter" type="button">States of matter</button>
              <button class="chip" data-topic="Parts of a plant" type="button">Parts of a plant</button>
              <button class="chip" data-topic="Multiplication" type="button">Multiplication</button>
            </div>
          </div>

          <button id="run-btn" class="primary-btn" type="button">Generate, Review, Refine</button>

          <div class="flow">
            <div class="flow-step">
              <strong>1. Generator Agent</strong>
              <span>Takes structured input and creates an explanation with MCQs.</span>
            </div>
            <div class="flow-step">
              <strong>2. Reviewer Agent</strong>
              <span>Checks age appropriateness, conceptual correctness, and clarity.</span>
            </div>
            <div class="flow-step">
              <strong>3. Refinement Pass</strong>
              <span>Runs only once if the reviewer returns <code>fail</code>.</span>
            </div>
            <div class="flow-step">
              <strong>4. Visible UI Flow</strong>
              <span>Shows input, generator output, reviewer feedback, and refined output if needed.</span>
            </div>
          </div>
        </div>
      </aside>

      <section id="output-panel" class="panel results">
        <div class="results-header">
          <div>
            <h2>Pipeline Output</h2>
            <p class="note">The cards below match the required generator output, reviewer output, and refined output.</p>
          </div>
          <div id="status-slot"></div>
        </div>
        <div id="results-root" class="empty">
          Submit a topic to see the structured input, generator output, reviewer feedback, and refined output.
        </div>
      </section>
    </section>
  </main>

  <script>
    const topicInput = document.getElementById("topic");
    const gradeInput = document.getElementById("grade");
    const runButton = document.getElementById("run-btn");
    const resultsRoot = document.getElementById("results-root");
    const statusSlot = document.getElementById("status-slot");

    document.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        topicInput.value = chip.dataset.topic;
      });
    });

    function badge(status, label) {
      const css = status === "pass" ? "status-badge status-pass" : "status-badge status-fail";
      return `<span class="${css}">${label}</span>`;
    }

    function card(title, subtitle, payload, status = null) {
      const statusHtml = status ? badge(status, status.toUpperCase()) : "";
      return `
        <article class="card">
          <header>
            <div>
              <h3>${title}</h3>
              <p>${subtitle}</p>
            </div>
            ${statusHtml}
          </header>
          <pre>${JSON.stringify(payload, null, 2)}</pre>
        </article>
      `;
    }

    async function runPipeline() {
      const payload = {
        grade: Number(gradeInput.value),
        topic: topicInput.value.trim()
      };

      resultsRoot.innerHTML = `<div class="loading">Running generator and reviewer agents...</div>`;
      statusSlot.innerHTML = "";
      runButton.disabled = true;

      try {
        const response = await fetch("/api/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Request failed.");

        const reviewStatus = data.reviewer_output.status;
        statusSlot.innerHTML = badge(
          reviewStatus,
          reviewStatus === "pass" ? "Ready on first pass" : "Refinement triggered"
        );

        const cards = [
          card("Input", "Structured input sent into the Generator Agent.", payload),
          card("Generator Output", "Deterministic explanation plus MCQs.", data.generator_output),
          card("Reviewer Output", "Feedback from the evaluator agent.", data.reviewer_output, data.reviewer_output.status)
        ];

        if (data.refined_output) {
          cards.push(
            card("Refined Output", "Single retry using reviewer feedback.", data.refined_output)
          );
        }

        resultsRoot.innerHTML = `<div class="stack">${cards.join("")}</div>`;
        document.getElementById("output-panel").scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      } catch (error) {
        resultsRoot.innerHTML = `<div class="error">${error.message}</div>`;
        statusSlot.innerHTML = badge("fail", "Pipeline error");
        document.getElementById("output-panel").scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      } finally {
        runButton.disabled = false;
      }
    }

    runButton.addEventListener("click", runPipeline);
  </script>
</body>
</html>
"""


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path not in {"/", "/index.html"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        body = HTML_PAGE.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/api/run":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
            request = GenerationRequest.from_payload(payload)
            result = PIPELINE.run(request)
            self.respond_json(HTTPStatus.OK, result)
        except ValueError as error:
            self.respond_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
        except json.JSONDecodeError:
            self.respond_json(HTTPStatus.BAD_REQUEST, {"error": "Body must be valid JSON."})
        except Exception as error:  # pragma: no cover
            self.respond_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": f"Unexpected server error: {error}"},
            )

    def log_message(self, format: str, *args: Any) -> None:
        return

    def respond_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(f"Serving TwinMind assessment app at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
