# -*- coding: utf-8 -*-

from orm import User, SupportProvider, TroubleTicket, TroubleDealLog, TroubleTask, SupportProvider, session_scope
from const import const
import logging, time, datetime


def addTroubleTicket(report_channel, type, region, level, description, 
		impact, startTime, custid, mac, contact, contact_phone, 
		create_user, create_user_name, deal_user, deal_user_name):
	logging.info('创建工单，创建人: %s' % create_user_name)
	if not report_channel or not account.strip():
		raise APIValueError('report_channel','上报渠道不能为空')
	if not type or not type.strip():
		raise APIValueError('trouble_type','故障类型不能为空')
	if not region or not region.strip():
		raise APIValueError('region','故障地市不能为空')
	if not level or not level.strip():
		raise APIValueError('level','故障级别不能为空')
	if not description or not description.strip():
		raise APIValueError('description', '故障现象不能为空')
	if not contact or not contact.strip():
		raise APIValueError('contact','故障联系人不能为空')
	if not create_user: 
		raise APIValueError('create_user', '工单创建人不能为空')	
	if not deal_user: 
		raise APIValueError('deal_user', '当前故障处理人不能为空')
	
	try:
		# 解析故障开始时间字符串到datetime对象
		st = datetime.datetime.strptime(startTime, '%Y-%m-%dT%H:%M')
	except Exception as e:
		raise APIValueError('datetime','故障日期格式不正确')
	
	troubleTicket = TroubleTicket(report_channel, type, region, level, description, 
		impact, startTime, custid, mac, contact, contact_phone, 
		create_user, create_user_name, deal_user, deal_user_name)

	troubleTicket.save()
	res = dict()
	res['returncode'] = const.RETURN_OK
	res['message'] = '故障工单添加成功'
	return res

def getAllTroubleCount(status):
	filters = {}
	if status.upper() != const.STATUS_ALL:
		filters = {TroubleTicket.status == status}
	return TroubleTicket.getTroubleCount(*filters)

def getTaskCountByProvider(providerID):
	filters = {TroubleTask.support_provider == providerID, TroubleTask.status == 0}
	return TroubleTask.getTaskCount(*filters)

def getTask(providerID):
	filters = {TroubleTask.support_provider == providerID, TroubleTask.status == 0}
	return TroubleTask.getTask(*filters)

def getTaskPage(page, items_perpage, providerID):
	filters = {TroubleTask.support_provider == providerID, TroubleTask.status == 0}
	return TroubleTask.getTaskPage(page, items_perpage, *filters)

def getDealLogByTrouble(troubleId):
	return TroubleDealLog.getDealLogByTrouble(troubleId)

def getProvider():
	return SupportProvider.getAll()

def  dealingTask(dealingtype, taskid, nextprovider, reply, uid):
	res = dict()
	with session_scope() as session:
		#更新当前工单
		task = session.query(TroubleTask).filter(TroubleTask.id==taskid).one()
		task.status = const.TASK_FINISHED
		task.reply = reply
		task.endtime = datetime.datetime.now()

		if(dealingtype != const.DEALING_FINISHED):
			#生成下一个工单
			trouble_ticket = task.trouble.id
			support_provider = nextprovider
			remark = reply
			createtime = datetime.datetime.now()
			assign_user = uid
			newTask = TroubleTask(trouble_ticket=trouble_ticket, support_provider=support_provider,
				remark=remark, createtime=createtime, assign_user=assign_user, status=0)
			session.add(newTask)

		#添加工程单处理记录
		user = session.query(User).join(User.support_provider).filter(User.id==uid).one()
		deal_user_name = user.name
		support_provider_name = user.support_provider.provider_name
		trouble_ticket_id = task.trouble.id
		deal_user = uid
		remark = reply
		log_type = dealingtype
		dealingLog = TroubleDealLog(trouble_ticket_id=trouble_ticket_id, deal_user=deal_user,remark=remark,
			log_type=log_type, deal_user_name=deal_user_name, support_provider_name=support_provider_name)
		session.add(dealingLog)

		#更新工单状态
		troubleTicketStatus = ''
		if(dealingtype == const.DEALING_FINISHED):
			troubleTicketStatus = const.STATUS_FINISHED
		else:
			troubleTicketStatus = const.STATUS_DEALING
		trouble = session.query(TroubleTicket).filter(TroubleTicket.id==task.trouble.id).one()
		trouble.status = troubleTicketStatus
		trouble.deal_user = uid
		trouble.deal_user_name = user.name
		session.commit()
		
	res['returncode'] = const.RETURN_OK
	res['message'] = '任务工单处理成功' + dealingtype
	return res

