# -*- coding: utf-8 -*-
import sys, logging, json, datetime
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship, sessionmaker, joinedload, subqueryload
from sqlalchemy import create_engine, text, Column, Integer, String, Text, DateTime, Table, ForeignKey, func

from contextlib import contextmanager
from collections import Iterable
from const import const
import pdb


Base = declarative_base()
Session = sessionmaker()

def get_dbengine( **kw):
	logging.info('create database engine')
	user=kw['user']
	db=kw['db']
	host=kw.get('host','localhost')
	password=kw['password']
	charset=kw.get('charset', 'utf8')

	connstr = 'mysql+pymysql://%s:%s@%s/%s?charset=%s' % (user, password, host, db, charset)

	global __engine 
	__engine = create_engine(connstr)
	Session.configure(bind=__engine)

@contextmanager
def session_scope():
	session = Session()
	try:
		yield session
		session.commit()
	except:
		session.rollback()
		raise
	finally: 
		session.close()


# 用户model
class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	account = Column(String(45))
	password = Column(String(45))
	name = Column(String(45))
	role = Column(String(45))
	is_admin = Column(Integer)
	

	def __init__(self, account, password, name, role, is_admin):
		self.account = account
		self.password = password
		self.name = name
		self.role = role
		self.is_admin = is_admin
		
	# 查询用户信息，支持提供字符串过滤参数(filter1, filter2 ...)
	@classmethod
	def getAll(self, *filters):
		'返回所有的用户'
		
		with session_scope() as session:

			#userCount = session.query(User).filter(*filters).count()
				
			users = session.query(User).filter(*filters).all()
			result = []
			
			for user in users:
				result.append(user.to_dict())
			#result = query_to_dict(users)
		
		return result
	
	def to_dict(self):
		from schema import UserSchema
		user_schema = UserSchema()
		return user_schema.dump(self).data

	@classmethod
	def getUserById(self, id):
		
		with session_scope() as session:
			
			user = session.query(User).filter(User.id == id).one()
			# result = query_to_dict(user)
			result = user.to_dict()
		result['password'] = '******'
		return 	result
	
	@classmethod
	def updateUser(self, id, name, role, is_admin):
		
		with session_scope() as session:
			
			user = session.query(User).filter(User.id == id).one()
			# logging.info('修改前的user： %s : %s : %s' % (user.account, user.name, user.password))
			user.name = name
			user.is_admin = is_admin
			user.role = role	
			session.commit()
			result = user.to_dict()
		return result	

	@classmethod
	def resetUser(self, id, password):
		
		with session_scope() as session:
			
			user = session.query(User).filter(User.id == id).one()
			logging.info('修改前的user： %s : %s : %s' % (user.account, user.name, user.password))
			logging.info('密码: %s' % password)
			user.password = password
			session.commit()
			result = user.to_dict()
		return result	

	@classmethod
	def deleteUser(self, id):
		
		with session_scope() as session:
			
			user = session.query(User).filter(User.id == id).one()
			
			session.delete(user)
		
		return True	
	
	def save(self):
		with session_scope() as session:
			session.add(self)
			session.commit()

	def __str__(self):
		return '<User(id: %s, account: %s, name: %s)>' % (self.id, self.account, self.name)

class MathOralCal(Base):
	__tablename__ = 'math_oral_cal'
	id = Column(Integer, primary_key=True)
	user = Column(Integer, ForeignKey('user.id'))
	cal_date = Column(DateTime)
	consuming_time = Column(Integer)
	error_count = Column(Integer)
	createtime = Column(DateTime)
	modifytime = Column(DateTime)

	student = relationship('User')

	def __init__(self, user, cal_date, consuming_time, error_count, createtime, modifytime):
		self.user = user
		self.cal_date = cal_date
		self.consuming_time = consuming_time
		self.error_count = error_count
		self.createtime = createtime
		self.modifytime = modifytime

	@classmethod
	def getAll(self, *filters, orderby='cal_date'):

		with session_scope() as session:
				
			cals = session.query(MathOralCal).filter(*filters).order_by(orderby).all()
			result = []
			
			for cal in cals:
				result.append(cal.to_dict())
		
		return result

	@classmethod
	def updateCal(self, id, consumingtime, errorcount):

		with session_scope() as session:
				
			cal = session.query(MathOralCal).filter(MathOralCal.id==id).one()
			cal.consuming_time = consumingtime
			cal.error_count = errorcount
			session.commit()
		
		return 

	@classmethod
	def getStatistic(self, *filters, orderby='desc'):
		orderByStr = 'completed_days desc,error_count_sum,consuming_time_sum' + ' ' + orderby

		with session_scope() as session:
			result = []
			
			errorCals = session.query(func.sum(MathOralCal.error_count).label(
				'error_count_sum'),func.sum(MathOralCal.consuming_time).label(
				'consuming_time_sum'),func.count(MathOralCal.consuming_time).label('completed_days'),MathOralCal.user).filter(*filters).group_by(MathOralCal.user).order_by(orderByStr).all()

			# timeCals = session.query(func.sum(MathOralCal.consuming_time).label(
			# 	'consuming_time_sum'),MathOralCal.user).filter(*filters).group_by(MathOralCal.user).order_by(orderbyStr).all()
			
			for cal in errorCals:
				
				# timeCals = session.query(func.sum(MathOralCal.consuming_time).label('consuming_time_sum')).filter(*filters,MathOralCal.user==cal[1]).group_by(MathOralCal.user).scalar()
				# days = session.query(func.count(MathOralCal.consuming_time)).filter(*filters,MathOralCal.user==cal[1]).group_by(MathOralCal.user).scalar()
				user = User.getUserById(cal[3])
						
				result.append(dict(name=user['name'],error=int(cal[0]),time=int(cal[1]),days=int(cal[2])))
			
				
		return result

	def to_dict(self):
		from schema import MathOralCalSchema
		cal_schema = MathOralCalSchema()
		return cal_schema.dump(self).data

	def save(self):
		with session_scope() as session:
			session.add(self)
			session.commit()



# 创建数据库-初始化数据
def create_db():
	try:
		logging.info('create db schema...')
		Base.metadata.create_all(__engine)
		logging.info('create db success')
	except Exception as e:
		logging.info('create db failed: %s' % e)

if __name__ == '__main__':
	from config import configs
	get_dbengine(**configs.db)
	if len(sys.argv) > 1 and sys.argv[1] == '--createdb':
		print(sys.argv[1])
		create_db()
	# print(InspectionType.getTypes())
	

	print(InspectionItem.getItems())

