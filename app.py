from flask import Flask, request,jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("Rotating_log")
logger.setLevel(logging.DEBUG)


def create_rotating_log():

    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

    file_handler = TimedRotatingFileHandler(filename='AppError.log', when="d", interval=1)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/flasksql'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)


class Employee(db.Model):

    emp_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    second_name = db.Column(db.String)
    email_address = db.Column(db.String, nullable=False)
    designation = db.Column(db.String, nullable=False)
    project_name = db.Column(db.String, nullable=False)
    manager = db.Column(db.String, nullable=False)
    project = db.relationship('Projects', backref='employee', lazy=True)
    timesheet = db.relationship('Timesheet', backref='employee', lazy=True)

    def __init__(self, emp_id, first_name, second_name, designation, project_name, manager):
        self.emp_id = emp_id
        self.first_name = first_name
        self.second_name = second_name
        self.email_address = first_name + '.' + second_name + '@company.in'
        self.designation = designation
        self.project_name = project_name
        self.manager = manager

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


@app.route("/employee_add", methods=['POST'])
def emp_add():
    emp_details = request.json
    entry = Employee(emp_id=emp_details["emp_id"],
                     first_name=emp_details["first_name"],
                     second_name=emp_details["second_name"],
                     designation=emp_details["designation"],
                     project_name=emp_details["project_name"],
                     manager=emp_details["manager"])
    try:
        db.session.add(entry)
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return "Employee already exists"
    else:
        logger.debug("Employee Details of emp_id {} added successfully".format(emp_details["emp_id"]))
        return "Employee Details of emp_id {} added successfully".format(emp_details["emp_id"])


@app.route("/employee_update", methods=['POST'])
def emp_update():
    emp_details = request.json
    try:
        service = db.session.query(Employee).filter(Employee.emp_id == emp_details["emp_id"]).first()
        service.first_name = emp_details["first_name"]
        service.second_name = emp_details["second_name"]
        service.email_address = emp_details["email_address"]
        service.designation = emp_details["designation"]
        service.project_name = emp_details["project_name"]
        service.manager = emp_details["manager"]
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    except AttributeError:
        logger.error(AttributeError)
        return "No such Employee id"
    else:
        logger.debug("Employee details of Emp_id {} updated successfully".format(emp_details["emp_id"]))
        return "Employee details of Emp_id {} updated successfully".format(emp_details["emp_id"])


@app.route("/employee_get", methods=['GET'])
def emp_get():
    emp_details = request.json
    try:
        service = db.session.query(Employee).filter(Employee.emp_id == emp_details["emp_id"]).first().as_dict()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    except AttributeError:
        logger.error(AttributeError)
        return "No such Employee id"
    else:
        logger.debug("GET request of Employee details of Emp_id {} executed successfully".format(emp_details["emp_id"]))
        return service


@app.route("/employee_delete", methods=['DELETE'])
def emp_delete():
    emp_details = request.json
    try:
        service = db.session.query(Employee).filter(Employee.emp_id == emp_details["emp_id"]).first()
        if service is not None:
            print(emp_details["emp_id"])
            db.session.delete(service)
            db.session.commit()
        else:
            return "No such Employee id"
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    else:
        logger.debug("Employee Details of emp_id {} deleted successfully".format(emp_details["emp_id"]))
        return "Employee Details of emp_id {} deleted successfully".format(emp_details["emp_id"])


class Projects(db.Model):

    prj_id = db.Column(db.Integer, nullable=False, primary_key=True)
    prj_name = db.Column(db.String, nullable=False)
    prj_manager_id = db.Column(db.Integer, db.ForeignKey('employee.emp_id'), nullable=False)
    prj_location = db.Column(db.String, nullable=False)
    prj_start_date = db.Column(db.Date,nullable=False)
    prj_end_date = db.Column(db.Date, nullable=False)
    timesheet_p = db.relationship('Timesheet', backref='project', lazy=True)

    def __init__(self, prj_id, prj_name, prj_location, prj_start_date, prj_end_date, prj_manager_id):
        self.prj_id = prj_id
        self.prj_name = prj_name
        self.prj_location = prj_location
        self.prj_start_date = prj_start_date
        self.prj_end_date = prj_end_date
        self.prj_manager_id = prj_manager_id

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


@app.route("/projects_add", methods=['POST'])
def prj_details_add():
    prj_details_dict = request.json
    entry = Projects(prj_id=prj_details_dict["prj_id"],
                     prj_name=prj_details_dict["prj_name"],
                     prj_location=prj_details_dict["prj_location"],
                     prj_start_date=prj_details_dict["prj_start_date"],
                     prj_end_date=prj_details_dict["prj_end_date"],
                     prj_manager_id=prj_details_dict["prj_manager_id"])
    try:
        db.session.add(entry)
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    else:
        logger.debug("Project Details of project id {} Added Successfully".format(prj_details_dict["prj_id"]))
        return "Project Details of project id {} Added Successfully".format(prj_details_dict["prj_id"])


@app.route("/projects_update", methods=['POST'])
def prj_details_update():
    prj_details_dict = request.json
    try:
        service = db.session.query(Projects).filter(Projects.prj_id == prj_details_dict["prj_id"]).first()
        service.prj_name = prj_details_dict["prj_name"]
        service.prj_location = prj_details_dict["prj_location"]
        service.prj_start_date = prj_details_dict["prj_start_date"]
        service.prj_end_date = prj_details_dict["prj_end_date"]
        service.prj_manager_id = prj_details_dict["prj_manager_id"]
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    except AttributeError:
        logger.error(AttributeError)
        return "No such project id"
    else:
        logger.debug("Project Details of project id {} updated Successfully".format(prj_details_dict["prj_id"]))
        return "Project Details of project id {} updated Successfully".format(prj_details_dict["prj_id"])


@app.route("/projects_get", methods=['GET'])
def prj_details_get():
    prj_details_dict = request.json
    try:
        service = db.session.query(Projects).filter(Projects.prj_id == prj_details_dict["prj_id"]).first().as_dict()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    except AttributeError:
        logger.error(AttributeError)
        return "No such Project id"
    else:
        logger.debug("GET request of project details of project id {} executed successfully".format(prj_details_dict["prj_id"]))
        return service


@app.route("/projects_delete", methods=['DELETE'])
def prj_details_delete():
    prj_details_dict = request.json
    try:
        service = db.session.query(Projects).filter(Projects.prj_id == prj_details_dict['prj_id']).first()
        if service is not None:
            db.session.delete(service)
            db.session.commit()
        else:
            return "No such project id"
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    else:
        logger.debug("Project Details of project id {} deleted successfully".format(prj_details_dict["prj_id"]))
        return "Project Details of project id {} deleted successfully".format(prj_details_dict["prj_id"])


class Timesheet(db.Model):
    s_no = db.Column(db.Integer, nullable=False, primary_key=True )
    emp_id = db.Column(db.Integer, db.ForeignKey('employee.emp_id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    shift = db.Column(db.Integer, nullable=False)
    prj_id = db.Column(db.Integer, db.ForeignKey('projects.prj_id'), nullable=False)

    def __init__(self, emp_id, work_date, hours, shift, prj_id):
        self.emp_id = emp_id
        self.work_date = work_date
        self.hours = hours
        self.shift = shift
        self.prj_id = prj_id

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    @staticmethod
    def is_workday(dates):
        for day in dates:
            day = (datetime.strptime(day, '%Y-%m-%d')).date()
            if day.weekday() == 5 or day.weekday() == 6:
                return False, "{} is not a workday. Please check your entry.".format(day)
        return True, "Workday it is"

    @staticmethod
    def check_already_exists(emp_id, weekly_details):
        dates = []
        for entry in range(len(weekly_details)):
            dates.append(weekly_details[entry]['work_date'])
        print(dates)

        status, message = Timesheet.is_workday(dates)
        if not status:
            return False,message

        for entry in dates:
            try:
                service = db.session.query(Timesheet).filter(Timesheet.work_date == entry,
                                                             Timesheet.emp_id == emp_id).all()
            except SQLAlchemyError as e:
                logger.error(str(e.__dict__['orig']))
                return str(e.__dict__['orig'])
            else:
                if len(service) > 0:
                    return False, "Entry already exists"
        return True, "Entry Doesn't Exist"

    @staticmethod
    def check_hours(weekly_details):
        dates = {}
        for i in range(len(weekly_details)):
            dates[str(weekly_details[i]['work_date'])] = 0

        for i in range(len(weekly_details)):
            dates[str(weekly_details[i]['work_date'])] = int(dates[str(weekly_details[i]['work_date'])]) + int(
                weekly_details[i]['hours'])

        for val in dates:
            if dates[val] > 8:
                return False, "Work hours cant be more than 8 hours per day. Recheck your entry for date {}".format(val)
        return True, "All good"


@app.route('/timesheet_add', methods=["POST"])
def timesheet_add():
    time_sheet = request.json
    weekly_details = time_sheet['weekly_details']

    # checking if the entry already exists/dates are workdays
    status, message = Timesheet.check_already_exists(time_sheet['emp_id'], weekly_details)
    if not status:
        return message

    # checking if hours are less than 8 hours
    status, message = Timesheet.check_hours(weekly_details)
    if not status:
        return message

    # creating entries and adding to the database
    for i in range(len(weekly_details)):
        entry = Timesheet(emp_id=time_sheet['emp_id'],
                          work_date=time_sheet['weekly_details'][i]['work_date'],
                          hours=time_sheet['weekly_details'][i]['hours'],
                          shift=time_sheet['weekly_details'][i]['shift'],
                          prj_id=time_sheet['weekly_details'][i]['prj_id'])
        try:
            db.session.add(entry)
            db.session.commit()
        except SQLAlchemyError as e:
            logger.error(str(e.__dict__['orig']))
            return str(e.__dict__['orig'])
    logger.debug("Timesheet entry added successfully for employee id {}".format(time_sheet["emp_id"]))
    return "Timesheet entry added successfully for employee id {}".format(time_sheet["emp_id"])


@app.route('/timesheet_update', methods=["POST"])
def timesheet_update():
    time_sheet = request.json
    emp_id = time_sheet['emp_id']
    weekly_details = time_sheet['weekly_details']
    status, message = Timesheet.check_already_exists(emp_id, weekly_details)  # checking if the entry already exists
    if status:
        return message
    for i in range(len(weekly_details)):
        list_entries = []
        dict_entries = {}
        dict_entries['work_date'] = weekly_details[i]['work_date']
        dict_entries['hours'] = weekly_details[i]['hours']
        list_entries.append(dict_entries)
        service = db.session.query(Timesheet).filter(
            Timesheet.work_date == weekly_details[i]['work_date'],
            Timesheet.emp_id == emp_id).all()
        update_dates = [row.as_dict() for row in service]
        list_entries.extend(update_dates)
        status, message = Timesheet.check_hours(list_entries)
        if not status:
            return message
        service1 = db.session.query(Timesheet).filter(Timesheet.work_date == weekly_details[i]['work_date'],
                                                      Timesheet.emp_id == emp_id).first()
        service1.hours = service1.hours + int(weekly_details[i]['hours'])
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    else:
        logger.debug("Timesheet Entry updated successfully for employee {}".format(emp_id))
        return "Timesheet Entry updated successfully for employee {}".format(emp_id)


@app.route("/timesheet_get", methods=['GET'])
def timesheet_get():
    time_sheet = request.json
    try:
        service = db.session.query(Timesheet).filter(Timesheet.emp_id == time_sheet["emp_id"]).all()
        if len(service) == 0:
            return "No such entries"
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    except AttributeError:
        logger.error(AttributeError)
        return "No such entries"
    else:
        list_of_dates = [row.as_dict() for row in service]
        logger.debug("GET request of Timesheet details of emp_id {} executed successfully".format(time_sheet["emp_id"]))
        return jsonify(list_of_dates)


@app.route('/timesheet_delete', methods=["DELETE"])
def timesheet_delete():
    time_sheet = request.json
    dates = time_sheet['dates']
    try:
        for i in dates:
            service = db.session.query(Timesheet).filter(Timesheet.work_date == i,
                                                         Timesheet.emp_id == time_sheet['emp_id']).first()
            if service is None:
                return "No such entries"
            db.session.delete(service)
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    except AttributeError:
        logger.error(AttributeError)
        return "No such entries"
    else:
        logger.debug("Timesheet Details of emp_id {} deleted successfully for the requested dates {}".format(time_sheet["emp_id"],dates))
        return "Timesheet Details of emp_id {} deleted successfully for the requested dates {}".format(time_sheet["emp_id"],dates)


class ProjectCostPerHour(db.Model):

    prj_id = db.Column(db.Integer, nullable=False, primary_key=True)
    associate = db.Column(db.Integer, nullable=False)
    senior_associate = db.Column(db.Integer, nullable=False)
    analyst = db.Column(db.Integer, nullable=False)
    senior_analyst = db.Column(db.Integer, nullable=False)

    def __init__(self, prj_id, associate, senior_associate, analyst, senior_analyst):
        self.prj_id = prj_id
        self.associate = associate
        self.senior_associate = senior_associate
        self.analyst = analyst
        self.senior_analyst = senior_analyst

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


@app.route('/project_cost_add', methods=['POST'])
def prj_cost_add():
    prj_cost = request.json
    entry = ProjectCostPerHour(prj_id=prj_cost["prj_id"],
                               associate=prj_cost["associate"],
                               senior_associate=prj_cost["senior_associate"],
                               analyst=prj_cost["analyst"],
                               senior_analyst=prj_cost["senior_analyst"])
    try:
        db.session.add(entry)
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    else:
        logger.debug("Project cost for project id {} added successfully".format(prj_cost["prj_id"]))
        return "Project cost for project id {} added successfully".format(prj_cost["prj_id"])


@app.route('/project_cost_update', methods=['POST'])
def prj_cost_update():
    prj_cost = request.json
    try:
        service = db.session.query(ProjectCostPerHour).filter(ProjectCostPerHour.prj_id == prj_cost["prj_id"]).first()
        service.associate = prj_cost["associate"]
        service.senior_associate = prj_cost["senior_associate"]
        service.analyst = prj_cost["analyst"]
        service.senior_analyst = prj_cost["senior_analyst"]
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    except AttributeError:
        logger.error(AttributeError)
        return "No such entries"
    else:
        logger.debug("Project cost for project id {} updated successfully".format(prj_cost["prj_id"]))
        return "Project cost for project id {} updated successfully".format(prj_cost["prj_id"])


@app.route("/project_cost_get", methods=['GET'])
def prj_cost_get():
    prj_cost = request.json
    try:
        service = db.session.query(ProjectCostPerHour).filter(ProjectCostPerHour.prj_id == prj_cost["prj_id"]).first().as_dict()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    except AttributeError:
        logger.error(AttributeError)
        return "No such Project id"
    else:
        logger.debug("GET request of project cost details of project id {} executed successfully".format(prj_cost["prj_id"]))
        return jsonify(service)


@app.route('/project_cost_delete', methods=['DELETE'])
def prj_cost_delete():
    prj_cost = request.json
    try:
        service = db.session.query(ProjectCostPerHour).filter(ProjectCostPerHour.prj_id == prj_cost["prj_id"]).first()
        if service is None:
            return "No such project id"
        db.session.delete(service)
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(str(e.__dict__['orig']))
        return str(e.__dict__['orig'])
    except (AttributeError, TypeError) as e:
        logger.error(e)
        return "No such project id_"
    else:
        logger.debug("Project cost for project id {} deleted successfully".format(prj_cost["prj_id"]))
        return "Project cost for project id {} deleted successfully".format(prj_cost["prj_id"])


if __name__ == '__main__':

    create_rotating_log()
    db.create_all()
    app.run()
