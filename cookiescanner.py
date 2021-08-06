#!/usr/bin/env python3

# Instalação:
# sudo yum install chromium-chromedriver
# sudo yum install firefox
# sudo -H python3 -m pip install selenium
# sudo -H python3 -m pip install flask

from flask import Flask, request, jsonify
import sys
import json
import time
import pickle
import sqlite3
import os
#import xlsxwriter as xw
import glob
from datetime import datetime as dt
from selenium import webdriver 

# Chrome ==========================================================
#from selenium.webdriver.chrome.options import Options
#chrome_options = Options()
#chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("--no-sandbox") # linux only
#chrome_options.headless = True # also works
#driver = webdriver.Chrome(options=chrome_options)
# =================================================================

from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True

app = Flask(__name__)
# app.config["DEBUG"] = True

hdr = ['Cookie', 'Dominio', 'Expiracao', 'HttpOnly', 'Path', 'SameSite', 'Secure', 'Value', 'EU_IA', 'Plataforma', 'Categoria', 'DscDominio', 'Retencao', 'Controlador', 'Politica' , 'Descricao']

coringas = []

try:
	con = sqlite3.connect('./db/cookies_db.db')
	cur = con.cursor()

	query = """ 
				select
						nome
				from
						all_cookies
				where
						coringa = 1
				order by
						nome
			"""
	ds = cur.execute(query)

	for item in ds:

		coringas.append(item[0])

	coringas.sort(key=len, reverse=True)

except Exception as e:
	print(">>> Catched: {0}".format(str(e)))
	print(">>> %s - Erro ao conectar a base de cookies para efetuar a carga dos cookies variantes..."%(dt.now()))

finally:
	con.close()

def getCookieName(cookieStr):

	for cookie in coringas:
		if cookie in cookieStr:
			 return(cookie)
	return cookieStr

@app.route('/', methods=['GET','POST'])
def home():
    return '''<h1>Scanner de Cookies</h1>
<p>Módulo Security - CookieScanner - API Scanner de Cookies.</br>
Autor: Christiano Medeiros - christiano.medeiros (at) modulo.com</p>'''

@app.route('/api/v1/cookies/scan', methods=['GET'])

def api_id():

	try:
		con = sqlite3.connect('./db/cookies_db.db')
		cur = con.cursor()
	except e:
		print(">>> %s - Erro ao conectar a base de cookies..."%(dt.now(),e))

	xrow=0
	xcol=0

	if 'uri' in request.args:
		uri = request.args['uri']

		cookies_json = "cookies_%s.json"%uri.replace('/','-')
		json_path = "./json/"

		print(">>> %s - Iniciando o WebDriver..."%dt.now())
		driver = webdriver.Firefox(options=options)

		try:
			print(">>> %s - Acessando %s..."%(dt.now(),uri))
			driver.get("%s"%uri)
		except Exception as e:
			print("### Erro: %s"%str(e))


		print(">>> %s - Gravando %s..."%(dt.now(),cookies_json))
		cookies = driver.get_cookies()
		with open(json_path+cookies_json, 'w+', newline='') as outputdata:
		    json.dump(cookies, outputdata,indent=4, sort_keys=True)

		driver.quit()

	else:
		return "Erro: Nenhuma uri informada. Por favor, especifique uma uri para efetuar o scan."

	result={}

	for ck in cookies:
		print("CK:",ck)
		analise = {}
		xds = []
		xcol = 0

		query = """ 
					select 	EU_IA,
						 	plataforma,
						 	categoria,
						 	dominio,
						 	retencao,
						 	controlador,
						 	politica,
						 	descricao 
					from
							all_cookies
					where
							nome like \'{}%\'
					order by
							nome
					limit 1

				""".format(getCookieName(ck['name']))

		#executando a quey na base all_cookies (base de cookies)
		ds = cur.execute(query)

		#criando lista contendo dados dos cookies coletados na web
		try:
			xds = [ck['name'],ck['domain'], dt.fromtimestamp(int(ck['expiry'])).strftime('%Y-%m-%d %H:%M:%S'), ck['httpOnly'], ck['path'], ck['sameSite'], ck['secure'], ck['value']]
		except:
			xds = [ck['name'],ck['domain'], '-1', ck['httpOnly'], ck['path'], ck['sameSite'], ck['secure'], ck['value']]

		#Incluindo na lista 'xds' campos de retorno via SQL da base de cookies
		for r in ds:
			for v in r:
				xds.append(v)

		#Populando dicionário 'analise' com os dados contidos na lista 'xds'
		for c in hdr:
			try:
				analise[c]=xds[hdr.index(c)]
			except:
				analise[c]=''

		# print("CK:",ck)

		# print("ANALISE:",analise)

		# print("RESULT:",result)

		result[getCookieName(ck['name'])]=analise

	con.close()

	print(">>> %s - Aguardando conexão..."%dt.now())

	endRes=dict()

	endRes[uri]=result

	return jsonify(endRes)

if __name__ == '__main__':
	print(">>> %s - Iniciando o servidor..."%dt.now())
	app.run(host='0.0.0.0',port=5000,debug=True) 
