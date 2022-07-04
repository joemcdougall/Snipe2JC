# Look at each laptop in Snipe IT, find the hostname, and match it against a JumpCloud agent

# modules for JSON APIs
import requests
from requests.structures import CaseInsensitiveDict

# modules for AWS SNS
import boto3

# modules needed for Google Workspace alert
from json import dumps
from httplib2 import Http

# variables for JC, Snipe IT, AWS SNS, and Google Workspace

Snipe_ApiKey = "XXXXXXXXXXXX"
JC_ApiKey = "XXXXXXXXXXXX"

JC_url = "https://console.jumpcloud.com/api/v2/systeminsights/system_info"
JC_headers = {"x-api-key": JC_ApiKey,"Accept": "application/json"}

AWS_REGION = 'eu-west-2'
AWS_ACCESS_KEY_ID = 'XXXXXXXXXXXX'
AWS_SECRET_ACCESS_KEY = 'XXXXXXXXXXXX' 
aws_topic_arn = "arn:aws:sns:eu-west-2:939804405085:XXXXXXXXXXXX"

workspace_webhook_url = "https://chat.googleapis.com/v1/spaces/XXXXXXXXXXXX"

# define SNS client using AWS creds

sns_client = boto3.client('sns', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# function for SNS

def publish_message(topic_arn, message, subject):

    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject,
    )


# function to convert bytes to gigabytes

def bytesToGB(inputBytes):
	inputBytes = int(inputBytes)
	return int(inputBytes/1073741824)


# function to send alert to Workspace webhook

def sendWorkspaceAlert(inputMessage):
    
    # Workspace webhook
    
    bot_message = {
        'text': inputMessage}
    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
    http_obj = Http()
    response = http_obj.request(
        uri=workspace_webhook_url,
        method='POST',
        headers=message_headers,
        body=dumps(bot_message),
    )


# list every snipe asset

snipe_url = ("https://XXXXXXXXXXXX.snipe-it.io/api/v1/hardware/")
headers = {"Authorization": "Bearer "+Snipe_ApiKey,"Accept": "application/json"}
response = requests.get(snipe_url, headers=headers)
data = (response.json())




# number of Snipe IT assets returned 

count_snipe_assets = (data["total"])

print ("Assets returned: " + str(count_snipe_assets) + "\n")


error_log_snipe = ""

# for each, print the Snipe IT ID and hostname (asset name)

count = 0

while count < count_snipe_assets:

	snipe_id = (data["rows"][count]["id"])
	snipe_name = (data["rows"][count]["name"])
	snipe_ern = (data["rows"][count]["asset_tag"])

	# We only want laptops, not door fobs or other assets, so match for XXXXXXXXXXXX 
	# NOTE - in my organisation, all laptops are named in the style "ORG-LAP-001" - hence wanting to scan for laptop names only. You may want to strip this code.

	if (snipe_name.__contains__("XXXXXXXXXXXX")):
		currentlyWorkingOn = f"Working on {snipe_ern} - {snipe_name} ({snipe_id})"
		print ("\n")
		print (currentlyWorkingOn)
		
		# look up asset on JumpCloud

		jc_lookup_asset = {"skip":"0","sort":"","filter":"hostname:eq:"+snipe_name,"limit":"1"}

		jc_response = requests.get(JC_url, headers=JC_headers, params=jc_lookup_asset)
		jc_data = (jc_response.json())

		# old inactive machines that JC doesn't see as recently used don't return anything, so ignore these
		


		if (len(jc_data)) != 0:

			hostname = str(jc_data[0]['hostname'])
			jc_system_id = jc_data[0]['system_id']
			ram = jc_data[0]['physical_memory']
			cpu_type = jc_data[0]['cpu_brand']
			cpu_cores = jc_data[0]['cpu_physical_cores']
			gbram = bytesToGB(ram)	


			systemstring = f"{hostname} has {gbram} GB of RAM, and is running on a {cpu_type} with {cpu_cores} cores. \nJumpCloud knows this system as {jc_system_id}"

			print (systemstring)

			# update Snipe IT with data from JumpCloud


			snipe_update_url = f"https://XXXXXXXXXXXX.snipe-it.io/api/v1/hardware/{snipe_id}"

	
			# NOTE - These fields are custom, you need to define them in Snipe-IT - make sure to use the correct field names!
			# Manual - https://snipe-it.readme.io/docs/custom-fields
		
			snipe_update_payload = {
			    "_snipeit_ram_11": gbram,
			    "_snipeit_cpu_13": cpu_type,
			    "_snipeit_jumpcloud_system_id_12": jc_system_id,
			    "_snipeit_cpu_cores_14": cpu_cores
			}
			snipe_update_headers = {
			    "Accept": "application/json",
			    "Authorization": "Bearer "+Snipe_ApiKey,
			    "Content-Type": "application/json"
			}

			snipe_update_response = requests.patch(snipe_update_url, json=snipe_update_payload, headers=snipe_update_headers)
			
			# check update worked

			if (snipe_update_response.status_code) != 200:
				print ("DID NOT UPDATE IN SNIPE !!! Debugging info: ")
				print (snipe_update_response.json)
				print ("\n")


		else:

			print ("JumpCloud could not locate machine")

			error_log_snipe = error_log_snipe + "Machine: " + snipe_name + " - " + snipe_ern + " - JC could not locate machine \n\n"

		print ("\n-------------------------------------------------")
			

	count = count +1


# publish error log

message = 'Errors found in running JC2Snipe today: \n------------------------------\n\n '+error_log_snipe
subject = 'JC2Snipe - Errors occured in script'

# send to AWS SNS
message_id = publish_message(aws_topic_arn, message, subject)
print ("published to topic " +aws_topic_arn)

# send to Google Workspace
sendWorkspaceAlert(error_log_snipe)