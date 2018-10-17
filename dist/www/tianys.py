# -*- coding: utf-8 -*-
import logging

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web
from jinja2 import Environment, FileSystemLoader
from coroweb import add_static, add_routes
from config import configs
# import orm
from orm import  get_dbengine
from handlers import cookie2user, COOKIE_NAME
import pdb

logging.basicConfig(level=logging.WARNING,filename='./log/tianyslog.txt')
# logging.basicConfig(level=logging.INFO)


def init_jinja2(app, **kw):
	logging.info('init jinja2...')
	options = dict(
		autoescape = kw.get('autoescap', True),
		block_start_string = kw.get('block_start_string', '{%'),
		block_end_string = kw.get('block_end_string', '%}'),
		variable_start_string = kw.get('variable_start_string', '{{{'),
		variable_end_string = kw.get('variable_end_string', '}}}'),
		auto_reload = kw.get('auto_reload', True))
	path = kw.get('path', None)
	if path is None:
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
	logging.info('set jinja2 template path: %s' % path)
	env = Environment(loader=FileSystemLoader(path), **options)
	filters = kw.get('filters', None)
	if filters is not None:
		for name, f in filters.items():
			env.filters[name] = f
	app['__templating__'] = env

async def logger_factory(app, handler):
	async def logger(request):
		logging.info('Request:%s %s' % (request.method, request.path))
		return (await handler(request))
	return logger

async def auth_factory(app, handler):
    
    async def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)

        if cookie_str:
            user = cookie2user(cookie_str)
            if user:
                logging.info('set current user: %s' % user['account'])
                request.__user__ = user
        if not (request.path.startswith('/signin') or request.path.startswith('/static')) and request.__user__ is None:
            return web.HTTPFound('/signin')
        if (request.path.startswith('/manage') and not request.__user__['is_admin']):
        	return web.HTTPFound('/signin')
      
        return ( await handler(request))
    return auth

async def response_factory(app, handler):
	
	async def response(request):
		logging.info('Response handler...')
		r = await handler(request)
		if isinstance(r, web.StreamResponse):
			return r
		if isinstance(r, bytes):
			resp = web.Response(body=r)
			resp.content_type = 'application/octet-stream'
			return resp
		if isinstance(r, str):
			if r.startswith('redirect:'):
				return web.HTTPFound(r[9:])
			resp = web.Response(body=r.encode('utf-8'))
			resp.content_type = 'text/html;charset=utf-8'
			return resp
		if isinstance(r, dict):
			template = r.get('__template__')
			if template is None:
				logging.info('r : %s' % r)
				resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
				# resp = web.Response(body=json.dumps(r, ensure_ascii=False, cls=orm.AlchemyEncoder).encode('utf-8'))
				resp.content_type = 'application/json;charset=utf-8'
				return resp
			else:
				r['__user__'] = request.__user__
				logging.info("返回数据中加的user: %s" % r['__user__'])
				resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
				resp.content_type = 'text/html;charset=utf-8'
				return resp
		if isinstance(r, int) and t >= 100 and t < 600:
			return web.Response(t)
		if isinstance(r, tuple) and len(r) == 2:
			t, m = r
			if isinstance(t, int) and t >= 100 and t < 600:
				return web.Response(t, str(m))
		# default:
		resp = web.Response(body=str(r).encode('utf-8'))
		resp.content_type = 'text/plain;charset=utf-8'
		return resp
	return response

async def init(loop):
	#初始化数据aiomysql数据，得到全局变量__engine

	# orm.get_dbengine(**configs.db)
	get_dbengine(**configs.db)
	app = web.Application(loop=loop, middlewares=[logger_factory, response_factory, auth_factory])
	init_jinja2(app)
	# 此处需插入路径绑定
	add_routes(app, 'handlers')
	add_static(app)
	srv = await loop.create_server(app.make_handler(), '0.0.0.0', 8089)
	logging.info('server started at http://0.0.0.0:8089')
	return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()


