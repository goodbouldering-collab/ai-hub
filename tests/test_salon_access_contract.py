from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ACCESS_SOURCE = (ROOT / "api" / "square" / "ai-salon-access.ts").read_text(
    encoding="utf-8"
)
SQUARE_SOURCE = (ROOT / "api" / "_lib" / "square.ts").read_text(encoding="utf-8")


class SalonAccessContractTests(unittest.TestCase):
    def test_password_is_rendered_only_by_the_paid_access_handler(self) -> None:
        self.assertIn("LINE参加パスワード", ACCESS_SOURCE)
        self.assertIn(
            "renderAccess(res, salonOpenChatUrl(), salonOpenChatPassword())",
            ACCESS_SOURCE,
        )
        self.assertIn('order?.state === "COMPLETED"', ACCESS_SOURCE)
        self.assertNotRegex(ACCESS_SOURCE, r'renderAccess\([^)]*["\']\d{4,8}')

    def test_password_comes_from_a_validated_server_environment_variable(self) -> None:
        self.assertIn(
            'requiredSquareEnv("AI_SALON_OPENCHAT_PASSWORD")',
            SQUARE_SOURCE,
        )
        self.assertIn("/^[0-9]{4,8}$/", SQUARE_SOURCE)
        self.assertNotRegex(SQUARE_SOURCE, r'const password\s*=\s*["\']\d{4,8}')


if __name__ == "__main__":
    unittest.main()
