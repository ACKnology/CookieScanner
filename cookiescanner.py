#!/usr/bin/env python3

# Instalação:
# sudo yum install chromium-chromedriver
# sudo yum install firefox
# sudo -H python3 -m pip install selenium
# sudo -H python3 -m pip install flask

import re
from flask import Flask, request, jsonify
import sys
import json
import time
import base64
import pickle
import sqlite3
import os
#import xlsxwriter as xw
import glob
import logging
import subprocess
import tempfile
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

coringas = []

hdr = ['Cookie', 'Dominio', 'Expiracao', 'HttpOnly', 'Path', 'SameSite', 'Secure', 'Value', 'EU_IA',
		'Plataforma', 'Categoria', 'DscDominio', 'Retencao', 'Controlador', 'Politica', 'Descricao']


mainName = os.path.basename(sys.argv[0]).split('.')[0]
mainPath = os.getcwd()
print(f"{dt.now()} - Iniciando o {mainName}...")
logging.info(f"Iniciando o {mainName}...")

try:
	# Criando o diretório de logs
	if not os.path.exists('./log'):
		os.makedirs('./log')
		
	logging.basicConfig(format='%(asctime)s - %(message)s', level = logging.INFO, filename = f'{mainPath}/log/{mainName}.log')

except OSError:
	print(f"{dt.now()} - Erro ao criar o diretório de logs")
	exit(1)

def getCookieInfo(sqlQuery):
		
	con = sqlite3.connect('./db/cookies_db.db')

	try:
		cur = con.cursor()
		ds = [row for row in cur.execute(sqlQuery)]

	except Exception as e:
		logging.error(f"Erro ao conectar na base de cookies: {e}")
		pass

	finally:
		con.close()

	return ds

try:
	release = subprocess.check_output(["git", "tag"]).decode()
except:
	release = ""
	pass	

# Obtenção dos cookies coringas na base de cookies

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

ds = getCookieInfo(query)

for item in ds:

	coringas.append(item[0])

coringas.sort(key=len, reverse=True)

app = Flask(__name__)
# app.config["DEBUG"] = True

def getCookieName(cookieStr):
	for cookie in coringas:
		if cookie in cookieStr:
		 return(cookie)
	return cookieStr

@app.errorhandler(Exception)
def all_exception_handler(error):
	print(f">>> {dt.now()} - Erro:{error}")
	logging.critical(f"Erro:{error}")
	# errorCode = str(error).split(" ")[0]
	# errorMesg = str(" ".join(str(error).split(" ")[1:]))
	errorMesg = str(error)
	return jsonify({'status_code':555, 'message': errorMesg}), 555


@app.route('/', methods=['GET', 'POST'])
def home():
    return f'''<h1>Scanner de Cookies {release}</h1>
<hr>
<p>Módulo Security - CookieScanner - API Scanner de Cookies.</br>
Autor: Christiano Medeiros - christiano.medeiros (at) modulo.com</br></br>
Exemplo:</br><a href="http://127.0.0.1:5000/api/v1/cookies/scan?uri=https://www.modulo.com">http://127.0.0.1:5000/api/v1/cookies/scan?uri=https://www.modulo.com</a></p>'''


@app.route('/api/v1/cookies/scan', methods=['GET'])
def api_id():

	cookies = ()
	endScan = dict()
	endScan.clear()
	result = dict()
	result.clear()

	if 'uri' in request.args:
		uri = request.args['uri']

		# cookies_json = f"{uri.replace('/', '-').replace(':', '=')}.json"
		# json_path = "./json/"

		print(f">>> {dt.now()} - Iniciando o WebDriver...")
		logging.info(f"Iniciando o WebDriver...")
		driver = webdriver.Firefox(options=options)

		try:
			print(f">>> {dt.now()} - Acessando {uri}...")
			logging.info(f"Acessando {uri}...")
			driver.get(f"{uri}")

		except Exception as e:
			print(f">>> {dt.now()} - Erro:{str(e)}")
			logging.error(f"Erro:{str(e)}")
			raise Exception(str(e))

		time.sleep(15)

		try:
			tmp_name = next(tempfile._get_candidate_names())
			tmp_dir = tempfile._get_default_tempdir()
			tmp_file = f"{tmp_dir}/{tmp_name}.png"
			print(f">>> {dt.now()} - Salvando o screenshot {tmp_file}")
			logging.info(f"Salvando o screenshot {tmp_file}")
			driver.save_screenshot(tmp_file)
			with open(tmp_file, "rb") as img_file:
				txt_img = base64.b64encode(img_file.read()).decode('utf-8')

		except Exception as e:
			print(f">>> {dt.now()} - Erro ao salvar o screenshot de {uri}: {e}")
			logging.error(f"Erro ao salvar o screenshot de {uri}: {e}")

		try:
			print(f">>> {dt.now()} - Obtendo cookies...")
			logging.info(f"Obtendo cookies...")
			cookies = ()
			cookies = driver.get_cookies()

		except Exception as e:
			print(f">>> {dt.now()} - {str(e)}")
			logging.error(f"Erro:{str(e)}")

		finally:
			print(f">>> {dt.now()} - Fechando o WebDriver...")
			logging.info(f"Fechando o WebDriver...")
			driver.close()

		for ck in cookies:
			print("CK:", ck)
			analise = {}
			xds = []
			xcol = 0

			query = f""" 
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
								nome like \'{getCookieName(ck['name'])}%\'
						order by
								nome
						limit 1
					"""

			#executando a query na base all_cookies (base de cookies)
			ds = getCookieInfo(query)

			#criando lista contendo dados dos cookies coletados na web
			try:
				xds = [ck['name'], ck['domain'], dt.fromtimestamp(int(ck['expiry'])).strftime('%Y-%m-%d %H:%M:%S'), ck['httpOnly'], ck['path'], ck['sameSite'], ck['secure'], ck['value']]
			except:
				xds = [ck['name'], ck['domain'], '-1', ck['httpOnly'],ck['path'], ck['sameSite'], ck['secure'], ck['value']]

			#Incluindo na lista 'xds' campos de retorno via SQL da base de cookies
			for r in ds:
				for v in r:
					xds.append(v)
					# print(v)

			#Populando dicionário 'analise' com os dados contidos na lista 'xds'
			analise.clear()

			for c in hdr:
				try:
					analise[c] = xds[hdr.index(c)]
				except:
					analise[c] = ''

			# print("CK:",ck)

			# print("ANALISE:",analise)

			# print("RESULT:",result)

			if getCookieName(ck['name']) != None :
				result[getCookieName(ck['name'])] = analise
			else:
				result[ck['name']] = analise

		endScan.clear()

		endScan["report"] = { "quantity": len(result), "screenshot": txt_img }
		endScan["uri"] = uri
		endScan["cookies"] = result

		return jsonify(endScan)

	else:
		raise Exception("URI não informada.")



if __name__ == '__main__':
	print(f">>> {dt.now()} - Início do serviço")
	logging.info(f"Início do serviço")
	app.run(host='0.0.0.0', port=5000, debug=True)
	print(f">>> {dt.now()} - Aguardando conexão...")

