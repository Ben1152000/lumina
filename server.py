from flask import Flask, request, abort
from flask_restful import Resource, Api
from program import Program

app = Flask(__name__)
api = Api(app)

programs = {
    "idle": Program(
        name="idle",
        data="",
        locked=True
    )
}

current_running_program = programs["idle"]

class DashboardResource(Resource):
    def get(self):
        global programs, current_running_program
        return "Hello, world!"

api.add_resource(DashboardResource, '/')

class StatusResource(Resource):
    # GET /status/
    # get server status
    def get(self):
        global programs, current_running_program
        return f"GET /status"

api.add_resource(StatusResource, '/status')

class ProgramsResource(Resource):
    # GET /programs
    # list all programs
    def get(self):
        global programs, current_running_program
        return {'programs': list(programs.keys())}

api.add_resource(ProgramsResource, '/programs')

class ModifyProgramResource(Resource):
    # GET /programs/<program_name>
    # download a program
    def get(self, program_name):
        global programs, current_running_program
        if program_name not in programs:
            abort(404, "Program not found.")
        return programs[program_name].data

    # POST /programs/<program_name>
    # upload a program
    def post(self, program_name):
        global programs, current_running_program
        if 'data' not in request.form:
            abort(400, "Required data header not found.")
        if program_name in programs and programs[program_name].locked:
            abort(403, f"Program {program_name} cannot be modified.")
        programs[program_name] = Program(
            name=program_name,
            data=request.form['data']
        )
        return '', 204

    # DELETE /programs/<program_name>
    # delete a program
    def delete(self, program_name):
        global programs, current_running_program
        if program_name not in programs:
            abort(404, "The program does not exist.")
        del programs[program_name]
        return '', 204

api.add_resource(ModifyProgramResource, '/programs/<string:program_name>')

class ExecuteResource(Resource):
    # GET /execute
    # get running program name
    def get(self):
        global programs, current_running_program
        return current_running_program.name

api.add_resource(ExecuteResource, '/execute')

class ExecuteProgramResource(Resource):
    # POST /execute/<program_name>
    # set running program
    def post(self, program_name):
        global programs, current_running_program
        if program_name not in programs:
            abort(404, "The program does not exist.")
        current_running_program = programs[program_name]
        return '', 204

api.add_resource(ExecuteProgramResource, '/execute/<string:program_name>')

if __name__ == '__main__':
    app.run()