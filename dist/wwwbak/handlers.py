# -*- coding: utf-8 -*-
from orm import User, MathOralCal
from coroweb import get, post
from apis import APIValueError, APIError
from sqlalchemy.orm.exc import NoResultFound
from aiohttp import web
from config import configs
from const import const
import sys, logging, hashlib, base64, re, json, time, datetime, math
import pdb

COOKIE_NAME = 'tianys'
_COOKIE_KEY = configs.session.secret
_WEEK = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
#每日值班的班次，最多6班
_SCHEDULENUM = ['first', 'second', 'third','forth','fifth','sixth']  

def user2cookie(user, max_age):
	'''
	Generate cookie str by user.
	'''
	# build cookie string by: id-expires-sha1
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user['account'], user['password'], expires, _COOKIE_KEY)
	L = [user['account'], expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)

def cookie2user(cookie_str):
	'''
	Parse cookie and load user if cookie is valid.
	'''
	if not cookie_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) != 3:
			return None
		account, expires, sha1 = L
		if int(expires) < time.time():
			return None
		filters = {User.account == account}
		users = User.getAll(*filters)
		user = users[0]
		if user is None:
			return None
		s = '%s-%s-%s-%s' % (user['account'], user['password'], expires, _COOKIE_KEY)
		if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
			logging.info('invalid sha1')
			return None
		user['password'] = '******'

		return user
	except Exception as e:
		logging.exception(e)
		return None

@get('/signin')
def signin():
	return {
		'__template__': 'signin.html'
	}
@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

@get('/')
def index(request):
	# logging.info('enter index...')
	# return {
	# 	'__template__': 'index.html'
	# }
	return {
		'__template__': 'report.html'
	}

@get('/view')
def viewCal(request):
	# logging.info('enter index...')
	# return {
	# 	'__template__': 'index.html'
	# }
	return {
		'__template__': 'view.html'
	}


@get('/manage')
def manageIndex(request):
	logging.info('enter index...')
	return {
		'__template__': 'managebase.html'
	}


@get('/api/users/{id}')
def api_get_users(request, *, id):
	filters = {User.id == id}
	users = User.getAll(*filters)
	for user in users:
		user['password'] = "******"
	
	return dict(user=users[0])

@get('/api/users')
def api_users():
	
	users = User.getAll()
	
	return dict(users=users)


_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


# 添加用户
@post('/api/users')
def api_register_user(*, account, password, name, role, is_admin):
	logging.info('添加用户的密码: %s' % password)
	if not account or not account.strip():
		raise APIValueError('account','账号不能为空')
	if re.search(r'[\-\%\']+',account):
		raise APIValueError('account','账号不能包含特殊字符')
	if not password or not _RE_SHA1.match(password):
		raise APIValueError('password','密码不能为空')
	if not name or not name.strip():
		raise APIValueError('name','用户名不能为空')
	if not role or not role.strip():
		raise APIValueError('role','用户角色不能为空')

	filters = {User.account == account}
	users = User.getAll(*filters)
	if len(users) > 0:
		raise APIError('添加用户失败', 'account', '用户账号已经存在')
	sha1_passwd = '%s:%s' % (account, password)
	user = User(account, hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), name, role, is_admin)
	user.save()
	res = dict()
	res['returncode'] = const.RETURN_OK
	res['message'] = '用户添加成功'
	# make session cookie:
	# r = web.Response()
	# 登录需要的设置cookie
	# r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	
	# r.body = json.dumps(orm_to_dict(user), ensure_ascii=False).encode('utf-8')
	return res

@post('/signin/authenticate')
def authenticate(*, account, password):
	logging.info('登录用户的密码： %s' % password)
	if not account:
		raise APIValueError('account', '账号不能为空.')
	if re.search(r'[\-\%\']+', account):
		raise APIValueError('account','账号不能包含特殊字符')
	if not password:
		raise APIValueError('password', '密码无效.')
	filters = {User.account == account}

	users = User.getAll(*filters)
	if len(users) == 0:
		raise APIValueError('account', '用户不存在.')
	user = users[0]
	# check passwd:
	sha1 = hashlib.sha1()
	sha1.update(account.encode('utf-8'))
	sha1.update(b':')
	sha1.update(password.encode('utf-8'))
	logging.info('密码in db: %s , 计算的 %s' %(user['password'], sha1.hexdigest()) )
	if user['password'] != sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid password.')
	# authenticate ok, set cookie:
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user['password'] = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r

@post('/manage/api/user/update/{id}')
def api_update_user(id, request, *, account, password, name, role, is_admin):
	if not account or not account.strip():
		raise APIValueError('account','账号不能为空')
	if not name or not name.strip():
		raise APIValueError('name','用户名不能为空')
	if not role or not role.strip():
		raise APIValueError('role','用户角色不能为空')
	user = User.getUserById(id)
	if user["account"] != account:
		raise APIValueError('account','登录账号不能修改')
	
	user = User.updateUser(id, name, is_admin, phone, email)
	user['password'] = "******"
	return  user

@post('/manage/api/user/reset/{id}')
def api_reset_user(id, request, *, newpassword):
	if not newpassword  or not newpassword.strip():
		raise APIValueError('account','密码不能为空')
	user = User.getUserById(id)
	if not user:
		raise APIValueError('account','获取用户信息失败')
	
	account = user['account']
	sha1_passwd = '%s:%s' % (account, newpassword)
	
	user = User.resetUser(id, hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest())
	user['password'] = "******"
	return  user


@post('/manage/api/user/delete/{id}')
def api_delete_user(id, request):
	res = dict()
	try:
		if User.deleteUser(id):
			res['returncode'] = 0
			res['message'] = '用户删除成功'
	except NoResultFound as e:
		res['returncode'] = 1
		res['error'] = 'deleteuser'
		res['message'] = "找不到相关记录"
	else:
		res['returncode'] = -1
		res['error'] = 'deleteuser'
		res['message'] = "用户删除失败，未知原因"

	
	return res

@get('/manage/user')
def adduser():
	return {
		'__template__': 'user.html'

	}

@get('/manage/user/edit')
def editUser(*, id):
	return {
		'__template__': 'user_edit.html',
		'id': id,
		'action': '/manage/api/user/update/%s' % id

	}

@get('/manage/user/add')
def addUser():
	return {
		'__template__': 'user_edit.html',
		'id': '',
		'action': '/api/users'

	}

@post('/api/addmathoralcal')
def addMathOralCal(*, uid, caldate, consumingtime, errorcount):
	if consumingtime is None or consumingtime < 0:
		raise APIValueError('consumingtime','口算计时不正确')
	if errorcount is None or errorcount < 0:
		raise APIValueError('errorcount','错题数量不正确')
	
	
	try:
		# 解析故障开始时间字符串到datetime对象
		ct = datetime.datetime.strptime(caldate, '%Y-%m-%d')
	except Exception as e:
		raise APIValueError('caldate','口算日期不正确' + e)
	#检查当天成绩是否已经提交
	filters = {MathOralCal.cal_date == caldate, MathOralCal.user == uid}
	cal = MathOralCal.getAll(*filters)
	res = dict()
	if len(cal) > 0:
		try:
			MathOralCal.updateCal(cal[0]['id'],consumingtime,errorcount)
			res['message'] = '%s 的成绩已经存在，本次修改成功' % (caldate)
		except Exception as e:
			raise APIValueError('callog','%s 的成绩修改失败' % (caldate) + e)
	else:
		mathOralCal = MathOralCal(uid, ct, consumingtime, errorcount,datetime.datetime.now(), datetime.datetime.now())
		#添加工单处理日志
		mathOralCal.save()
		res['message'] = '口算记录添加成功'
	
	res['returncode'] = const.RETURN_OK
	
	return res

@get('/api/math/getmathoralcal')
def getMathOralCal(*, uid, starttime, endtime, orderby):
	try:
		# 解析故障开始时间字符串到datetime对象
		st = datetime.datetime.strptime(starttime, '%Y-%m-%d')
		et = datetime.datetime.strptime(endtime, '%Y-%m-%d')
		et = et + datetime.timedelta(days=1)
	except Exception as e:
		raise APIValueError('datetime','开始或结束日期不正确')
	filters = {}
	
	user = User.getUserById(uid)
	
	#教师和管理员可以读取所有学生成绩
	if user['role'] == 'TEACHER' or user['is_admin'] == 1:	
		filters = {MathOralCal.cal_date >= st, MathOralCal.cal_date < et}

	else:
		#家长仅能读取单个学生升级
		filters = {MathOralCal.user == uid, MathOralCal.cal_date >= st, MathOralCal.cal_date < et}
	
	cals = MathOralCal.getAll(*filters, orderby=orderby)
	
	return  dict(cals=cals)

@get('/api/math/mathoralcals/{id}')
def api_reset_oral(id, request, *, starttime, endtime):
	try:
		# 解析故障开始时间字符串到datetime对象
		st = datetime.datetime.strptime(starttime, '%Y-%m-%d')
		et = datetime.datetime.strptime(endtime, '%Y-%m-%d')
		et = et + datetime.timedelta(days=1)
	except Exception as e:
		raise APIValueError('datetime','开始或结束日期不正确')
	
	filters = {MathOralCal.user == id, MathOralCal.cal_date >= st, MathOralCal.cal_date < et}
	cals = MathOralCal.getAll(*filters)
	return  dict(cals = cals)

@get('/api/math/getstatistic')
def getMathStatistic(*, uid, starttime, endtime, orderby):
	try:
		# 解析故障开始时间字符串到datetime对象
		st = datetime.datetime.strptime(starttime, '%Y-%m-%d')
		et = datetime.datetime.strptime(endtime, '%Y-%m-%d')
		et = et + datetime.timedelta(days=1)
	except Exception as e:
		raise APIValueError('datetime','开始或结束日期不正确')
	filters = {}
	user = User.getUserById(uid)
	#教师和管理员可以读取所有学生成绩
	if user['role'] == 'TEACHER' or user['is_admin'] == 1:	
		filters = {MathOralCal.cal_date >= st, MathOralCal.cal_date < et}

	else:
		#家长仅能读取单个学生升级
		filters = {MathOralCal.user == uid, MathOralCal.cal_date >= st, MathOralCal.cal_date < et}

	cals = MathOralCal.getStatistic(*filters, orderby=orderby)
	return dict(cals=cals)


# 帮助函数，根据用户id列表返回以指定符号分隔的用户名字符串
def getUserName(delimiter,users):
	userids = []
	result = []
	for userid in users:
		userids.append(int(userid))
	filters = {User.id.in_(userids)}
	allUser = User.getAll(*filters)
	for user in allUser:
		result.append(user['name'])
	logging.info('result: %s' % result)
	return delimiter.join(result)







