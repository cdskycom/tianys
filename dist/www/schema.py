# -*- coding: utf-8 -*-
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from orm import User, MathOralCal

# class SupportProviderSchema(ModelSchema):
# 	class Meta:
# 		model = SupportProvider
# 		dateformat = '%Y-%m-%dT%H:%M:%S'

# 	users = fields.Nested('UserSchema', many=True, only=["account","name","phone","email"])

class UserSchema(ModelSchema):
	class Meta:
		model = User
		dateformat = '%Y-%m-%dT%H:%M:%S'

class MathOralCalSchema(ModelSchema):
	class Meta:
		model = MathOralCal
		dateformat = '%Y-%m-%dT%H:%M:%S'
	student = fields.Nested(UserSchema, exclude=("password",))



