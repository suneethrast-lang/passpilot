
import unittest

from backend.services.validators import validate_documents


class ValidatorTests(unittest.TestCase):

    def test_matching_documents(self):
        result = validate_documents({
            "case_id": "TEST-001",
            "documents": [
                {
                    "type": "identity",
                    "fields": {
                        "name": "Arjun Kumar",
                        "date_of_birth": "2005-04-12",
                    },
                },
                {
                    "type": "address",
                    "fields": {
                        "name": "ARJUN KUMAR",
                        "date_of_birth": "2005-04-12",
                    },
                },
            ],
        })

        self.assertEqual(result["checks"][0]["status"], "match")
        self.assertEqual(result["checks"][1]["status"], "match")
        self.assertFalse(result["requires_human_review"])

    def test_name_mismatch(self):
        result = validate_documents({
            "documents": [
                {"type": "identity", "fields": {"name": "Arjun Kumar"}},
                {"type": "address", "fields": {"name": "Arjun Raj"}},
            ],
        })

        self.assertEqual(
            result["checks"][0]["status"],
            "review_required",
        )
        self.assertTrue(result["requires_human_review"])

    def test_missing_information(self):
        result = validate_documents({
            "documents": [
                {"type": "identity", "fields": {"name": "Arjun Kumar"}},
            ],
        })

        self.assertEqual(
            result["checks"][0]["status"],
            "insufficient_data",
        )

    def test_invalid_date_is_not_accepted(self):
        result = validate_documents({
            "documents": [
                {
                    "type": "identity",
                    "fields": {
                        "date_of_birth": "2005-02-30",
                    },
                },
                {
                    "type": "address",
                    "fields": {
                        "date_of_birth": "2005-02-30",
                    },
                },
            ],
        })

        self.assertEqual(
            result["checks"][1]["status"],
            "insufficient_data",
        )


if __name__ == "__main__":
    unittest.main()
