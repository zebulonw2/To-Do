"""
main driver for a simple social network project
"""
# pylint: disable=W0703
# pylint: disable=R0913
import datetime
import sys
from texttable import Texttable
from loguru import logger
import peewee as pw
import typer
import models as m

# logger.remove()
# logger.add("log_{time}.log")
# logger.add(sys.stderr, level="DEBUG")

app = typer.Typer()


@app.command(short_help="Add New Contributor To Project")
def add_contributor(name: str, role: str):
    """
    Add New Contributor To Project
    """
    typer.echo(f"Adding {name} To Project...")
    try:
        new_contributor = m.ContributorsDB.create(NAME=name, ROLE=role, DELETED=False)
        new_contributor.save()
        logger.info(
            f"Contributor Added: " f"{new_contributor.NAME, new_contributor.ROLE}"
        )
        return new_contributor
    except pw.IntegrityError:
        logger.error(f"'{name}' Already in DB")
        return False
    except Exception as error:  # pragma: no cover
        logger.error(error)
        return False


@app.command(short_help="Deletes Contributor and Associated Tasks")
def delete_contributor(name: str):
    """
    Deletes Contributor and Associated Tasks
    """
    typer.echo(f"Deleting {name} From Project...")
    test_list = []
    try:
        contributor = m.ContributorsDB.get(m.ContributorsDB.NAME == name)
        contributor.DELETED = True
        logger.info(
            f"Deleted: {contributor.NAME, contributor.ROLE, contributor.DELETED}"
        )
        test_list.append(contributor.DELETED)
        task_query = (
            m.TasksDb.select(m.TasksDb, m.ContributorsDB)
            .join(m.ContributorsDB)
            .where(m.ContributorsDB.NAME == name)
        )
        if len(task_query) > 0:
            for row in task_query:
                row.DELETED = True
                test_list.append(row.DELETED)
            logger.info(f"{len(task_query)} Task(s) Owned By {name} Deleted")
        return test_list
    except pw.DoesNotExist:
        logger.error(f"'{name}' Not Found in DB")
        return False
    except Exception as error:  # pragma: no cover
        logger.error(error)
        return False


@app.command(short_help="Add New Task To Project")
def add_task(
    task_owner: str,
    task_name: str,
    description: str,
    priority: str,
    start: str,
    due: str,
):
    """
    Add New Task To Project
    """
    typer.echo(f"Adding {task_name} To Project")
    task_num = str(len(m.TasksDb) + 1)
    val_priority(priority)
    val_start(start)
    val_due(due, start)
    deleted = False
    finished = False
    try:
        tsk = m.TasksDb.create(
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
        logger.info(
            f"Task Added To DB: "
            f"{tsk.NUM, tsk.OWNER, tsk.NAME, tsk.DESCRIPTION, tsk.PRIORITY, tsk.START, tsk.DUE}"
        )
        tsk.save()
        return tsk
    except pw.DoesNotExist:
        logger.error(f"'{task_owner}' Not A Contributor")
        return False
    except Exception as error:  # pragma: no cover
        logger.error(f"{error.__class__, str(error)}")
        return False


@app.command(
    short_help="Updates Task Information. Requires Task Num and At Least One Optional Arg"
)
def update_task(
    task_num: str,
    task_name: str = None,
    task_description: str = None,
    priority: str = None,
):
    """
    Updates Task Information. Requires Task Num and At Least One Optional Argument
    """
    typer.echo(f"Updating Task '{task_num}'...")
    try:
        row = m.TasksDb.get(m.TasksDb.NUM == task_num)
        if task_name:
            row.NAME = task_name
        if task_description:
            row.DESCRIPTION = task_description
        if priority:
            val_priority(priority)
            row.PRIORITY = priority
        row.save()
        logger.info(
            f"Task '{task_num}' Changed. "
            f"Name: '{row.NAME}' Description: {row.DESCRIPTION} Priority: '{row.PRIORITY}'"
        )
        return row
    except pw.DoesNotExist:
        logger.error(f"'{task_num}' Not Found in DB")
        return False
    except Exception as error:  # pragma: no cover
        logger.error(error)
        return False


@app.command(short_help="Marks Task Complete")
def mark_task_complete(task_num: str):
    """
    Marks Task Complete
    """
    typer.echo(f"Marking Task '{task_num}' Complete...")
    try:
        row = m.TasksDb.get(m.TasksDb.NUM == task_num)
        row.FINISHED = True
        logger.info(f"Task Marked Complete: " f"{row.NUM, row.NAME, row.FINISHED}")
        row.save()
        return row
    except pw.DoesNotExist:
        logger.error(f"'{task_num}' Not Found in DB")
        return False
    except Exception as error:  # pragma: no cover
        logger.error(error)
        return False


@app.command(short_help="Deletes Task From Project")
def delete_task(task_num):
    """
    Deletes Task From Project
    """
    typer.echo(f"Deleting Task '{task_num}'...")
    try:
        row = m.TasksDb.get(m.TasksDb.NUM == task_num)
        row.DELETED = True
        row.save()
        logger.info(f"Task Deleted: " f"{row, row.NUM, row.NAME, row.DELETED}")
        return row
    except pw.DoesNotExist:
        logger.error(f"'{task_num}' Not Found in DB")
        return False
    except Exception as error:  # pragma: no cover
        logger.error(error)
        return False


@app.command(
    short_help="Lists Task on Entered Sort Field, Default Sorts by Task Number"
)
def list_tasks(sort="Num"):
    """
    Lists Task on Entered Sort Field, Default Sorts by Task Number
    """
    typer.echo(f"Sorting On {sort}...")
    print(f"Sorted On {sort}")
    table = Texttable()
    table.set_max_width(0)
    table.set_cols_dtype(["t"] * 9)
    table.add_row(
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
    if sort == "Num":
        query = m.TasksDb.NUM
    elif sort == "Owner":
        query = m.TasksDb.OWNER
    elif sort == "Name":
        query = m.TasksDb.NAME
    elif sort == "Priority":
        query = m.TasksDb.PRIORITY
    elif sort == "Start":
        query = m.TasksDb.START
    elif sort == "Due":
        query = m.TasksDb.DUE
    elif sort == "Finished":
        query = m.TasksDb.FINISHED
    elif sort == "Deleted":
        query = m.TasksDb.DELETED
    else:
        query = ""
    test_list = []
    # pylint: disable=E1133
    for i in m.TasksDb.select().order_by(query):
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
        table.add_row(row)
        logger.info(row)
        test_list.append(row)
    print(table.draw())
    return test_list


@app.command(short_help="Prints Size Of DBs")
def table_attributes():
    """
    Prints Size Of DBs
    """
    typer.echo("Printing Table Attributes...")
    logger.info(f"Contributors DB {len(m.ContributorsDB)}")
    logger.info(f"Tasks DB {len(m.TasksDb)}")
    return len(m.ContributorsDB), len(m.TasksDb)


class DateFormatError(Exception):
    """Dates must be YYYY-MM-DD"""

    def __init__(self, message: str):
        super().__init__(f"\n{message}")


class PriorityError(Exception):
    """Priority must be High, Medium, or Low"""

    def __init__(self, message: str):
        super().__init__(f"\n{message}")


def val_start(start):
    """Validates Start Date"""
    try:
        datetime.datetime.strptime(start, "%Y-%m-%d")
        return True
    except ValueError:
        raise DateFormatError("Dates Must Be YYYY-MM-DD") from Exception


def val_due(due, start):
    """Validates Due Date"""
    try:
        datetime.datetime.strptime(due, "%Y-%m-%d")
        if not due > start:
            raise DateFormatError(f"Due Date Must Be After {start}")
        return True
    except ValueError:
        print("Dates Must Be YYYY-MM-DD")
        raise DateFormatError("Dates Must Be YYYY-MM-DD") from Exception


def val_priority(priority):
    """Validates Priority Format"""
    priority_options = ["HIGH", "MEDIUM", "LOW"]
    if str(priority).upper() not in priority_options:
        raise PriorityError("Priority Must Be High, Medium, or Low")
    return True


if __name__ == "__main__":
    m.create_db()
    app()
    m.db.close()
    sys.exit()
