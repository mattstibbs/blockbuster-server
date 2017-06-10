# 3rd Party Imports
from flask import request, Response, make_response
from flask import jsonify
from functools import wraps
import logging

# Local Imports
from blockbuster import app
import bb_auditlogger
from blockbuster import bb_request_processor
from blockbuster import bb_api_request_processor
from blockbuster import bb_security

# Set up auditor
bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'STARTUP', 'Application Startup')

logger = logging.getLogger(__name__)


def add_response_headers(headers=None):
    """This decorator adds the headers passed in to the response"""
    if headers is None:
        headers = {}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


def allow_cors(f):
    """This decorator passes X-Robots-Tag: noindex"""
    @wraps(f)
    @add_response_headers({'Access-Control-Allow-Origin': '*'})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


# Following methods provide the endpoint authentication.
# Authentication is applied to an endpoint by decorating the route with @requires_auth
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth:
            print(str.format("API User: {0}", auth.username))
        if not auth or not check_auth(auth.username, auth.password):
            return user_must_authenticate()
        return f(*args, **kwargs)
    return decorated


def check_auth(username, password):
    successful = bb_security.credentials_are_valid(username, password)
    print(str.format("Authentication Successful: {0}", successful))
    return successful


def user_must_authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


# Routes
# The /status endpoint is not secured as it does not return any data other than service status
@app.route("/status/", methods=['GET'])
def get_status():
    status = bb_api_request_processor.APIRequestProcessor().service_status_get()
    bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'GET_STATUS', status)
    return status


@app.route("/api/v1.0/InboundSMS/", methods=['POST'])
@requires_auth
def post_inboundsms():
    bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'POST_INBOUNDSMS', request.form['Body'])
    return bb_request_processor.process_twilio_request(request)


# API Routes
@app.route("/api/v1.0/stats/", methods=['GET'])
@requires_auth
@allow_cors
def get_stats():
    result = bb_api_request_processor.APIRequestProcessor()\
        .service_stats_get()
    bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'GET_STATS', str(result))
    return jsonify(stats=result)


@app.route("/api/v1.0/cars/", methods=['GET'])
@requires_auth
@allow_cors
def uri_get_cars():
    result = bb_api_request_processor.APIRequestProcessor()\
        .cars_getall()
    return jsonify(cars=result)


@app.route("/api/v1.0/cars/<registration>", methods=['GET'])
@requires_auth
@allow_cors
def uri_get_registrations(registration):
    result = bb_api_request_processor.APIRequestProcessor().cars_get(registration)
    return jsonify(result)


@app.route("/api/v1.0/blocks/", methods=['GET'])
@requires_auth
def uri_get_blocksall():
    result = bb_api_request_processor.APIRequestProcessor().blocks_getall()
    return jsonify(blocks=result)


@app.route("/api/v1.0/status/<requestermobile>", methods=['GET'])
@requires_auth
def uri_get_status(requestermobile):
    return jsonify(bb_api_request_processor.APIRequestProcessor().status_get(requestermobile))


@app.route("/api/v1.0/smslogs/", methods=['GET'])
@requires_auth
@allow_cors
def uri_get_smslogs():
    result = bb_api_request_processor.APIRequestProcessor().smslogs_get()
    return jsonify(logs=result)


@app.route("/api/v1.0/logs/", methods=['GET'])
@requires_auth
@allow_cors
def uri_get_logs():
    result = bb_api_request_processor.APIRequestProcessor().logs_get()
    return jsonify(logs=result)


# Routes that I haven't finished yet...
@app.route("/api/v1.0/blocks", methods=['POST'])
@requires_auth
def uri_post_blocks():
    content = request.get_json()
    block = content['block']
    blocker_reg = block['blocker_reg']
    blocked_reg = block['blocked_reg']
    response = blocker_reg + " has blocked in " + blocked_reg
    return response, 200
