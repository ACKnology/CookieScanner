#!/usr/bin/env python3

import sqlite3
import json
import os
import sys
import datetime
import xlsxwriter as xw
import glob

from datetime import datetime as dt

filel=glob.glob("./json/*.json")

xfile = sys.argv[1]

wb = xw.Workbook("./xlsx/{}.xlsx".format(xfile))

for jfile in filel:

	print(">> %s - Lendo o arquivo %s"%(dt.now(),jfile))

	f = open("%s"%jfile,)
	js = json.load(f)

	print(">> %s - Criando a planilha %s"%(dt.now(),jfile.split("_")[1][:-5]))
	ws = wb.add_worksheet(jfile.split("_")[1][:-5])

	con = sqlite3.connect('./db/cookies_db.db')
	cur = con.cursor()

	hdr = (['Cookie', 'Dominio', 'Expiracao', 'HttpOnly', 'Path', 'SameSite', 'Secure', 'Value', 'EU_AI', 'Plataforma', 'Categoria', 'DscDominio', 'Retencao', 'Controlador', 'Politica' , 'Descricao'])

	xrow=0
	xcol=0

	for c in hdr:
	   ws.write(xrow,xcol,c)
	   xcol=xcol+1

	xrow=1

	for ck in js:
		xcol = 0
		query = "select EU_IA, plataforma, categoria, dominio, retencao, controlador, politica, descricao from all_cookies where nome like \'{}%\' order by nome limit 1".format(ck['name'])
		#print(query)
		#pass
		ds = cur.execute(query)
		try:
			#xds = ([ck['domain'], ck['expiry'], ck['httpOnly'], ck['path'], ck['sameSite'], ck['secure'], ck['value']])
			xds = ([ck['name'],ck['domain'], datetime.datetime.fromtimestamp(int(ck['expiry'])).strftime('%Y-%m-%d %H:%M:%S'), ck['httpOnly'], ck['path'], ck['sameSite'], ck['secure'], ck['value']])
		except:
			xds = ([ck['name'],ck['domain'], '-1', ck['httpOnly'], ck['path'], ck['sameSite'], ck['secure'], ck['value']])

		for r in ds:
			xds.append(r[0])
			xds.append(r[1])
			xds.append(r[2])
			xds.append(r[3])
			xds.append(r[4])
			xds.append(r[5])
			xds.append(r[6])
			xds.append(r[7])
		for c in xds:
			#print("xrow:%d, xcol:%d, xds:%s"%(xrow,xcol,xds))
			ws.write(xrow,xcol,xds[xcol])
			xcol = xcol + 1
		xrow = xrow + 1

print(">> %s - Gravando o arquivo ./xlsx/%s.xlsx"%(dt.now(),xfile))
wb.close()
#con.close()


#cell_format.set_font_color('#FF0000')
#cell_format = workbook.add_format({'bold': True, 'font_color': 'red'})








