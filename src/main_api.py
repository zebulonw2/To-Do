"""API for To-Do List"""
from flask import Flask, render_template
from flask_restful import Resource, Api
import models as m
from main import list_tasks
from flask import jsonify

db = m.db
app = Flask(__name__)


@app.route("/")
def home():
    """Defines Home Screen"""
    return render_template("index.html")


class Contributors(Resource):
    """Class For Contributors Method"""
    def get(self):
        """Shows All Contributors"""
        query = m.ContributorsDB.select()
        result = {
            "Contributors": [
                (i.NAME, i.ROLE, "Current" if i.DELETED is False else "Former")
                for i in query
            ]
        }
        return jsonify(result)


class Profile(Resource):
    """Class for Profiling Method"""
    @staticmethod
    def get(self, name):
        """Shows A Contributor's Profile And Task List"""
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
    """Defines List Sorting Pages"""
    def get(self, sort):
        """Retrieves Sorted Task List From main.py"""
        table = list_tasks(sort=sort)
        results = {f"Tasks Sorted On {str(sort).title()}": [table]}
        return jsonify(results)


def main():
    m.create_db()
    api = Api(app)
    api.add_resource(Contributors, "/contributors/")
    api.add_resource(Profile, "/contributors/<name>/")
    api.add_resource(List, "/tasks/<sort>/")
    app.run(port=5000, debug=True)
    db.close()


if __name__ == "__main__":
    main()
