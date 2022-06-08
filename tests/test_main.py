"""
Unit Test for main.py
"""
import unittest

import loguru
import peewee as pw
import pytest
import src.validator
import src.main
import src.errors
from src.models import ContributorsDB, TasksDb
from unittest.mock import patch
import sys

MODELS = (ContributorsDB, TasksDb)
test_db = pw.SqliteDatabase(":memory:")


class TestValidator(unittest.TestCase):  # todo make sure all are tested
    """Tests Validation Methods"""

    def test_sys_args_good(self):
        args = ["main", "add_contributor", "zeb", "tester"]
        with patch.object(sys, 'argv', args):
            self.assertEqual(src.validator.val_sys_args(args[1:]), True)

    def test_sys_args_missing_args(self):
        args = ["main", "add_contributor"]
        with patch.object(sys, 'argv', args):
            with pytest.raises(SystemExit) as error:
                self.assertEqual(src.validator.val_sys_args(args[1:]), str(error.value))

    def test_sys_args_no_method(self):
        args = ["main"]
        with patch.object(sys, 'argv', args):
            with pytest.raises(SystemExit) as error:
                self.assertEqual(src.validator.val_sys_args(args[1:]), str(error.value))

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
            self.assertEqual(src.validator.val_priority("low p"),
                             str(error.value))
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
        row = src.main.add_contributor("zeb", "tester")
        assert row.NAME == "zeb"

    def test_add_contributor_already_exists(self):
        row = src.main.add_contributor("zeb", "tester")
        assert row.NAME == "zeb"
        with pytest.raises(pw.IntegrityError) as error:
            self.assertEqual(src.main.add_contributor("zeb", "tester"), str(error.value))

    def test_add_task(self):
        """Test Adding Status"""
        src.main.add_contributor("zeb", "tester")
        row = src.main.add_task("zeb", "write tests", "test description", "high",
                                "2020-01-01", "2022-01-01")
        assert row.NAME == 'write tests'

    def test_add_task_no_contributor(self):
        with pytest.raises(ContributorsDB.DoesNotExist) as error:
            self.assertEqual(src.main.add_task("", "write tests", "test description", "high",
                                               "2020-01-01", "2022-01-01"), str(error.value))

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
        task = TasksDb.get(TasksDb.NUM == "1")
        print(task.NAME, task.DESCRIPTION, task.PRIORITY)

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
        row = src.main.mark_task_complete("1")
        assert row.FINISHED is True

    def test_mark_complete_not_exist(self):
        with pytest.raises(TasksDb.DoesNotExist) as error:
            self.assertEqual(src.main.mark_task_complete(""), str(error.value))

    def test_delete_task(self):
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "write tests", "test description", "high",
                          "2020-01-01", "2022-01-01")
        row = src.main.delete_task("1")
        assert row.DELETED is True

    def test_delete_contributor_no_task(self):
        src.main.add_contributor("zeb", "tester")
        self.assertEqual(src.main.delete_contributor("zeb"), True)

    def test_delete_contributor_with_task(self):
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "write tests", "test description", "high",
                          "2020-01-01", "2022-01-01")
        row = src.main.delete_contributor("zeb")

    def test_delete_contributor_not_exist(self):
        with pytest.raises(ContributorsDB.DoesNotExist) as error:
            self.assertEqual(src.main.delete_contributor(""), str(error.value))

    def test_delete_not_exists(self):
        with pytest.raises(TasksDb.DoesNotExist) as error:
            self.assertEqual(src.main.delete_task(""), str(error.value))

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


class TestList(unittest.TestCase):
    """Tests Listing Function"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)
        src.main.add_contributor("john", "writer")
        src.main.add_contributor("zeb", "tester")
        src.main.add_task("zeb", "c test", "a description", "low pri",
                          "2021-01-01", "2023-01-01")
        src.main.add_task("zeb", "a test", "another description", "medium",
                          "2020-01-02", "2022-01-02")
        src.main.add_task("john", "b test", "test description", "high",
                          "2020-01-03", "2022-01-03")
        src.main.mark_task_complete("2")
        src.main.delete_task("2")

    def test_list_default(self):
        task_list = src.main.list_tasks()
        first_row = task_list[0]
        assert first_row[0] == "1"

    def test_list_num(self):
        task_list = src.main.list_tasks(sort="Num")
        first_row = task_list[0]
        assert first_row[0] == "1"

    def test_list_owner(self):
        task_list = src.main.list_tasks(sort="Owner")
        first_row = task_list[0]
        assert first_row[1] == "john"

    def test_list_name(self):
        task_list = src.main.list_tasks(sort="Name")
        first_row = task_list[0]
        assert first_row[2] == "a test"

    def test_list_priority(self):  # todo get values to update
        task_list = src.main.list_tasks(sort="Priority")
        first_row = task_list[0]
        assert first_row[3] == "low"

    def test_list_start(self):
        task_list = src.main.list_tasks(sort="Start")
        first_row = task_list[0]
        assert first_row[5] == "2020-01-02"

    def test_list_due(self):
        task_list = src.main.list_tasks(sort="Due")
        first_row = task_list[0]
        assert first_row[6] == "2022-01-02"

    def test_list_finished(self):
        task_list = src.main.list_tasks(sort="Finished")
        first_row = task_list[0]
        assert first_row[7] is False

    def test_list_deleted(self):
        task_list = src.main.list_tasks(sort="Deleted")
        first_row = task_list[0]
        assert first_row[8] is False

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


if __name__ == "__main__":
    unittest.main()
