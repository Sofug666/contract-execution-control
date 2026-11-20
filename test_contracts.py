from pathlib import Path
import subprocess
import sys
from uuid import uuid4
import unittest


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.registry = Path.cwd() / f"test-registry-{uuid4().hex}.json"
        self.addCleanup(self.registry.unlink, missing_ok=True)

    def run_cli(self, *args, expected=0):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(Path(__file__).with_name("contracts.py")),
             "--file", str(self.registry), *args],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, expected, result.stderr)
        return result.stdout, result.stderr

    def test_empty_registry(self):
        output, _ = self.run_cli("report")
        self.assertIn("Реестр пуст", output)

    def test_deadline_boundaries_and_completion(self):
        self.run_cli("add-contract", "D-01", "Учебный поставщик")
        self.run_cli("add-obligation", "D-01", "O-01", "Передача отчёта", "Роль A", "2026-11-20")
        for day, status in [("19", "В работе"), ("20", "Срок сегодня"), ("21", "Просрочено")]:
            with self.subTest(day=day):
                output, _ = self.run_cli("report", "--as-of", "2026-11-" + day)
                self.assertIn(status, output)
        self.run_cli("close", "D-01", "O-01")
        output, _ = self.run_cli("report", "--as-of", "2026-11-21")
        self.assertIn("Выполнено", output)
        _, error = self.run_cli("close", "D-01", "O-01", expected=2)
        self.assertIn("уже выполнено", error)

    def test_duplicate_contract(self):
        self.run_cli("add-contract", "D-01", "Первая запись")
        _, error = self.run_cli("add-contract", "D-01", "Вторая запись", expected=2)
        self.assertIn("уже существует", error)
        output, _ = self.run_cli("report")
        self.assertIn("Первая запись", output)
        self.assertNotIn("Вторая запись", output)

    def test_unknown_contract_and_invalid_date(self):
        _, error = self.run_cli("close", "D-99", "O-01", expected=2)
        self.assertIn("Договор не найден", error)
        _, error = self.run_cli("report", "--as-of", "2026-02-30", expected=2)
        self.assertIn("Укажите дату", error)


if __name__ == "__main__":
    unittest.main()
