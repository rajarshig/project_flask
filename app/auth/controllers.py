import json
from typing import Dict

from flask import (Blueprint, request)
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import success, failure

from app.auth.services import create_user, get_auth_token
from app.auth.validations import user_signup, user_login
from app.custom.pdf.pdf_maker import build_pdf
from app.utils.response_helper import pdf_response
from app.utils.validator import validator

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint("auth", __name__, url_prefix="/auth")


@mod_auth.route("/signup/", methods=["POST"])
@validator([user_signup])
def signup() -> Dict:
    """
       API to Sign up with a new user.
       :return: JSON response
    """
    payload = request.get_json()
    error, result = create_user(**payload)
    return success(data=result) if not error else failure(message=error)


@mod_auth.route("/login/", methods=["POST"])
@validator([user_login])
def login() -> Dict:
    """
       API to login user.
       :return: JSON response
    """
    payload = request.get_json()
    error, result = get_auth_token(**payload)
    return success(data=result) if not error else failure(message=error)


@mod_auth.route("/test/", methods=["GET"])
@jwt_required
def authenticate() -> Dict:
    """
       API to test AUTH.
       :return: JSON Response
    """
    user = json.loads(get_jwt_identity())
    return success(data=user, message="Authenticated")


@mod_auth.route("/pdf/", methods=["GET"])
@jwt_required
def generate_pdf() -> bytes:
    """
       API to test PDF.
       :return: PDF Response
    """
    template_name = 'welcome'
    user = json.loads(get_jwt_identity())
    pdf = build_pdf(template=template_name, template_data=user)
    return pdf_response(pdf=pdf, name=template_name)
