from flask import Flask, request, abort
from flask_restful import Resource, Api
from program import Program
from multiprocessing import Process, Value
from ctypes import c_bool
import re

class ProgramProcess(Process):

    def __init__(self, name, data):
        super().__init__()
        self.running = Value(c_bool, True)
        self.program = Program(name=name, data=data)

    def run(self):
        while self.program.running and self.running.value:
            self.program.step()
        self.stop()
    
    def stop(self):
        self.running.value = False
        # self.program.terminate()

binaries = {}
BUILTIN = ['idle', 'rainbow']
for name in BUILTIN:
    with open(f'programs/{name}.bin', 'rb') as binary:
        binaries[name] = binary.read()

current = ProgramProcess(name='idle', data=binaries['idle'])

app = Flask(__name__)
api = Api(app)

class DashboardResource(Resource):
    def get(self):
        return "Hello, world!"

api.add_resource(DashboardResource, '/')

class StatusResource(Resource):
    # GET /status/
    # get server status
    def get(self):
        return f"GET /status"

api.add_resource(StatusResource, '/status')

class ProgramsResource(Resource):
    # GET /programs
    # list all programs
    def get(self):
        global binaries
        return {'programs': list(binaries.keys())}

api.add_resource(ProgramsResource, '/programs')

class ModifyProgramResource(Resource):
    # GET /programs/<name>
    # download a program
    def get(self, name):
        global binaries
        if name not in binaries:
            abort(404, "Program not found.")
        return binaries[name]

    # POST /programs/<name>
    # upload a program
    def post(self, name):
        global binaries
        if 'data' not in request.form:
            abort(400, "Required data header not found.")
        if name in BUILTIN:
            abort(403, f"Program {name} cannot be modified.")
        binaries[name] = request.form['data']
        return '', 204

    # DELETE /programs/<name>
    # delete a program
    def delete(self, name):
        global binaries
        if name not in binaries:
            abort(404, "The program does not exist.")
        del binaries[name]
        return '', 204

api.add_resource(ModifyProgramResource, '/programs/<string:name>')

class ExecuteResource(Resource):
    # GET /execute
    # get running program name
    def get(self):
        global current
        return current.program.name

api.add_resource(ExecuteResource, '/execute')

class ExecuteProgramResource(Resource):
    # POST /execute/<name>
    # set running program
    def post(self, name):
        global binaries, current
        if name not in binaries:
            abort(404, "The program does not exist.")
        current.stop()  # kill previous program
        current.join()  # make sure the process has ended
        current = ProgramProcess(name=name, data=binaries[name])
        current.start()
        return '', 204

api.add_resource(ExecuteProgramResource, '/execute/<string:name>')

class ColorResource(Resource):
    color_pattern = re.compile(r'^[0-9a-f]{6}$')

    # POST /color/<value>
    # set running program to run solid color
    def post(self, value):
        global binaries, current
        if not ColorResource.color_pattern.match(value):
            abort(404, "Invalid color code.")
        value = int(value, 16)
        r, g, b = ((value >> 16) & 0xff, (value >> 8) & 0xff, value & 0xff)
        current.stop()  # kill previous program
        current.join()  # make sure the process has ended
        current = ProgramProcess(name='color', data=bytes(
            [0x31,    r,    g,    b,
             0x00, 0xe7, 0x11, 0x0a,
             0xf9, 0x40, 0x06, 0x00]
        ))
        current.start()
        return '', 204

api.add_resource(ColorResource, '/color/<string:value>')

if __name__ == '__main__':
    current.start()
    app.run()