"""
Unit Test for main.py
"""
import sys
import unittest
from unittest.mock import patch

import loguru
import peewee as pw
import pytest

import main
import errors
import validator
from models import ContributorsDB, TasksDb

MODELS = (ContributorsDB, TasksDb)
test_db = pw.SqliteDatabase(":memory:")


class TestValidator(unittest.TestCase):
    """Tests Validation Methods"""

    def test_sys_args_good(self):
        args = ["main", "add_contributor", "zeb", "tester"]
        with patch.object(sys, "argv", args):
            self.assertEqual(validator.val_sys_args(args[1:]), True)

    def test_sys_args_missing_args(self):
        args = ["main", "add_contributor"]
        with patch.object(sys, "argv", args):
            with pytest.raises(SystemExit) as error:
                self.assertEqual(validator.val_sys_args(args[1:]), str(error.value))

    def test_sys_args_no_method(self):
        args = ["main"]
        with patch.object(sys, "argv", args):
            with pytest.raises(SystemExit) as error:
                self.assertEqual(validator.val_sys_args(args[1:]), str(error.value))

    def test_start_good(self):
        self.assertEqual(validator.val_start("2022-06-06"), True)

    def test_start_bad(self):
        with pytest.raises(errors.DateFormatError) as error:
            self.assertEqual(validator.val_start("022-06-06"), str(error.value))
            self.assertEqual(validator.val_start("2022_06_06"), str(error.value))

    def test_due_good(self):
        self.assertEqual(validator.val_due("2022-06-06", "2022-06-05"), True)

    def test_due_bad(self):
        with pytest.raises(errors.DateFormatError) as error:
            self.assertEqual(
                validator.val_due("022-06-06", "2022-01-01"), str(error.value)
            )
            self.assertEqual(
                validator.val_due("2022_06_06", "2022-01-01"), str(error.value)
            )

    def test_due_before_start(self):
        with pytest.raises(errors.DateFormatError) as error:
            self.assertEqual(
                validator.val_due("2022-06-05", "2022-06-06"), str(error.value)
            )

    def test_priority_good(self):
        self.assertEqual(validator.val_priority("high"), True)
        self.assertEqual(validator.val_priority("HIGH"), True)
        self.assertEqual(validator.val_priority("High"), True)
        self.assertEqual(validator.val_priority("low"), True)
        self.assertEqual(validator.val_priority("medium"), True)

    def test_priority_bad(self):
        with pytest.raises(errors.PriorityError) as error:
            self.assertEqual(validator.val_priority("low p"), str(error.value))
            self.assertEqual(validator.val_priority(""), str(error.value))


class TestAdd(unittest.TestCase):
    """Tests Adding Functions"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)

    def test_add_contributor(self):
        row = main.add_contributor("zeb", "tester")
        assert row.NAME == "zeb"
        self.assertEqual(main.add_contributor("zeb", "tester"), False)

    def test_add_task(self):
        """Test Adding Status"""
        main.add_contributor("zeb", "tester")
        row = main.add_task(
            "zeb", "write tests", "test description", "high", "2020-01-01", "2022-01-01"
        )
        assert row.NUM == "1"
        assert str(row.OWNER) == "zeb"
        assert row.NAME == "write tests"
        assert row.DESCRIPTION == "test description"
        assert row.PRIORITY == "high"
        loguru.logger.debug(row.PRIORITY)
        assert row.START == "2020-01-01"
        assert row.DUE == "2022-01-01"
        assert row.FINISHED is False
        assert row.DELETED is False

    def test_add_task_no_contributor(self):
        self.assertEqual(
            main.add_task(
                "",
                "write tests",
                "test description",
                "high",
                "2020-01-01",
                "2022-01-01",
            ),
            False,
        )

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


class TestUpdate(unittest.TestCase):
    """Tests Updating Function"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)

    def test_update(self):
        main.add_contributor("zeb", "tester")
        main.add_task(
            "zeb", "write tests", "test description", "high", "2020-01-01", "2022-01-01"
        )
        row = main.update_task(
            "1",
            task_name="new_name",
            task_description="new_description",
            priority="low",
        )
        assert row.NAME == "new_name"
        assert row.DESCRIPTION == "new_description"
        assert row.PRIORITY == "low"

    def test_update_priority_bad(self):
        main.add_contributor("zeb", "tester")
        main.add_task(
            "zeb", "test name", "test description", "high", "2020-01-01", "2022-01-01"
        )
        with pytest.raises(errors.PriorityError) as error:
            self.assertEqual(main.update_task("1", priority=" "), str(error.value))

    def test_update_not_exist(self):
        self.assertEqual(main.update_task("2", task_name=" "), False)

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


class TestMarkComplete(unittest.TestCase):
    """Tests Marking Functions Complete"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)

    def test_mark_complete(self):
        main.add_contributor("zeb", "tester")
        main.add_task(
            "zeb", "write tests", "test description", "high", "2020-01-01", "2022-01-01"
        )
        row = main.mark_task_complete("1")
        assert row.FINISHED is True

    def test_mark_complete_not_exist(self):
        self.assertEqual(main.mark_task_complete(""), False)

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


class TestDelete(unittest.TestCase):
    """Tests Deleting Functions"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)

    def test_delete_contributor_no_task(self):
        main.add_contributor("zeb", "tester")
        row = main.delete_contributor("zeb")
        for item in row:
            assert item is True

    def test_delete_contributor_with_task(self):
        main.add_contributor("zeb", "tester")
        main.add_task(
            "zeb", "write tests", "test description", "high", "2020-01-01", "2022-01-01"
        )
        main.add_task(
            "zeb",
            "write more tests",
            "another description",
            "medium",
            "2022-05-05",
            "2050-01-01",
        )
        row = main.delete_contributor("zeb")
        for item in row:
            assert item is True

    def test_delete_task(self):
        main.add_contributor("zeb", "tester")
        main.add_task(
            "zeb", "write tests", "test description", "high", "2020-01-01", "2022-01-01"
        )
        row = main.delete_task("1")
        assert row.DELETED is True

    def test_delete_contributor_not_exist(self):
        self.assertEqual(main.delete_contributor(""), False)

    def test_delete_task_not_exist(self):
        self.assertEqual(main.delete_task(""), False)

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


class TestList(unittest.TestCase):
    """Tests Listing Function"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)

        main.add_contributor("john", "writer")
        main.add_contributor("zeb", "tester")
        main.add_task(
            "zeb", "c test", "a description", "low", "2021-01-03", "2023-01-01"
        )
        main.add_task(
            "zeb", "a test", "another description", "medium", "2021-01-02", "2022-01-02"
        )
        main.add_task(
            "john", "b test", "test description", "high", "2020-01-01", "2022-01-03"
        )

    def test_list_default(self):
        task_list = main.list_tasks()
        first_row = task_list[0]
        assert first_row[0] == "1"

    def test_list_num(self):
        task_list = main.list_tasks(sort="Num")
        first_row = task_list[0]
        assert first_row[0] == "1"

    def test_list_owner(self):
        task_list = main.list_tasks(sort="Owner")
        first_row = task_list[0]
        assert first_row[1] == "john"

    def test_list_name(self):
        task_list = main.list_tasks(sort="Name")
        first_row = task_list[0]
        assert first_row[2] == "a test"

    def test_list_priority(self):
        task_list = main.list_tasks(sort="Priority")
        first_row = task_list[0]
        assert first_row[4] == "high"

    def test_list_start(self):
        task_list = main.list_tasks(sort="Start")
        first_row = task_list[0]
        assert first_row[5] == "2020-01-01"

    def test_list_due(self):
        task_list = main.list_tasks(sort="Due")
        first_row = task_list[0]
        assert first_row[6] == "2022-01-02"

    def test_list_finished(self):
        main.mark_task_complete('2')
        task_list = main.list_tasks(sort="Finished")
        first_row = task_list[0]
        assert first_row[7] == False
        last_row = task_list[-1]
        assert last_row[7] == True

    def test_list_deleted(self):
        main.delete_task("2")
        task_list = main.list_tasks(sort="Deleted")
        first_row = task_list[0]
        assert first_row[8] == False
        last_row = task_list[2]
        assert last_row[8] == True

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


if __name__ == "__main__":
    unittest.main()
