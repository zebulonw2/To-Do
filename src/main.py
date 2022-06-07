"""
main driver for a simple social network project
"""
import os
import sys
from loguru import logger
import peewee as pw
import models as m
from validator import val_priority, val_due, val_start, val_sys_args


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
    Deletes contributor
    """
    try:
        row = m.ContributorsDB.get(m.ContributorsDB.NAME == name)
        row.DELETED = True
        logger.info(f"Contributor Deleted: " f"{row.NAME, row.ROLE, row.DELETED}")
        return True
    except pw.IntegrityError:
        logger.error(f"'{name}' Not Found in DB")
        raise m.ContributorsDB.DoesNotExist


def add_task(task_owner, task_name, description, priority, start, due):
    """
    Add New Task To Project
    """
    task_num = str(len(m.TasksDb) + 1)
    val_start(start)
    val_due(due, start)
    val_priority(priority)
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


def update_task(task_num, task_name=None, task_description=None):
    """
    Updates Task Information
    """
    try:
        row = m.TasksDb.get(m.TasksDb.NUM == task_num)
        if task_name:
            row.NAME = task_name
        if task_description:
            row.DESCRIPTION = task_description
        logger.info(f"Task '{task_num}' Changed. "
                    f"Name: '{row.NAME}' Description: {row.DESCRIPTION}")
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
        logger.info(f"Task Deleted: " f"{row.NUM, row.NAME}")
        return True
    except pw.IntegrityError:
        logger.error(f"'{task_num}' Not Found in DB")
        raise m.TasksDb.DoesNotExist


def list_tasks(status_id):
    """
    Searches for a status in status_collection
    """
    try:
        row = m.StatusDb.get(m.StatusDb.STATUS_ID == status_id)
        print(
            f"Status Found:\n"
            f"Status ID: {row.STATUS_ID}\n"
            f"User ID: {row.USER_ID}\n"
            f"Status Text: {row.STATUS_TEXT}"
        )
        return True
    except m.StatusDb.DoesNotExist:
        logger.error(f"'{status_id}' Not Found in DB")
        return False


def main() -> None:
    """Entrypoint of program run as module"""
    m.create_db()
    val_sys_args()
    args = sys.argv[1:]
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
    m.db.close()
    sys.exit()


if __name__ == "__main__":
    main()
