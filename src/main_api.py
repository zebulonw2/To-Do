from flask import Flask
from flask_restful import Resource, Api
import models as m
from flask import jsonify

db = m.db


class Contributors(Resource):
    def get(self):
        query = m.ContributorsDB.select()
        result = {
            "Contributors": [
                (i.NAME, i.ROLE, "Current" if i.DELETED is False else "Former")
                for i in query
            ]
        }
        db.close()
        return jsonify(result)


class Profile(Resource):
    def get(self, name):
        c = m.ContributorsDB.get(m.ContributorsDB.NAME == name)
        tasks = []
        task_query = (
            m.TasksDb.select(m.TasksDb, m.ContributorsDB)
            .join(m.ContributorsDB)
            .where(m.ContributorsDB.NAME == name)
        )
        for t in task_query:
            row = (
                t.NUM,
                t.NAME,
                t.DESCRIPTION,
                t.PRIORITY,
                t.START,
                t.DUE,
                t.FINISHED,
                t.DELETED,
            )
            tasks.append(row)
        result = {
            "Contributor": [
                (c.NAME, c.ROLE, "Current" if c.DELETED is False else "Former")
            ],
            "Tasks": tasks,
        }
        return jsonify(result)


class Tasks(Resource):
    def get(self):
        tasks = []
        query = m.TasksDb.select()
        for i in query:
            row = (
                i.NUM,
                str(i.OWNER),
                i.NAME,
                i.DESCRIPTION,
                i.PRIORITY,
                i.START,
                i.DUE,
                i.FINISHED,
                i.DELETED,
            )
            tasks.append(row)
        result = {"Tasks": [tasks]}
        return jsonify(result)


class Priority(Resource):
    def get(self):
        tasks = []
        query = m.TasksDb.select().s
        for i in query:
            row = (
                i.NUM,
                str(i.OWNER),
                i.NAME,
                i.DESCRIPTION,
                i.PRIORITY,
                i.START,
                i.DUE,
                i.FINISHED,
                i.DELETED,
            )
            tasks.append(row)
        result = {"Tasks": [tasks]}
        return jsonify(result)


class Finished(Resource):
    def get(self):
        tasks = []
        query = m.TasksDb.select().where(m.TasksDb.FINISHED is True)
        for i in query:
            row = (
                i.NUM,
                str(i.OWNER),
                i.NAME,
                i.DESCRIPTION,
                i.PRIORITY,
                i.START,
                i.DUE,
                i.FINISHED,
                i.DELETED,
            )
            tasks.append(row)
        result = {"Finished Tasks": [tasks]}
        return jsonify(result)


class Deleted(Resource):
    def get(self):
        tasks = []
        query = m.TasksDb.select().where(m.TasksDb.DELETED is True)
        for i in query:
            row = (
                i.NUM,
                str(i.OWNER),
                i.NAME,
                i.DESCRIPTION,
                i.PRIORITY,
                i.START,
                i.DUE,
                i.FINISHED,
                i.DELETED,
            )
            tasks.append(row)
        result = {"Deleted Tasks": [tasks]}
        return jsonify(result)


def main():
    m.create_db()
    app = Flask(__name__)

    api = Api(app)
    api.add_resource(Contributors, "/contributors")
    api.add_resource(Profile, "/contributors/<name>", "/tasks/<name>")
    api.add_resource(Tasks, "/tasks")
    api.add_resource(Priority, "tasks/priority")
    api.add_resource(Finished, "tasks/finished")
    api.add_resource(Deleted, "tasks/deleted")

    app.run(port=5000)

    db.close()


if __name__ == "__main__":
    main()

#todo add /deleted, /finished, /priority, NUM", "OWNER", "NAME", "DESCRIPTION",
# "PRIORITY", "START", "DUE", "FINISHED", "DELETED",