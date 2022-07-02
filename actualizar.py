from lxml import etree
import requests
import json

# - CONFIGURACION - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

formaFondo = 'izq' #izq, der, cenI, cenD

idAutosSVG = ['ferrari','ferrariT','red','redT','mercedes','mercedesT'
			 ,'haas','haasT','alpine','alpineT','alfa','alfaT','alpha'
			 ,'alphaT','mclaren','mclarenT','aston','astonT','williams'
			 ,'williamsT']

triNombreCorrespondiente = ['LEC','SAI','VER','PER','RUS','HAM'
						   ,'MAG','MSC','ALO','OCO','BOT','ZHO'
						   ,'GAS','TSU','RIC','NOR','STR','VET'
						   ,'ALB','LAT']

reemplazados = ['VET']
reemplazos = ['HUL']

# - GLOBALES  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

xml = etree.parse('original.svg')
svg = xml.getroot()
anchoTotal = 677.33331
altoTotal = 285.75
offsetBizarroY = 24.95989 - 21.502689999999916
offsetBizarroRedBull = 21.503 - 23.439
origenX = 0
origenY = 0
yGanador = 21.502689999999944
yUltimo = 207.41797999999994
ySombraSi = "-68.20254"
xIzquierda = 21.502689999999916
intervaloX = 53.75671999999997 - xIzquierda

# - FUNCIONES/CLASES  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def traducirTiempo(piloto, milisP, ultimaD, antPiloto):
	if piloto['status'] == 'Finished':
		if antPiloto != None and int(piloto['Time']['millis']) - milisP < antPiloto.punta:
			return antPiloto.punta + int(float(piloto['Time']['time']) * 1000)
		return int(piloto['Time']['millis']) - milisP
	if piloto['status'][0] == '+':
		return antPiloto.punta + ultimaD
	else:
		return -67

def posicionCampeonato(triNombre):
	return 0

def abandono(nombre, resultado):
	triNombre = triNombreCorrespondiente[idAutosSVG.index(nombre)]
	for p in resultado:
		if p.triNombre == triNombre and p.punta < 0:
			return True
	return False

def obtenerOrdenX(posicionCarrera, forma, triNombre):
	if "_campeonato" in forma:
		posicionCarrera = posicionCampeonato(triNombre)
		forma = forma[:-11]
	if forma == "cenD":
		corr = [10,9,11,8,12,7,13,6,14,5,15,4,16,3,17,2,18,1,19,0]
		posicionCarrera = corr[posicionCarrera]
		forma = "izq"
	if forma == "cenI":
		corr = [9,10,8,11,7,12,6,13,5,14,4,15,3,16,2,17,1,18,0,19]
		posicionCarrera = corr[posicionCarrera]
		forma = "izq"
	if forma == "izq":
		return xIzquierda + posicionCarrera * intervaloX
	if forma == "der":
		return xIzquierda + (19-posicionCarrera) * intervaloX

class Elemento:
	def __init__(self, id, comaNegativo):
		self.x = float(comaNegativo.partition(",")[0]) - origenX
		self.y = float(comaNegativo.partition(",")[2]) - origenY
		self.id = id
	def __str__(self):
		return self.id + " - X: " + str(self.x) + ", Y: " + str(self.y)
elementoVacio = Elemento("","0,0")

class Auto:
	def __init__(self, nombre, elementos):
	    self.nombre = nombre
	    self.soyRedBull = self.nombre[:3] == 'red'
	    self.elementos = elementos
	    minX = anchoTotal * 10
	    minY = altoTotal * 10
	    for e in self.elementos:
	    	if e.x < minX:
	    		minX = e.x
	    	if e.y < minY:
	    		minY = e.y
	    self.x = minX
	    self.y = minY

	def __str__(self):
		return self.nombre + " - X: " + str(self.x) + ", Y: " + str(self.y)

	def setX(self,x):
		diferencia = x - self.x
		for e in self.elementos:
			e.x = e.x + diferencia
		self.x = x

	def setY(self,y):
		diferencia = y - self.y
		for e in self.elementos:
			e.y = e.y + diferencia
		self.y = y

	def contieneElemento(self,id):
		for e in self.elementos:
			if e.id == id:
				return True
		return False

	def getYElemento(self,id):
		offset = 0
		if self.soyRedBull:
			offset = offsetBizarroRedBull
		for e in self.elementos:
			if e.id == id:
				return e.y + origenY + offset

	def getXElemento(self,id):
		for e in self.elementos:
			if e.id == id:
				return e.x + origenX

class Parrilla:
	def __init__(self, autos):
	    self.autos = autos

	def buscarAuto(self, nombre):
		for a in self.autos:
			if a.nombre == nombre:
				return a
		return

	def ordenarY(self, resultado):
		maxDistancia = 0
		for p in resultado:
			if p.punta > maxDistancia:
				maxDistancia = p.punta

		for p in resultado:
			for a in self.autos:
				if a.nombre == idAutosSVG[triNombreCorrespondiente.index(p.triNombre)]:
					if p.punta < 0:
						a.setY(yUltimo)
					else:
						a.setY(yGanador + (p.punta/maxDistancia) * (yUltimo-yGanador))
	
	def ordenarX(self, forma, resultado):
		posicionesSombra = []
		i = 0
		for p in resultado:
			for a in self.autos:
				if a.nombre == idAutosSVG[triNombreCorrespondiente.index(p.triNombre)]:
					a.setX(obtenerOrdenX(i,forma,p.triNombre))
					if abandono(a.nombre,resultado):
						posicionesSombra.append(str(int((obtenerOrdenX(i,forma,p.triNombre) - xIzquierda)/intervaloX)))
			i+=1
		return posicionesSombra


class PilotoResultado:
	def __init__(self, triNombre, punta):
		self.triNombre = triNombre
		self.punta = punta

# - EJECUCION - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

for child in svg:
	autos = []
	for child2 in child:
		if child2.get('id') == 'rect30279':
			origenX = float(child2.get('x'))
			origenY = float(child2.get('y')) + offsetBizarroY
		if child2.get('id') in idAutosSVG:
			elementos = []
			for child3 in child2:
				e = elementoVacio
				if child3.get('x'):
					e = Elemento(child3.get('id'),child3.get('x') + ',' + child3.get('y'))
				if child3.get('d'):
					e = Elemento(child3.get('id'),child3.get('d').partition(" ")[2].partition(" ")[0])
				if e.id != "":
					elementos.append(e)
			autos.append(Auto(child2.get('id'),elementos))

parrilla = Parrilla(autos)
resultado = []

diccionario = json.loads(requests.get('http://ergast.com/api/f1/current/last/results.json').text)
pilotos = diccionario['MRData']['RaceTable']['Races'][0]['Results']

milisPrimero = 0
ultimaDiferencia = 1
anteriorPiloto = None

i = 0
for p in pilotos:
	if p['Driver']['code'] not in triNombreCorrespondiente:
		triNombreCorrespondiente[triNombreCorrespondiente.index(reemplazados[reemplazos.index(p['Driver']['code'])])] = reemplazos[reemplazos.index(p['Driver']['code'])]
	if i == 0:
		milisPrimero = int(p['Time']['millis'])
	resultado.append(PilotoResultado(p['Driver']['code'],traducirTiempo(p, milisPrimero, ultimaDiferencia, anteriorPiloto)))
	if i > 0:
		ultimaDiferencia = resultado[-1].punta - resultado[-2].punta
		print(ultimaDiferencia)
	anteriorPiloto = resultado[-1]
	i+=1

parrilla.ordenarY(resultado)
posicionesSombra = parrilla.ordenarX(formaFondo, resultado)

for child in svg:
	for child2 in child:
		if child2.get('id') in idAutosSVG:
			auto = parrilla.buscarAuto(child2.get('id'))
			for child3 in child2:
				if child3.get('x') and auto.contieneElemento(child3.get('id')):
					child3.set('x',str(auto.getXElemento(child3.get('id'))))
					child3.set('y',str(auto.getYElemento(child3.get('id'))))
				if child3.get('d') and auto.contieneElemento(child3.get('id')):
					texto = child3.get('d')
					nuevasCoordenadas = str(auto.getXElemento(child3.get('id'))) + "," + str(auto.getYElemento(child3.get('id')))
					nuevoTexto = 'm ' + nuevasCoordenadas + texto[texto.index(' ',2):]
					child3.set('d',nuevoTexto)	
		if 'sombra' in child2.get('id') and child2.get('id').replace("sombra","") in posicionesSombra:
			texto = child2.get('d')
			nuevoTexto = texto[0:texto.index(",")] + "," + ySombraSi + texto[texto.index(' ',2):]
			child2.set('d',nuevoTexto)

with open('modificado.svg', 'wb') as f:
    xml.write(f)
