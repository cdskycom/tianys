# -*- coding: utf-8 -*-

class _const:
  class ConstError(TypeError): pass
  class ConstCaseError(ConstError): pass

  def __setattr__(self, name, value):
      if name in self.__dict__:
          raise self.ConstError("can't change const %s" % name)
      if not name.isupper():
          raise self.ConstCaseError('const name "%s" is not all uppercase' % name)
      self.__dict__[name] = value

const = _const()

# 工单状态常量
const.STATUS_ACCEPT = 'ACCEPT'
const.STATUS_DEALING = 'DEALING'
const.STATUS_FINISHED = 'FINISHED'
const.STATUS_ALL = 'ALL'

#任务状态常量
const.TASK_PENDING = 0
const.TASK_FINISHED = 1
const.TASK_ACCEPTED = 2  #已接收任务，但未完成处理

# 工单处理标识常量
const.DEALING_CREATE = 'CREATE'
const.DEALING_REPLY = 'REPLY'
const.DEALING_TRANSIT = 'TRANSIT'
const.DEALING_FINISHED = 'FINISHED'
const.DEALING_ACCEPT = 'ACCEPT'  #接单

# 返回消息常量
const.RETURN_OK = 0
