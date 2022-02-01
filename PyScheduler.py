import requests
import json
import threading

dict_EV={}

def sendResponse(jsonRequest):
	jsonResponse={}
	#req=requests.post("http://parsec2.unicampania.it:10020/postmessage",jsonResponse)
	jsonResponse["sim_id"]=jsonRequest["message"]["id"]
	jsonResponse["time"]=int(jsonRequest["time"])+10
	jsonResponse["id"]=jsonRequest["message"]["id"]
	#print(jsonResponse)
	switchsubject=jsonRequest["message"]["subject"]
	if switchsubject=="LOAD":
		jsonResponse["subject"]= "ASSIGNED_START_TIME"
		jsonResponse["ast"]=jsonRequest["message"]["est"].strip()
		jsonResponse["producer"]="[0]:[0]"
		req=requests.post("http://parsec2.unicampania.it:10020/postmessage",jsonResponse)
		print("Req: ", req.text)
	elif switchsubject=="HC":
		jsonResponse["csvfile"]=jsonRequest["message"]["id"]+".csv"
		jsonResponse["subject"]="HC_PROFILE"
		#incompleto
		req=requests.post("http://parsec2.unicampania.it:10020/postmessage",jsonResponse)
	elif switchsubject=="EV":
		jsonResponse["subject"]= "EV_PROFILE"
		dict_EV_message_id=dict_EV[jsonRequest["message"]["id"]]
		dict_EV_message_id_capacity=dict_EV_message_id["capacity"]
		booked_charge=int(dict_EV_message_id_capacity)*int(jsonRequest["message"]["target_soc"])-int(jsonRequest["message"]["soc_at_arrival"])/100
		available_energy=int(dict_EV_message_id["max_ch_pow_ac"])*int(jsonRequest["message"]["actual_departure_time"]-int(jsonRequest["message"]["arrival_time"]))
		charged_energy=available_energy
		charged_0=int(dict_EV_message_id_capacity)*int(jsonRequest["message"]["soc_at_arrival"])/100
		if available_energy>=booked_charge:
			charging_time=3600*charged_energy/int(dict_EV_message_id["max_ch_pow_ac"])
			csvstr=int(jsonRequest["message"]["arrival_time"])+","+charged_0+"\n"
			csvstr+=(charging_time+int(jsonRequest["message"]["arrival_time"]))+","+(charged_energy+charged_0)
			#incompleto non ho capito come creare il blob

def getRequest():
	r =requests.get("http://parsec2.unicampania.it:10020/getmessage")
	json_object = json.loads(r.text)
	#pairs = json_object.items()
	message=json_object['message']
	subject=""
	print(json_object)
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


