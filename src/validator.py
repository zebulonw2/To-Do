"""
Validates CLI Arguments
"""
import datetime
from loguru import logger
from errors import DateFormatError, PriorityError


def val_sys_args(args):
    methods = [
        "add_contributor",
        "delete_contributor",
        "add_task",
        "update_task",
        "mark_task_complete",
        "delete_task",
        "list_tasks",
        "table_attributes",
    ]

    if len(args) == 0:
        logger.error(f"Args Called: {args}")
        raise SystemExit(f"Usage: main {methods}")

    if args[0] == methods[0]:
        if len(args) != 3:
            logger.error(f"Args Called: {args}")
            raise SystemExit("Usage: main add_contributor name role")

    if args[0] == methods[1]:
        if len(args) != 2:
            logger.error(f"Args Called: {args}")
            raise SystemExit("Usage: main delete_contributor name")

    if args[0] == methods[2]:
        if len(args) != 7:
            logger.error(f"Args Called: {args}")
            raise SystemExit(
                "Usage: main add_task task_owner task_name task_description "
                "priority start_date due_date"
            )
        val_priority(args[4])
        val_start(args[5])
        val_due(args[6], args[5])

    if args[0] == methods[3]:
        if len(args) not in (4, 5, 6):
            logger.error(f"Args Called: {args}")
            raise SystemExit(
                "Usage: main update_task task_number [task_name] [task_description] [priority]"
            )

    if args[0] == methods[4]:
        if len(args) != 2:
            logger.error(f"Args Called: {args}")
            raise SystemExit("Usage: main mark_task_complete task_number")

    if args[0] == methods[5]:
        if len(args) != 2:
            logger.error(f"Args Called: {args}")
            raise SystemExit("Usage: main delete_task task_number")

    if args[0] == methods[6]:
        logger.debug(len(args))
        sort_fields = [
            "Num",
            "Owner",
            "Name",
            "Priority",
            "Start",
            "Due",
            "Finished",
            "Deleted",
        ]
        if len(args) not in (1, 2):
            logger.error(f"Args Called: {args}")
            raise SystemExit(f"Usage: main list_tasks sort_by={sort_fields}")
        if len(args) == 2:
            sort_arg = args[1]
            if sort_arg not in sort_fields:
                logger.error(f"Args Called: {args}")
                raise SystemExit(f"Usage: main list_tasks sort_by={sort_fields}")

    if args[0] == methods[7]:
        if len(args) != 1:
            logger.error(f"Args Called: {args}")
            raise SystemExit(f"Usage: main table_attributes")

    if args[0] not in methods:
        logger.error(args)
        raise SystemExit(
            "Usage: main [add_contributor] [delete_contributor] [add_task] "
            "[update_task] [delete_task] [list_tasks]"
        )
    return True


def val_start(start):
    try:
        datetime.datetime.strptime(start, "%Y-%m-%d")
        return True
    except ValueError:
        raise DateFormatError("Dates Must Be YYYY-MM-DD")


def val_due(due, start):
    try:
        datetime.datetime.strptime(due, "%Y-%m-%d")
        if not due > start:
            raise DateFormatError(f"Due Date Must Be After {start}")
        return True
    except ValueError:
        print(f"Dates Must Be YYYY-MM-DD")
        raise DateFormatError("Dates Must Be YYYY-MM-DD")


def val_priority(priority):
    priority_options = ["HIGH", "MEDIUM", "LOW"]
    if str(priority).upper() not in priority_options:
        raise PriorityError("Priority Must Be High, Medium, or Low")
    return True
