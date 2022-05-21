import requests
import json
import os, sys, time
import time as t
import telnyx

trucks = [] #vins stored here
zipcodes = ["10001", "90001"] #Enter all ZIP Codes here


def sms(zipcode):
	telnyx.api_key = "KEY" # Your Telnyx API Key
	telnyx.Message.create(
	    to="+1", #Your phone number
	    from_="+1", #Your Telnyx phone number
	    text="There is another TRX in stock at " + zipcode + ": https://www.ramtrucks.com/new-inventory.ram_1500_dt.2022.html?modelYearCode=IUT202220&radius=250"
	)

def loop(method):
	while True:
		for zipcode in zipcodes:
			header = { 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0' }
			url = "https://www.ramtrucks.com/hostd/inventory/getinventoryresults.json?func=SALES&includeIncentives=N&matchType=X&modelYearCode=IUT202220&pageNumber=1&pageSize=10&radius=250&sortBy=0&variation=TRX&zip=" + zipcode
			response = requests.get(url=url, headers=header, timeout=10)
			loadjson = json.loads(response.text)

			stock = loadjson["result"]["data"]["metadata"]["exactMatchCount"]
			if int(stock) >= 1:
				for x in range(int(stock)):
					matchtype = loadjson["result"]["data"]["vehicles"][x]["match"]["matchLevel"]
					vin = loadjson["result"]["data"]["vehicles"][x]["vin"]
					color = loadjson["result"]["data"]["vehicles"][x]["exteriorColorDesc"]
					vehicleDesc = loadjson["result"]["data"]["vehicles"][x]["vehicleDesc"]
					dealercode = loadjson["result"]["data"]["vehicles"][x]["dealerCode"]
					price = loadjson["result"]["data"]["vehicles"][x]["price"]["msrp"]

					if matchtype == "Exact":
						if vin not in trucks:
							trucks.append(vin) # Append Array 

							# Get Dealer Information
							getdealer = requests.get(url="https://www.ramtrucks.com/bdlws/MDLSDealerLocator?zipCode=" + zipcode + "&func=SALES&radius=250&brandCode=R&resultsPerPage=999", headers=header, timeout=10)
							dealerjson = json.loads(getdealer.text)
							for a in range(999):
								if dealercode == dealerjson["dealer"][a]["dealerCode"]:
									name = dealerjson["dealer"][a]["dealerName"]
									address = dealerjson["dealer"][a]["dealerAddress1"]
									city = dealerjson["dealer"][a]["dealerCity"]
									state = dealerjson["dealer"][a]["dealerState"]
									phone = dealerjson["dealer"][a]["phoneNumber"]
									dealerzip = dealerjson["dealer"][a]["dealerZipCode"]
									break
								else:
									pass

							print("[%s] New vehicle at %s [%s, %s %s] [PHONE: %s] [PRICE: $%s]" % (vin, name, city, state, dealerzip[0:5], phone, price))
							if method == 2:
								sms(dealerZipCode)
							else:
								pass #Method does not match
						else:
							pass #VIN Already in Database
			else:
				print("No matches found in ZIP: %s" % (zipcode))
		if method == 1:
			break
		else:
			if method == 2:
				print("Rechecking in 2 minutes...")
				time.sleep(120)
			else:
				pass

loop(1)
print("Running main process now!")
loop(2)
