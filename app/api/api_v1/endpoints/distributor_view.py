import pinject
from flask import Blueprint, request

from app.controllers import DistributorController
from app.repositories import DistributorRepository
from app.services import RedisService
from core import validator, auth_role
from app.schema import (
    DistributorSchema,
    DistributorCreateSchema,
    DistributorUpdateSchema,
    DistributorShowSchema,
)
from core import handle_result

distributor = Blueprint("distributor", __name__)

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        DistributorController,
        DistributorRepository,
        RedisService,
    ],
)
distributor_controller = obj_graph.provide(DistributorController)


@distributor.route("/", methods=["POST"])
@validator(schema=DistributorCreateSchema)
# @auth_role()
def create_distributor():
    """
    ---
    post:
      description: creates a new distributor
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: DistributorCreateSchema
      responses:
        '201':
          description: returns a distributor
          content:
            application/json:
              schema: DistributorSchema
      tags:
          - Distributor
    """

    data = request.json
    result = distributor_controller.create(data)
    return handle_result(result, schema=DistributorSchema)


@distributor.route("/", methods=["GET"])
# @auth_role()
def get_all_distributors():
    """
    ---
    get:
      description: returns all distributors
      security:
        - bearerAuth: []
      responses:
        '200':
          description: returns all distributors
          content:
            application/json:
              schema:
                type: array
                items: DistributorSchema
      tags:
          - Distributor
    """

    result = distributor_controller.index()
    return handle_result(result, schema=DistributorSchema, many=True)


@distributor.route("/<string:distributor_id>", methods=["GET"])
@auth_role()
def get_distributor(distributor_id):
    """
    ---
    get:
      description: returns a distributor with id specified in path
      parameters:
        - in: path
          name: distributor_id   # Note the name is the same as in the path
          required: true
          schema:
            type: string
          description: The distributor ID
      responses:
        '200':
          description: returns a distributor
          content:
            application/json:
              schema: DistributorShowSchema
      tags:
          - Distributor
    """

    result = distributor_controller.show(distributor_id)
    return handle_result(result, schema=DistributorShowSchema)


@distributor.route("/<string:distributor_id>", methods=["PATCH"])
@validator(schema=DistributorUpdateSchema)
@auth_role()
def update_distributor(distributor_id):
    """
    ---
    patch:
      description: updates a distributor with id specified in path
      parameters:
        - in: path
          name: distributor_id   # Note the name is the same as in the path
          required: true
          schema:
            type: string
          description: The distributor ID
      requestBody:
        required: true
        content:
            application/json:
                schema: DistributorUpdateSchema
      security:
        - bearerAuth: []
      responses:
        '200':
          description: returns a template
          content:
            application/json:
              schema: DistributorSchema
      tags:
          - Distributor
    """

    data = request.json
    result = distributor_controller.update(distributor_id, data)
    return handle_result(result, schema=DistributorSchema)


@distributor.route("/<string:distributor_id>", methods=["DELETE"])
@auth_role()
def delete_distributor(distributor_id):
    """
    ---
    delete:
      description: deletes a distributor with id specified in path
      parameters:
        - in: path
          name: distributor_id
          required: true
          schema:
            type: string
          description: The distributor ID
      security:
        - bearerAuth: []
      responses:
        '200':
          description: returns nothing
          content:
            application/json:
              schema: DistributorSchema
      tags:
          - Distributor
    """
    result = distributor_controller.delete(distributor_id)
    return handle_result(result)
