import unittest

from app import EducationalContentPipeline, GenerationRequest, ReviewerAgent


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = EducationalContentPipeline()
        self.reviewer = ReviewerAgent()

    def test_grade_four_angles_triggers_refinement_and_passes(self) -> None:
        request = GenerationRequest(grade=4, topic="Types of angles")

        result = self.pipeline.run(request)
        refined_review = self.reviewer.review(request, result["refined_output"])

        self.assertEqual(result["reviewer_output"]["status"], "fail")
        self.assertIsNotNone(result["refined_output"])
        self.assertEqual(refined_review.status, "pass")

    def test_pipeline_returns_exact_top_level_shape(self) -> None:
        request = GenerationRequest(grade=4, topic="Fractions")

        result = self.pipeline.run(request)

        self.assertEqual(
            set(result.keys()),
            {"generator_output", "reviewer_output", "refined_output"},
        )
        self.assertEqual(
            set(result["generator_output"].keys()),
            {"explanation", "mcqs"},
        )
        self.assertEqual(
            set(result["reviewer_output"].keys()),
            {"status", "feedback"},
        )

    def test_reviewer_flags_long_explanation(self) -> None:
        request = GenerationRequest(grade=2, topic="Fractions")
        content = {
            "explanation": "Fractions are mathematical ideas that show several equal parts of one whole object and often require careful comparisons.",
            "mcqs": [
                {
                    "question": "Which one means one half exactly?",
                    "options": ["1/3", "1/2", "2/3", "3/3"],
                    "answer": "B",
                },
                {
                    "question": "Which number tells the total equal parts in the whole fraction model?",
                    "options": ["Top number", "Bottom number", "Both numbers", "No number"],
                    "answer": "B",
                },
                {
                    "question": "Which one is a fraction?",
                    "options": ["1/2", "A", "Blue", "Circle"],
                    "answer": "A",
                },
            ],
        }

        review = self.reviewer.review(request, content)

        self.assertEqual(review.status, "fail")
        self.assertTrue(
            any("too long" in item.lower() for item in review.feedback),
            review.feedback,
        )


if __name__ == "__main__":
    unittest.main()
