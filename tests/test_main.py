"""
Unit Test for main.py
"""
import unittest
import peewee as pw
import pytest
import src.validator
import src.main
import src.errors
from src.models import ContributorsDB, TasksDb

MODELS = (ContributorsDB, TasksDb)
test_db = pw.SqliteDatabase(":memory:")


class TestValidator(unittest.TestCase):
    """Tests Validation Methods"""

    def test_start_good(self):
        self.assertEqual(src.validator.val_start("2022-06-06"), True)

    def test_start_bad(self):
        with pytest.raises(src.errors.DateFormatError) as error:
            self.assertEqual(src.validator.val_start("022-06-06"),
                             str(error.value))
            self.assertEqual(src.validator.val_start("2022_06_06"),
                             str(error.value))

    def test_due_good(self):
        self.assertEqual(src.validator.val_due("2022-06-06", "2022-06-05"), True)

    def test_due_bad(self):
        with pytest.raises(src.errors.DateFormatError) as error:
            self.assertEqual(src.validator.val_due("022-06-06", "2022-01-01"),
                             str(error.value))
            self.assertEqual(src.validator.val_due("2022_06_06", "2022-01-01"),
                             str(error.value))

    def test_due_before_start(self):
        with pytest.raises(src.errors.DateFormatError) as error:
            self.assertEqual(src.validator.val_due("2022-06-05", "2022-06-06"),
                             str(error.value))

    def test_priority_good(self):
        self.assertEqual(src.validator.val_priority("high"), True)
        self.assertEqual(src.validator.val_priority("HIGH"), True)
        self.assertEqual(src.validator.val_priority("High"), True)
        self.assertEqual(src.validator.val_priority("low"), True)
        self.assertEqual(src.validator.val_priority("medium"), True)

    def test_priority_bad(self):
        with pytest.raises(src.errors.PriorityError) as error:
            self.assertEqual(src.validator.val_priority(""),
                             str(error.value))


class TestMain(unittest.TestCase):
    """Tests Functions from Main"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)

    def test_add_contributor(self):
        """Test Adding Contributor"""
        self.assertEqual(src.main.add_contributor("zeb", "tester"), True)

    def test_add_task(self):
        """Test Adding Status"""
        src.main.add_contributor("zeb", "tester")
        self.assertEqual(src.main.add_task("zeb", "write tests", "test description", "high",
                                           "2020-01-01", "2022-01-01"), True)

    def test_add_task_no_contributor(self):
        self.assertEqual(src.main.add_task("", "write tests", "test description", "high",
                                           "2020-01-01", "2022-01-01"), False)

    def test_update_name(self):
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "write tests", "test description", "high",
                          "2020-01-01", "2022-01-01")
        self.assertEqual(src.main.update_task("1", task_name="write more tests"), True)

    def test_update_description(self):
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "test name", "test description", "high",
                          "2020-01-01", "2022-01-01")
        self.assertEqual(src.main.update_task("1", task_description="new description"), True)

    def test_update_priority_good(self):
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "test name", "test description", "high",
                          "2020-01-01", "2022-01-01")
        self.assertEqual(src.main.update_task("1", priority="low"), True)

    def test_update_priority_bad(self):
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "test name", "test description", "high",
                          "2020-01-01", "2022-01-01")
        with pytest.raises(src.errors.PriorityError) as error:
            self.assertEqual(src.main.update_task("1", priority=" "), str(error.value))

    def test_update_all(self):
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "write tests", "test description", "high",
                          "2020-01-01", "2022-01-01")
        self.assertEqual(src.main.update_task(
            "1", task_name="new_name", task_description="new_description", priority="low"), True)

    def test_update_not_exist(self):
        self.assertEqual(src.main.update_task("2", task_name=""), False)

    def test_mark_complete(self):
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "write tests", "test description", "high",
                          "2020-01-01", "2022-01-01")
        self.assertEqual(src.main.mark_task_complete("1"), True)

    def test_mark_complete_not_exist(self):
        with pytest.raises(TasksDb.DoesNotExist) as error:
            self.assertEqual(src.main.mark_task_complete(""), str(error.value))

    def test_delete_task(self):
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "write tests", "test description", "high",
                          "2020-01-01", "2022-01-01")
        self.assertEqual(src.main.delete_task("1"), True)

    def test_delete_contributor_no_task(self):
        src.main.add_contributor("zeb", "tester")
        self.assertEqual(src.main.delete_contributor("zeb"), True)

    def test_delete_contributor_with_task(self):
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "write tests", "test description", "high",
                          "2020-01-01", "2022-01-01")
        self.assertEqual(src.main.delete_contributor("zeb"), True)

    def test_delete_contributor_not_exist(self):
        with pytest.raises(ContributorsDB.DoesNotExist) as error:
            self.assertEqual(src.main.delete_contributor(""), str(error.value))

    def test_delete_not_exists(self):
        with pytest.raises(TasksDb.DoesNotExist) as error:
            self.assertEqual(src.main.delete_task(""), str(error.value))

    def test_list_num(self):
        src.main.add_contributor("john", "writer")
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("john", "write code", "test description", "high",
                          "2020-01-01", "2022-01-01")
        src.main.add_task("zeb", "write tests", "test description", "low",
                          "2020-01-02", "2022-01-02")
        src.main.mark_task_complete("2")
        src.main.delete_task("2")
        self.assertEqual(src.main.list_tasks(sort_field="num"), True)

    def test_list_name(self):
        pass

    def test_list_bad(self):
        pass

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


if __name__ == "__main__":
    unittest.main()
