from flask import Response, json


def handle_result(result, schema=None, many=False):
    if schema:
        return Response(
            schema(many=many).dumps(result.value),
            status=result.status_code,
            mimetype="application/json",
        )
    else:
        return Response(
            json.dumps(result.value),
            status=result.status_code,
            mimetype="application/json",
        )
