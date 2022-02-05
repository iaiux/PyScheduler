import csv

import requests
import json
import threading

dict_EV={}

def sendResponse(jsonRequest):
	jsonResponse={}
	jsonResponse["sim_id"]=jsonRequest["message"]["id"]
	jsonResponse["time"]=int(jsonRequest["time"])+10
	jsonResponse["id"]=jsonRequest["message"]["id"]
	switchsubject=jsonRequest["message"]["subject"]
	if switchsubject=="LOAD":
		jsonResponse["subject"]= "ASSIGNED_START_TIME"
		jsonResponse["ast"]=jsonRequest["message"]["est"].strip()
		jsonResponse["producer"]="[0]:[0]"
		req=requests.post("http://parsec2.unicampania.it:10020/postanswer",jsonResponse)
		print("Req: ", req.text)
	#per ora gli hc non ci interessano quindi commento questo codice
	#elif switchsubject=="HC":
	#	jsonResponse["csvfile"]=jsonRequest["message"]["id"]+".csv"
		#jsonResponse["subject"]="HC_PROFILE"
		#incompleto
		#req=requests.post("http://parsec2.unicampania.it:10020/postmessage",jsonResponse)
	elif switchsubject=="EV":
		jsonResponse["subject"]= "EV_PROFILE"
		dict_EV_message_id=dict_EV[jsonRequest["message"]["id"]]
		dict_EV_message_id_capacity=dict_EV_message_id["capacity"]
		booked_charge=float(dict_EV_message_id_capacity)*float(jsonRequest["message"]["target_soc"])-float(jsonRequest["message"]["soc_at_arrival"])/100
		available_energy=float(dict_EV_message_id["max_ch_pow_ac"])*(int(jsonRequest["message"]["actual_departure_time"])-(int(jsonRequest["message"]["arrival_time"])))
		charged_energy=available_energy
		charged_0=float(dict_EV_message_id_capacity)*int(jsonRequest["message"]["soc_at_arrival"])/100
		if available_energy>=booked_charge:
			charging_time=3600*charged_energy/float(dict_EV_message_id["max_ch_pow_ac"])
		csvstr=(str(jsonRequest["message"]["arrival_time"]))+","+str(charged_0)+"\n"
		csvstr+=str(charging_time)+str(jsonRequest["message"]["arrival_time"])+","+str(charged_energy)+str(charged_0)+"\n"
		with open("test.csv",'w') as f:
			f.write(csvstr)
		r = requests.post("http://parsec2.unicampania.it:10020/postanswer", files={'file': open('test.csv','r')})
		print("Req: ", r.text)

def getRequest():
	r =requests.get("http://parsec2.unicampania.it:10020/getmessage")
	json_object = json.loads(r.text)
	#pairs = json_object.items()
	message=json_object['message']
	subject=""
	#print(json_object)
	if message!="no new message": #ho dovuto mettere questo if perché se non lo mettessi
		subject=message['subject'] #quando il messaggio è no new message non ha subject e quindi
									#mi va in errore perché non è un dict
	if subject== "CREATE_EV":
		dict_EV[message['id']]=message
	if subject=="LOAD" or subject=="HC" or subject=="EV":
		sendResponse(json_object)

	threading.Timer(2.0, getRequest).start()


if __name__ == '__main__':
	getRequest()


