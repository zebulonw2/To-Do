"""
Unit Test for main.py
"""
import unittest
import peewee as pw
import pytest
import validator
import main
import errors
from models import ContributorsDB, TasksDb

MODELS = (ContributorsDB, TasksDb)
test_db = pw.SqliteDatabase(":memory:")


class TestValidator(unittest.TestCase):
    """Tests Validation Methods"""

    def test_start_good(self):
        self.assertEqual(validator.val_start("2022-06-06"), True)

    def test_start_bad(self):
        with pytest.raises(errors.DateFormatError) as error:
            self.assertEqual(validator.val_start("022-06-06"),
                             str(error.value))
            self.assertEqual(validator.val_start("2022_06_06"),
                             str(error.value))

    def test_due_good(self):
        self.assertEqual(validator.val_due("2022-06-06", "2022-06-05"), True)

    def test_due_bad(self):
        with pytest.raises(errors.DateFormatError) as error:
            self.assertEqual(validator.val_due("022-06-06", "2022-01-01"),
                             str(error.value))
            self.assertEqual(validator.val_due("2022_06_06", "2022-01-01"),
                             str(error.value))

    def test_due_before_start(self):
        with pytest.raises(errors.DateFormatError) as error:
            self.assertEqual(validator.val_due("2022-06-05", "2022-06-06"),
                             str(error.value))

    def test_priority_good(self):
        self.assertEqual(validator.val_priority("high"), True)
        self.assertEqual(validator.val_priority("HIGH"), True)
        self.assertEqual(validator.val_priority("High"), True)
        self.assertEqual(validator.val_priority("low"), True)
        self.assertEqual(validator.val_priority("medium"), True)

    def test_priority_bad(self):
        with pytest.raises(errors.PriorityError) as error:
            self.assertEqual(validator.val_priority(""),
                             str(error.value))


class TestMain(unittest.TestCase):
    """Tests Functions from Main"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)

    def test_add_contributor(self):
        """Test Adding Contributor"""
        start_len = len(ContributorsDB)
        self.assertEqual(main.add_contributor("zeb", "tester"), True)
        end_len = len(ContributorsDB)
        assert end_len - start_len == 1

    def test_add_task(self):
        """Test Adding Status"""
        start_len = len(TasksDb)
        self.assertEqual(main.add_task("zeb", "write tests", "test description", "high",
                                                 "2020-01-01", "2022-01-01"), True)
        end_len = len(TasksDb)
        assert end_len - start_len == 1

    def test_add_task_no_contributor(self):
        self.assertEqual(main.add_task("", "write tests", "test description", "high",
                                                 "2020-01-01", "2022-01-01"), False)

    def test_update_name(self):
        self.assertEqual(main.update_task("1"), True)

    def test_update_description(self):
        pass

    def test_update_not_exist(self):
        pass

    def test_mark_complete(self):
        self.assertEqual(main.mark_task_complete("1"), True)

    def test_mark_complete_not_exist(self):
        with pytest.raises(TasksDb.DoesNotExist) as error:
            self.assertEqual(main.mark_task_complete(""), str(error.value))

    def test_delete_task(self):
        self.assertEqual(main.delete_task("1"), True)

    def test_delete_contributor(self):
        self.assertEqual(main.delete_contributor("zeb"), True)

    def test_delete_contributor_not_exist(self):
        with pytest.raises(ContributorsDB.DoesNotExist) as error:
            self.assertEqual(main.delete_contributor(""), str(error.value))

    def test_delete_not_exists(self):
        with pytest.raises(TasksDb.DoesNotExist) as error:
            self.assertEqual(main.delete_task(""), str(error.value))

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


if __name__ == "__main__":
    unittest.main()
