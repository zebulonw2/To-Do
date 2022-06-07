"""Defines To-Do List Relational Database"""
# pylint: disable=R0903
import peewee as pw

db = pw.SqliteDatabase("to-do.db")


class BaseModel(pw.Model):
    """Base Class For DB"""

    class Meta:
        """Meta Class"""
        database = db


class ContributorsDB(BaseModel):
    """Class For Contributors"""
    NAME = pw.CharField(primary_key=True, max_length=30)
    ROLE = pw.CharField(max_length=30)
    DELETED = pw.BooleanField(default=False)


class TasksDb(BaseModel):
    """Class For Tasks"""
    NUM = pw.CharField(primary_key=True)
    OWNER = pw.ForeignKeyField(ContributorsDB, backref="task")
    NAME = pw.CharField()
    DESCRIPTION = pw.CharField()
    PRIORITY = pw.CharField
    START = pw.CharField()
    DUE = pw.CharField()
    FINISHED = pw.BooleanField(default=False)
    DELETED = pw.BooleanField(default=False)


def create_db():
    """Creates Tables"""
    db.connect()
    db.execute_sql('PRAGMA foreign_keys = ON;')
    db.create_tables([ContributorsDB, TasksDb])
