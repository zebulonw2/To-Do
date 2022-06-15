"""
Unit Test for main.py
"""
import unittest
import loguru
import peewee as pw
import pytest
import main
import models
from models import ContributorsDB, TasksDb

MODELS = (ContributorsDB, TasksDb)
test_db = pw.SqliteDatabase(":memory:")


class TestValidator(unittest.TestCase):
    """Tests Validation Methods"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)

    def test_start_good(self):
        """test good start format"""
        self.assertEqual(main.val_start("2022-06-06"), True)

    def test_start_bad(self):
        """test bad start format"""
        with pytest.raises(main.DateFormatError) as error:
            self.assertEqual(main.val_start("022-06-06"), str(error.value))

    def test_due_good(self):
        """tests good due format"""
        self.assertEqual(main.val_due("2022-06-06", "2022-06-05"), True)

    def test_due_bad(self):
        """tests bad due format"""
        with pytest.raises(main.DateFormatError) as error:
            self.assertEqual(main.val_due("022-06-06", "2022-01-01"), str(error.value))

    def test_due_before_start(self):
        """test due date before start date"""
        with pytest.raises(main.DateFormatError) as error:
            self.assertEqual(main.val_due("2022-06-05", "2022-06-06"), str(error.value))

    def test_priority_good(self):
        """tests good priority formats"""
        self.assertEqual(main.val_priority("high"), True)
        self.assertEqual(main.val_priority("HIGH"), True)
        self.assertEqual(main.val_priority("High"), True)
        self.assertEqual(main.val_priority("low"), True)
        self.assertEqual(main.val_priority("medium"), True)

    def test_priority_bad(self):
        """tests bad priority formats"""
        with pytest.raises(main.PriorityError) as error:
            self.assertEqual(main.val_priority("low p"), str(error.value))

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


class TestAdd(unittest.TestCase):
    """Tests Adding Functions"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)

    def test_add_contributor(self):
        """add contributor"""
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
        """add task when no contributor exists"""
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
        """tests update"""
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
        """tests update with bad priority format"""
        main.add_contributor("zeb", "tester")
        main.add_task(
            "zeb", "test name", "test description", "high", "2020-01-01", "2022-01-01"
        )
        self.assertEqual(main.update_task("1", priority=" "), False)

    def test_update_not_exist(self):
        """update task that doesn't exist"""
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
        """tests mark complete"""
        main.add_contributor("zeb", "tester")
        main.add_task(
            "zeb", "write tests", "test description", "high", "2020-01-01", "2022-01-01"
        )
        row = main.mark_task_complete("1")
        assert row.FINISHED is True

    def test_mark_complete_not_exist(self):
        """marks task complete that doesn't exists"""
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
        """tests delete with no task"""
        main.add_contributor("zeb", "tester")
        row = main.delete_contributor("zeb")
        for item in row:
            assert item is True

    def test_delete_contributor_with_task(self):
        """tests delete with task"""
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
        """tests delete task"""
        main.add_contributor("zeb", "tester")
        main.add_task(
            "zeb", "write tests", "test description", "high", "2020-01-01", "2022-01-01"
        )
        row = main.delete_task("1")
        assert row.DELETED is True

    def test_delete_contributor_not_exist(self):
        """tests delete a contributor that doesn't exist"""
        self.assertEqual(main.delete_contributor(""), False)

    def test_delete_task_not_exist(self):
        """tests delete a task that doesn't exist"""
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
        """tests sort on default"""
        task_list = main.list_tasks(" ")
        first_row = task_list[0]
        assert first_row[0] == "1"

    def test_list_num(self):
        """tests sort on num"""
        task_list = main.list_tasks(sort="Num")
        first_row = task_list[0]
        assert first_row[0] == "1"

    def test_list_owner(self):
        """tests sort on owner"""
        task_list = main.list_tasks(sort="Owner")
        first_row = task_list[0]
        assert first_row[1] == "john"

    def test_list_name(self):
        """tests sort on name"""
        task_list = main.list_tasks(sort="Name")
        first_row = task_list[0]
        assert first_row[2] == "a test"

    def test_list_priority(self):
        """tests sort on priority"""
        task_list = main.list_tasks(sort="Priority")
        first_row = task_list[0]
        assert first_row[4] == "high"

    def test_list_start(self):
        """tests sort on start"""
        task_list = main.list_tasks(sort="Start")
        first_row = task_list[0]
        assert first_row[5] == "2020-01-01"

    def test_list_due(self):
        """tests sort on due"""
        task_list = main.list_tasks(sort="Due")
        first_row = task_list[0]
        assert first_row[6] == "2022-01-02"

    def test_list_finished(self):
        """tests sort on finished"""
        main.mark_task_complete("2")
        task_list = main.list_tasks(sort="Finished")
        for row in task_list:
            assert row[7] is True

    def test_list_deleted(self):
        """tests sort on deleted"""
        main.delete_task("2")
        task_list = main.list_tasks(sort="Deleted")
        for row in task_list:
            assert row[8] is True

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


class TestTableAttributes(unittest.TestCase):
    """Tests Table Attributes Method"""

    def setUp(self) -> None:
        for model in MODELS:
            model.bind(test_db, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)

    def test_table_attributes(self):
        """Tests table attributes"""
        row = main.table_attributes()
        assert row[0] == 0
        assert row[1] == 0

    def tearDown(self) -> None:
        test_db.drop_tables(MODELS)
        test_db.close()


class TestDB(unittest.TestCase):
    """Tests DB Creation"""

    def test_db_creation(self):
        self.assertEqual(models.create_db(), (ContributorsDB, TasksDb))


if __name__ == "__main__":
    unittest.main()
