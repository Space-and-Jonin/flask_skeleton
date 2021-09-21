import pinject
from flask import Blueprint, request

from app.controllers import EmployeeController
from core import handle_result
from core import validator, auth_role
from app.repositories import EmployeeRepository, TokenRepository
from app.schema import (
    EmployeeCreateSchema,
    EmployeeSchema,
    EmployeeUpdateSchema,
    PinResetRequestSchema,
    PinResetSchema,
    TokenSchema,
    LoginSchema,
    ResendTokenSchema,
)
from app.services import AuthService

employee = Blueprint("employee", __name__)

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[EmployeeController, EmployeeRepository, AuthService, TokenRepository],
)
employee_controller = obj_graph.provide(EmployeeController)


@employee.route("/", methods=["POST"])
@auth_role()
@validator(schema=EmployeeCreateSchema)
def create_employee():
    """
    ---
    post:
      description: creates a new employee
      requestBody:
        required: true
        content:
          application/json:
            schema: EmployeeCreateSchema
      responses:
        '201':
          description: returns an employee object
          content:
            application/json:
              schema: EmployeeSchema
      tags:
          - Authentication
    """

    data = request.json
    result = employee_controller.create(data)
    return handle_result(result, schema=TokenSchema)


@employee.route("/accounts/<string:employee_id>", methods=["PATCH"])
@auth_role()
@validator(schema=EmployeeUpdateSchema)
def update_employee(employee_id):
    """
    ---
    patch:
      description: updates an employee with id specified in path
      parameters:
        - in: path
          name: employee_id
          required: true
          schema:
            type: string
          description: The employee ID
      requestBody:
        required: true
        content:
            application/json:
                schema: EmployeeUpdateSchema
      security:
        - bearerAuth: []
      responses:
        '200':
          description: returns an employee
          content:
            application/json:
              schema: EmployeeSchema
      tags:
          - Employee
    """

    data = request.json
    result = employee_controller.update(employee_id, data)
    return handle_result(result, schema=EmployeeSchema)


@employee.route("/accounts/<string:employee_id>", methods=["GET"])
@auth_role()
def show_employee(employee_id):
    """
    ---
    get:
      description: returns an employee with id specified in path
      parameters:
        - in: path
          name: employee_id
          required: true
          schema:
            type: string
          description: The employee ID
      security:
        - bearerAuth: []
      responses:
        '200':
          description: returns an employee
          content:
            application/json:
              schema: EmployeeSchema
      tags:
          - Employee
    """
    result = employee_controller.show(employee_id)
    return handle_result(result, schema=EmployeeSchema)


@employee.route("/accounts/<string:employee_id>", methods=["DELETE"])
@auth_role()
def delete_employee(employee_id):
    """
    ---
    delete:
      description: deletes a employee with id specified in path
      parameters:
        - in: path
          name: employee_id
          required: true
          schema:
            type: string
          description: The employee ID
      security:
        - bearerAuth: []
      responses:
        '204':
          description: returns nil
      tags:
          - Employee
    """
    result = employee_controller.delete(employee_id)
    return handle_result(result)


@employee.route("/token_login", methods=["POST"])
@validator(schema=LoginSchema)
def login_user():
    """
    ---
    post:
      description: logs in a customer
      requestBody:
        required: true
        content:
            application/json:
                schema: LoginSchema
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: TokenSchema
      tags:
          - Authentication
    """

    data = request.json
    result = employee_controller.login(data)
    return handle_result(result, schema=TokenSchema)


@employee.route("/change-password", methods=["POST"])
# @validator(schema=PinChangeSchema)
def change_password(user_id):
    """
    ---
    post:
      description: changes a employee's password
      requestBody:
        required: true
        content:
            application/json:
                schema: PinChangeSchema
      security:
        - bearerAuth: []
      responses:
        '204':
          description: returns nil
      tags:
          - Authentication
    """
    data = request.json
    data["employee_id"] = user_id
    result = employee_controller.change_password(data)
    return handle_result(result)


@employee.route("/request-reset", methods=["POST"])
@validator(schema=PinResetRequestSchema)
def forgot_password():
    """
    ---
    post:
      description: requests a reset of a employee's password
      requestBody:
        required: true
        content:
            application/json:
                schema: PinResetRequestSchema
      responses:
        '200':
          description: returns a uuid (employee's id)
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: uuid
                    example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
      tags:
          - Authentication
    """
    data = request.json
    result = employee_controller.request_password_reset(data)
    return handle_result(result)


@employee.route("/reset-password", methods=["POST"])
@validator(schema=PinResetSchema)
def reset_password():
    """
    ---
    post:
      description: confirms reset of an employee's password
      requestBody:
        required: true
        content:
            application/json:
                schema: PinResetSchema
      responses:
        '204':
          description: returns nil
      tags:
          - Authentication
    """
    data = request.json
    result = employee_controller.reset_password(data)
    return handle_result(result)


@employee.route("/resend-token", methods=["POST"])
@validator(schema=ResendTokenSchema)
def resend_token():
    """
    ---
    post:
      description: creates a new token
      requestBody:
        required: true
        content:
          application/json:
            schema: ResendTokenSchema
      responses:
        '200':
          description: uuid of the user
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: uuid
                    example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
      tags:
          - Authentication
    """

    data = request.json
    result = employee_controller.resend_token(data.get("token_id"))
    return handle_result(result)
