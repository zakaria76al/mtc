from flask import Flask, request, render_template, send_file
from sys import maxsize
from itertools import permutations
import copy
import random
import time
import rstr
import pandas as pd
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

#Class city
class city:
	def __init__(self,i,t):
		self.i=i #id de la ville
		self.t=t #tableau de distance entre les villes
	def distance(self,c):
		le=len(self.t)
		for v in range(0,le):
			if c.i==v:
				return self.t[v]

#Dynamic function
def TCP(T, Villes_Depart_Arrivee, index_j=-1):
    if len(T) == 2:  
      return T[0][1]
    else:
        ltDist = list()
        n = len(T)
        if n == Nb_Villes:
          for j in range(0,n):
            if j != Villes_Depart_Arrivee:
              
              ltCopy = copy.deepcopy(T)
              #----------Suppression de la ville J----------
              del(ltCopy[j])
              n1 = len(ltCopy)
              for t in range(0,n1):
                  del(ltCopy[t][j])
              #--------------------------------------------- 
                                       
              for k in range(0,n1):
                if k != Villes_Depart_Arrivee:                               
                  
                  if j <= k: 
                    a = TCP(ltCopy,Villes_Depart_Arrivee,k)  
                    ltDist.append(a + T[k+1][j] + T[j][Villes_Depart_Arrivee])
                    
                  else:
                    a = TCP(ltCopy,Villes_Depart_Arrivee,k)
                    ltDist.append(a + T[k][j] + T[j][Villes_Depart_Arrivee])
        else:
          for j in range(0,n):
            if j != Villes_Depart_Arrivee and j != index_j:

              ltCopy = copy.deepcopy(T)  
              #----------Suppression de la ville J----------
              del(ltCopy[index_j])
              n1 = len(ltCopy)
              for t in range(0,n1):
                  del(ltCopy[t][index_j])
              #---------------------------------------------
              
              if index_j < j:
                a = TCP(ltCopy,Villes_Depart_Arrivee,j-1) 
              else:  
                a = TCP(ltCopy,Villes_Depart_Arrivee,j)
                   
              ltDist.append(a + T[j][index_j])
    return min(ltDist)


def calcule_tot_distance(r): # r:liste id de ville(solution)
	d=0
	le=len(r)
	for j in range(0,le-1):
		d+=r[j].distance(r[j+1])
	return d+r[len(r)-1].distance(r[0])
#---------------------------Structure de voisinage 1----------------------------
def swap(i,j,l):
	tmp=l[i]
	l[i]=l[j]
	l[j]=tmp
	return l

def findTSPSwapSolution(s, timeAvailable):
	improvement = True
	start = time.time()
	end = start + timeAvailable
	while improvement:
		improvement = False
		best_distance = calcule_tot_distance(s)
		i=0
		a=len(s)
		while i<a:
            # for k in range(i+1,a):
			new_route = copy.deepcopy(swap(random.randint(1,a-1),random.randint(1,a-1),copy.deepcopy(s)))
			new_distance = calcule_tot_distance(new_route)
			print(new_distance)
			if new_distance < best_distance:
				s = copy.deepcopy(new_route)
				best_distance = new_distance
				improvement = True
				i=0
			else:
				i += 1  
				if time.time() > end:
					return s
	print(best_distance)
	s.insert(0, best_distance)
	return s
#--------------------------structure de voisinage 2opt--------------------------
def twoOptSwap(route, i, k):
	new_route = []
    # 1. take route[0] to route[i-1] and add them in order to new_route
	for index in range(0, i):
		new_route.append(route[index])
    # 2. take route[i] to route[k] and add them in reverse order to new_route
	for index in range(k, i-1, -1):
		new_route.append(route[index])
    # 3. take route[k+1] to end and add them in order to new_route
	for index in range(k+1, len(route)):
		new_route.append(route[index])
	return new_route

def findTSP2OptSolution(s, timeAvailable):
	improvement = True
	start = time.time()
	end = start + timeAvailable
	while improvement:
		improvement = False
		best_distance = calcule_tot_distance(s)
		i = 1
		while i < len(s):
			for k in range(i+1, len(s)):
				new_route = twoOptSwap(s, i, k)
				new_distance = calcule_tot_distance(new_route)
				if new_distance < best_distance:
					s = copy.deepcopy(new_route)
					best_distance = new_distance
					improvement = True
					i = 1
				if time.time() > end:
					return s
			else:
				i += 1
	print(best_distance)
	s.insert(0,best_distance)
	return s

def generalVNS(s, timeAvailable):
	a = copy.deepcopy(s)
	TSP2OPT = findTSP2OptSolution(s, timeAvailable)
	TSPSwap = findTSPSwapSolution(a, timeAvailable)
	if(TSP2OPT[0] < TSPSwap[0]):
		return TSP2OPT
	else:
		return TSPSwap


def createFile(data, best_distance):
	name = rstr.xeger(r'[A-Z]\d[A-Z]\d[A-Z]\d') + ".txt"
	f = open("/app/mtc/" + name, "x")
	txt = "La distance optimal trouvé est : " + str(best_distance) + " km\nLes villes à visiter par ordre sont comme suit : \n"
	for i in data:
		txt += "\t" + str(i) + "\n"
	f.write(txt)
	f.close()
	return "files/" + name


UPLOAD_FOLDER = "/app/mtc/"


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/files/<path:filename>', methods=['get','post'])
def downloadfilename(filename):
	return send_file("/app/mtc/" + filename, as_attachment=True)

@app.route('/dynamic', methods=['get','post'])
def dynamic():
	if request.method == 'POST':
		a = request.form['listeCities']
		b = a.split(',')
		listeCities = list()
		for i in b:
			listeCities.append(int(i))
		AllcitiesNames = ["Agadir","Al Hoceima","Beni Mellal","Casablanca","Dakhla","El Jadida","Errachidia","Essaouira","Fes","Figuig","Kenitra","Khenifra","Khouribga","Laayoune","Lagouira","Marrakech","Meknes","Nador","Ouarzazat","Ouajda","Rabat","Safi","Settat","Tanger","TanTan","Taza","Tetouan"]
		startCityN = AllcitiesNames[int(request.form['startCity'])]
		citiesNames = list()
		for i in listeCities:
			citiesNames.append(AllcitiesNames[i])
		startCity = citiesNames.index(startCityN)
		graph = [[0,1091,467,511,1173,417,681,173,756,1076,596,642,507,649,1645,273,740,1095,375,1099,602,294,439,880,331,876,892],[1091,0,564,536,2264,632,616,887,275,669,435,400,614,1740,2736,758,335,175,922,293,445,792,608,323,1422,173,278],[467,564,0,210,1640,271,375,370,289,770,122,300,90,1116,2112,194,278,628,398,632,260,351,157,538,798,409,536],[511,536,210,0,1684,99,545,351,289,920,131,299,120,1160,2156,238,229,628,442,632,91,256,72,369,842,2049,2065],[1173,2264,1640,1684,0,1590,1854,1346,1920,2249,1769,1815,1680,524,472,1446,1913,2260,1548,2272,1775,1467,1612,2053,841,2049,2065],[417,632,271,99,1590,0,506,252,388,1001,360,230,181,1066,2062,197,328,727,399,731,190,157,117,468,748,508,484],[681,616,375,545,1854,506,0,745,364,395,292,480,425,1330,2326,510,346,510,306,514,482,683,512,608,1012,760,604],[173,887,370,351,1346,252,745,0,640,1081,499,482,410,822,1818,176,580,9979,380,963,442,129,296,720,504,120,736],[756,275,289,289,1920,388,364,640,0,719,160,166,333,1396,2392,483,60,339,687,343,198,545,361,303,1087,599,281],[1076,669,770,920,2249,1001,395,1081,719,0,687,875,820,1725,2721,905,741,515,701,326,877,1078,907,988,1407,286,931],[596,435,122,131,1769,360,292,499,160,687,0,254,169,1245,2241,234,153,323,527,503,40,480,238,620,927,453,411],[642,400,300,299,1815,230,480,482,166,875,254,0,245,1291,2287,369,130,497,573,507,289,387,203,238,973,280,254],[507,614,90,120,1680,181,425,410,333,820,169,245,0,1156,2152,234,322,672,838,676,205,328,69,483,838,1525,499],[649,1740,1116,1160,524,1066,1330,822,1396,1725,1245,1291,1156,0,996,922,1389,1736,1024,1748,1251,943,1088,1529,318,2521,1541],[1645,2736,2112,2156,472,2062,2326,1818,2392,2721,2241,2287,2152,996,0,1918,2389,2732,2020,2744,2247,1989,2084,2525,1314,603,2537],[273,758,194,238,1446,197,510,176,483,905,234,369,234,922,1918,0,467,822,204,826,321,157,166,598,504,180,675],[740,335,278,229,1913,328,346,580,60,741,153,130,322,1389,2389,467,0,399,652,403,138,486,292,267,1071,219,258],[1095,175,628,628,2260,727,510,9979,339,515,323,497,672,1736,2732,822,399,0,816,104,535,884,969,1086,1426,790,437],[375,922,398,442,1548,399,306,380,687,701,527,573,838,1024,2020,204,652,816,0,820,528,361,370,811,705,223,280],[1099,293,632,632,2272,731,514,963,343,326,503,507,676,1748,2744,826,403,104,820,0,541,888,698,609,1430,318,555],[602,445,260,91,1775,190,482,442,198,877,40,289,205,1251,2247,321,138,535,528,541,0,347,157,278,933,664,294],[294,792,351,256,1467,157,683,129,545,1078,480,387,328,943,1989,157,486,884,361,888,347,0,201,625,625,474,641],[439,608,157,72,1612,117,512,296,361,907,238,203,69,1088,2084,166,292,969,370,698,157,201,0,433,770,423,450],[880,323,538,369,2053,468,608,720,303,988,620,238,483,1529,2525,598,267,1086,811,609,278,625,433,0,1211,1217,57],[331,1422,798,842,841,748,1012,504,1087,1407,927,973,838,318,1314,504,1071,1426,705,1430,933,625,770,1211,0,1420,1223],[876,173,409,2049,2049,508,760,120,599,286,453,280,1525,2521,603,180,219,790,223,318,664,474,423,1217,1420,0,370],[892,278,536,2065,2065,484,604,736,281,931,411,254,499,1541,2537,675,258,437,280,555,294,641,450,57,1223,370,0]]
		#Dcouper les données
		ltDistGlobale = list()
		for i in listeCities:
			ltDistSpec = list()
			for j in listeCities:
				ltDistSpec.append(graph[i][j])
			ltDistGlobale.append(ltDistSpec)
		print(ltDistGlobale)
		#Chercher le chemin
		V=len(listeCities)
		vertex = [] 
		for i in range(V):
			if i != startCity:
				vertex.append(i)
		min_path = maxsize
		next_permutation=permutations(vertex)
		for i in next_permutation:
			current_pathweight = 0
			k = startCity
			for j in i:
				current_pathweight += ltDistGlobale[k][j]
				k = j
			current_pathweight += ltDistGlobale[k][startCity]
			min_path = min(min_path, current_pathweight)
			if min_path == current_pathweight:
				chemin = i
		print(min_path)
		txt = list()
		txt.append(str(citiesNames[startCity]))
		for i in chemin:
			txt.append(str(citiesNames[i]))
		txt.append(str(citiesNames[startCity]))
		nameFile = createFile(txt,min_path)
		return render_template('results.html',chemin=txt,distance=min_path, fileLink=nameFile)
	else:
		return render_template('calculatorDynamic.html')

@app.route('/vns', methods=['get','post'])
def vns():
	if request.method == 'POST':
		#-------All Data-------
		graph = [[0,1091,467,511,1173,417,681,173,756,1076,596,642,507,649,1645,273,740,1095,375,1099,602,294,439,880,331,876,892],[1091,0,564,536,2264,632,616,887,275,669,435,400,614,1740,2736,758,335,175,922,293,445,792,608,323,1422,173,278],[467,564,0,210,1640,271,375,370,289,770,122,300,90,1116,2112,194,278,628,398,632,260,351,157,538,798,409,536],[511,536,210,0,1684,99,545,351,289,920,131,299,120,1160,2156,238,229,628,442,632,91,256,72,369,842,2049,2065],[1173,2264,1640,1684,0,1590,1854,1346,1920,2249,1769,1815,1680,524,472,1446,1913,2260,1548,2272,1775,1467,1612,2053,841,2049,2065],[417,632,271,99,1590,0,506,252,388,1001,360,230,181,1066,2062,197,328,727,399,731,190,157,117,468,748,508,484],[681,616,375,545,1854,506,0,745,364,395,292,480,425,1330,2326,510,346,510,306,514,482,683,512,608,1012,760,604],[173,887,370,351,1346,252,745,0,640,1081,499,482,410,822,1818,176,580,9979,380,963,442,129,296,720,504,120,736],[756,275,289,289,1920,388,364,640,0,719,160,166,333,1396,2392,483,60,339,687,343,198,545,361,303,1087,599,281],[1076,669,770,920,2249,1001,395,1081,719,0,687,875,820,1725,2721,905,741,515,701,326,877,1078,907,988,1407,286,931],[596,435,122,131,1769,360,292,499,160,687,0,254,169,1245,2241,234,153,323,527,503,40,480,238,620,927,453,411],[642,400,300,299,1815,230,480,482,166,875,254,0,245,1291,2287,369,130,497,573,507,289,387,203,238,973,280,254],[507,614,90,120,1680,181,425,410,333,820,169,245,0,1156,2152,234,322,672,838,676,205,328,69,483,838,1525,499],[649,1740,1116,1160,524,1066,1330,822,1396,1725,1245,1291,1156,0,996,922,1389,1736,1024,1748,1251,943,1088,1529,318,2521,1541],[1645,2736,2112,2156,472,2062,2326,1818,2392,2721,2241,2287,2152,996,0,1918,2389,2732,2020,2744,2247,1989,2084,2525,1314,603,2537],[273,758,194,238,1446,197,510,176,483,905,234,369,234,922,1918,0,467,822,204,826,321,157,166,598,504,180,675],[740,335,278,229,1913,328,346,580,60,741,153,130,322,1389,2389,467,0,399,652,403,138,486,292,267,1071,219,258],[1095,175,628,628,2260,727,510,9979,339,515,323,497,672,1736,2732,822,399,0,816,104,535,884,969,1086,1426,790,437],[375,922,398,442,1548,399,306,380,687,701,527,573,838,1024,2020,204,652,816,0,820,528,361,370,811,705,223,280],[1099,293,632,632,2272,731,514,963,343,326,503,507,676,1748,2744,826,403,104,820,0,541,888,698,609,1430,318,555],[602,445,260,91,1775,190,482,442,198,877,40,289,205,1251,2247,321,138,535,528,541,0,347,157,278,933,664,294],[294,792,351,256,1467,157,683,129,545,1078,480,387,328,943,1989,157,486,884,361,888,347,0,201,625,625,474,641],[439,608,157,72,1612,117,512,296,361,907,238,203,69,1088,2084,166,292,969,370,698,157,201,0,433,770,423,450],[880,323,538,369,2053,468,608,720,303,988,620,238,483,1529,2525,598,267,1086,811,609,278,625,433,0,1211,1217,57],[331,1422,798,842,841,748,1012,504,1087,1407,927,973,838,318,1314,504,1071,1426,705,1430,933,625,770,1211,0,1420,1223],[876,173,409,2049,2049,508,760,120,599,286,453,280,1525,2521,603,180,219,790,223,318,664,474,423,1217,1420,0,370],[892,278,536,2065,2065,484,604,736,281,931,411,254,499,1541,2537,675,258,437,280,555,294,641,450,57,1223,370,0]]
		AllcitiesNames = ["Agadir","Al Hoceima","Beni Mellal","Casablanca","Dakhla","El Jadida","Errachidia","Essaouira","Fes","Figuig","Kenitra","Khenifra","Khouribga","Laayoune","Lagouira","Marrakech","Meknes","Nador","Ouarzazat","Ouajda","Rabat","Safi","Settat","Tanger","TanTan","Taza","Tetouan"]
		#------Cities in request------
		a = request.form['listeCities']
		b = a.split(',')
		listeCities = list()
		for i in b:
			listeCities.append(int(i))
		#--------Start city--------
		startCity = int(request.form['startCity'])
		listeCities.remove(startCity)
		listeCities.insert(0,startCity)
		#-------Cities name--------
		listeCitiesName = list()
		for i in listeCities:
			listeCitiesName.append(AllcitiesNames[i])
		#--------Cut data---------
		ltDistGlobale = list()
		for i in listeCities:
			ltDistSpec = list()
			for j in listeCities:
				ltDistSpec.append(graph[i][j])
			ltDistGlobale.append(ltDistSpec)
		#--------Create new data city--------
		Lcity = list()
		for i in range(0,len(ltDistGlobale)):
			Lcity.append(city(i,ltDistGlobale[i]))
		#--------VNS-------
		t = generalVNS(Lcity,60)
		best_distance = t[0]
		t.pop(0)
		txt = list()
		for i in range(0, len(t)):
			txt.append(str(listeCitiesName[t[i].i]))
		txt.append(str(listeCitiesName[0]))
		print(txt)
		nameFile = createFile(txt,best_distance)
		return render_template('results.html',chemin=txt,distance=best_distance, fileLink=nameFile)
	else:
		return render_template('calculatorVns.html')

@app.route('/upload', methods=['get','post'])
def upload():
	if request.method == 'POST':
		#code ....
		dataFile = request.files['dataFile']
		if(dataFile.filename == ''):
			return render_template('upload.html?file=noFile')
		dataFile.save(os.path.join(app.config['UPLOAD_FOLDER'], dataFile.filename.split('.')[0] + ".xlsx"))
		#labled data
		islabled = True
		if 'islabled' not in request.form:
			islabled = False
		#Import Data
		citiesNames = list()
		X = pd.read_excel("/app/mtc/" + dataFile.filename.split('.')[0] + ".xlsx", engine='openpyxl', header = 0)
		
		if islabled == False:
			X = pd.read_excel("/app/mtc/" + dataFile.filename.split('.')[0] + ".xlsx", engine='openpyxl', header = None)
			citiesNames = request.form['labels'].split(",")
		else:
			citiesNames = copy.deepcopy(X.columns)

		X.columns = [i for i in range(1,len(X)+1)]
		algorithm = request.form['algorithm']
		data = X.values.tolist()
		print(data)
		if algorithm == "vns":
			lX = copy.deepcopy(X.values.tolist())
			Lcity = list()
			for i in range(0,len(lX)):
				Lcity.append(city(i,lX[i]))
			t = generalVNS(Lcity, 60)
			best_distance = t[0]
			t.pop(0)
			txt = list()
			for i in range(0, len(t)):
				txt.append(str(citiesNames[t[i].i]))
			txt.append(str(citiesNames[0]))
			print(txt)
			nameFile = createFile(txt,best_distance)
			return render_template('results.html',chemin=txt,distance=best_distance, fileLink=nameFile)
		elif algorithm == "dynamic":
			graph = copy.deepcopy(X.values.tolist())
			startCity = 0
			ltDistGlobale = list()
			listeCities = list()
			for i in range(0,len(graph)):
				listeCities.append(i)
			for i in listeCities:
				ltDistSpec = list()
				for j in listeCities:
					ltDistSpec.append(graph[i][j])
				ltDistGlobale.append(ltDistSpec)
			print(ltDistGlobale)
			#Chercher le chemin
			V=len(listeCities)
			vertex = [] 
			for i in range(V):
				if i != startCity:
					vertex.append(i)
			min_path = maxsize
			next_permutation=permutations(vertex)
			for i in next_permutation:
				current_pathweight = 0
				k = startCity
				for j in i:
					current_pathweight += ltDistGlobale[k][j]
					k = j
				current_pathweight += ltDistGlobale[k][startCity]
				min_path = min(min_path, current_pathweight)
				if min_path == current_pathweight:
					chemin = i
			print(min_path)
			txt = list()
			txt.append(str(citiesNames[startCity]))
			for i in chemin:
				txt.append(str(citiesNames[i]))
			txt.append(str(citiesNames[startCity]))
			nameFile = createFile(txt,min_path)
			return render_template('results.html',chemin=txt,distance=min_path, fileLink=nameFile)
		return render_template('upload.html')
	else:
		return render_template('upload.html')

#if __name__ == "__main__":
#    app.run()

#@app.route('/calcul', methods=['post'])
#def calculDynamic():
#	a = request.form['listeCities']
#	b = a.split(',')
#	listeCities = list()
#	for i in b:
#		listeCities.append(int(i))
#	startCity = int(request.form['startCity'])
#	graph = [[0,1334,1559,809,1334,1559,809],[1334,0,1343,1397,1334,1559,809],[1559,1343,0,921,1334,1559,809],[809,1397,921,0,809,1397,921],[1334,1334,1334,809,0,1397,921],[1559,1559,1559,1397,1397,0,921],[809,809,809,921,921,921,0]]
#	V=len(listeCities)
#	vertex = [] 
#	for i in range(V):
#		if i != startCity:
#			vertex.append(i)
#	min_path = maxsize
#	next_permutation=permutations(vertex)
#	for i in next_permutation:
#		current_pathweight = 0
#		k = startCity
#		for j in i:
#			current_pathweight += graph[k][j]
#			k = j
#		current_pathweight += graph[k][startCity]
#		min_path = min(min_path, current_pathweight)
#		if min_path == current_pathweight:
#			chemin = i
#	print(min_path)
#	txt = ""
#	for i in chemin:
#		txt=txt + str(i) + ", "
#	return txt