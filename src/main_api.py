from flask import Flask, render_template
from flask_restful import Resource, Api
import models as m
from main import list_tasks
from flask import jsonify

db = m.db
app = Flask(__name__)


class Contributors(Resource):
    def get(self):
        query = m.ContributorsDB.select()
        result = {
            "Contributors": [
                (i.NAME, i.ROLE, "Current" if i.DELETED is False else "Former")
                for i in query
            ]
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


class List(Resource):
    def get(self, sort):
        table = list_tasks(sort=sort)
        results = {f"Tasks Sorted On {str(sort).title()}": [table]}
        return jsonify(results)


@app.route("/")
def home():
    return render_template("index.html")


def main():
    m.create_db()

    api = Api(app)
    api.add_resource(Contributors, "/contributors/")
    api.add_resource(Tasks, "/tasks/")
    api.add_resource(
        Profile,
        "/contributors/<name>/",
        "/tasks/<name>/",
    )
    api.add_resource(List, "/tasks/sort/<sort>/")

    app.run(port=5000, debug=True)

    db.close()


if __name__ == "__main__":
    main()
