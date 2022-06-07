"""
main driver for a simple social network project
"""
import os
import sys
from texttable import Texttable
import pysnooper
from loguru import logger
import peewee as pw
import src.models as m
from src.validator import val_sys_args

# logger.remove()
# logger.add("log_{time}.log")
# logger.add(sys.stderr, level="DEBUG")

path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def add_contributor(name, role):
    """
    Add New Contributor To Project
    """
    try:
        new_contributor = m.ContributorsDB.create(NAME=name, ROLE=role, DELETED=False)
        new_contributor.save()
        logger.info(
            f"Contributor Added: "
            f"{new_contributor.NAME, new_contributor.ROLE, new_contributor.DELETED}"
        )
        return True
    except pw.IntegrityError as error:
        logger.error(error)
        return False


def delete_contributor(name):
    """
    Deletes contributor and Associated Tasks
    """
    try:
        c = m.ContributorsDB.get(m.ContributorsDB.NAME == name)
        c.DELETED = True
        logger.info(f"Contributor Deleted: " f"{c.NAME, c.ROLE, c.DELETED}")
        task_query = (
            m.TasksDb.select(m.TasksDb, m.ContributorsDB)
                .join(m.ContributorsDB)
                .where(m.ContributorsDB.NAME == name)
        )
        if len(task_query) > 0:
            for row in task_query:
                row.DELETED = True
            logger.info(f"{len(task_query)} Task(s) Owned By {name} Deleted")
            return True
        return True
    except pw.IntegrityError:
        logger.error(f"'{name}' Not Found in DB")
        raise m.ContributorsDB.DoesNotExist


def add_task(task_owner, task_name, description, priority, start, due):
    """
    Add New Task To Project
    """
    task_num = str(len(m.TasksDb) + 1)
    deleted = False
    finished = False
    try:
        t = m.TasksDb.create(
            NUM=task_num,
            OWNER=task_owner,
            NAME=task_name,
            DESCRIPTION=description,
            START=start,
            DUE=due,
            PRIORITY=priority,
            DELETED=deleted,
            FINISHED=finished,
        )
        t.save()
        logger.info(
            f"Task Added To DB: "
            f"{t.NUM, t.OWNER, t.NAME, t.DESCRIPTION, t.PRIORITY, t.START, t.DUE}"
        )
        return True
    except m.ContributorsDB.DoesNotExist as error:
        logger.error(f"'{task_owner}' Not A Contributor")
        return False


def update_task(task_num, task_name=None, task_description=None, priority=None):
    """
    Updates Task Information
    """
    try:
        row = m.TasksDb.get(m.TasksDb.NUM == task_num)
        if task_name:
            row.NAME = task_name
        if task_description:
            row.DESCRIPTION = task_description
        if priority:
            # validator.val_priority(priority) #todo validate this via sys.args
            row.PRIORITY = priority
        row.save()
        logger.info(
            f"Task '{task_num}' Changed. "
            f"Name: '{row.NAME}' Description: {row.DESCRIPTION} Priority: '{row.PRIORITY}'"
        )
        return True
    except m.TasksDb.DoesNotExist:
        logger.error(f"'{task_num}' Not Found in DB")
        return False


def mark_task_complete(task_num):
    """
    Marks Task Complete
    """
    try:
        row = m.TasksDb.get(m.TasksDb.NUM == task_num)
        row.FINISHED = True
        row.save()
        logger.info(f"Task Marked Complete: " f"{row.NUM, row.NAME}")
        return True
    except pw.IntegrityError:
        logger.error(f"'{task_num}' Not Found in DB")
        raise m.TasksDb.DoesNotExist


def delete_task(task_num):
    """
    Deletes Task
    """
    try:
        row = m.TasksDb.get(m.TasksDb.NUM == task_num)
        row.DELETED = True
        row.save()
        logger.info(f"Task Deleted: " f"{row, row.NUM, row.NAME, row.DELETED}")
        return True
    except pw.IntegrityError:
        logger.error(f"'{task_num}' Not Found in DB")
        raise m.TasksDb.DoesNotExist


def list_tasks(sort=None):  # todo figure out sort
    """
    Lists Task on Entered Sort Field, Default Sorts by Task Number
    """
    testing_list = []
    t = Texttable()
    t.set_max_width(0)
    t.set_cols_dtype(["t"] * 9)
    t.add_row([f"Sorted By {sort}", "", "", "", "", "", "", "", ""])
    t.add_row(
        [
            "Num",
            "Owner",
            "Name",
            "Description",
            "Priority",
            "Start",
            "Due",
            "Finished",
            "Deleted",
        ]
    )
    if sort == 'Num':
        query = m.TasksDb.NUM
    if sort == 'Owner':
        query = m.TasksDb.OWNER
    if sort == 'Name':
        query = m.TasksDb.NAME
    if sort == 'Priority':
        query = m.TasksDb.PRIORITY
    if sort == 'Start':
        query = m.TasksDb.START
    if sort == 'Due':
        query = m.TasksDb.DUE
    if sort == 'Finished':
        query = m.TasksDb.FINISHED
    if sort == 'Deleted':
        query = m.TasksDb.DELETED
    else:
        query = ""
    task_query = m.TasksDb.select().order_by(query)
    for i in task_query:
        row = [
            i.NUM,
            str(i.OWNER),
            i.NAME,
            i.DESCRIPTION,
            i.PRIORITY,
            i.START,
            i.DUE,
            i.FINISHED,
            i.DELETED,
        ]
        t.add_row(row)
        logger.info(row)
        testing_list.append(row)
    print(t.draw())
    logger.info(testing_list)
    return testing_list


def main() -> None:
    """Entrypoint of program run as module"""
    m.create_db()
    args = sys.argv[1:]
    val_sys_args(args)
    if args[0] == "add_contributor":
        add_contributor(name=args[1], role=args[2])
    if args[0] == "delete_contributor":
        delete_contributor(name=args[1])
    if args[0] == "add_task":
        add_task(
            task_owner=args[1],
            task_name=args[2],
            description=args[3],
            start=args[4],
            due=args[5],
            priority=args[6],
        )
    if args[0] == "update_task":
        update_task(task_num=args[1], *args)
    if args[0] == "mark_task_complete":
        mark_task_complete(task_num=args[1])
    if args[0] == "delete_task":
        delete_task(task_num=args[1])
    if args[0] == "list_tasks":
        list_tasks(sort=args[1])
    m.db.close()
    sys.exit()


if __name__ == "__main__":
    main()
