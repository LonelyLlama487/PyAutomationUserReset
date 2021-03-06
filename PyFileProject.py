from simple_salesforce import Salesforce as sf
import requests as req
import configparser as cfg

def credParser():
    try:
        cg = cfg.ConfigParser()
        cg.read('creds.ini')
        connVals = {}
        if 'CREDS' in cg :
            connVals = {'username': cg['CREDS']['username'],
                        'password': cg['CREDS']['password'],
                        'secret': cg['CREDS']['sec'],
                        'consumer_key': cg['CREDS']['consumer_key'],
                        'consumer_secret': cg['CREDS']['consumer_secret'],
                        'access_token':cg['CREDS']['access_token'],
                        'prod_url':cg['CREDS']['prod_url'],
                        'sandbox_url':cg['CREDS']['sandbox_url']}
        return connVals
    except:
        print("[-]CredParser got an exception")

def sessionInitiator(uname,passkey,sec):
    try:
        s = sf(username=uname,password=passkey,security_token=sec)
        #print('Connected to : '+s.base_url)
        return s
    except:
        print("[-]Session cannot be initiated")

def passResetter(uid):
    userCred = credParser()
    payload = {
    'grant_type': 'password',
    'client_id': userCred['consumer_key'],
    'client_secret': userCred['consumer_secret'],
    'username': userCred['username'],
    'password': userCred['password'] + userCred['secret']
    }
    checkv2 = sessionInitiator(userCred['username'],userCred['password'],userCred['secret'])
    checkInstance = checkv2.query("SELECT Id, InstanceName, IsSandbox, Name, OrganizationType FROM Organization")
    final_url = userCred['prod_url'] if (checkInstance['records'][0]['IsSandbox'] != "False") else userCred['sandbox_url']
    resp = req.post(final_url, data = payload, json = {})

    if (resp.ok):
        tok = resp.json()['access_token']
        chk_url = resp.json()['instance_url'] + "/services/apexrest/User/"
        r = req.post(chk_url, headers = {"Authorization": "Bearer " + tok}, json = {"uid": uid})
        print(r.json())
    else:
        print("[-] Connection Ended with status code :" + resp.status_code)

#Used for external calls for user reset outside for the chatbot
def externalUserResetCallout(uname):
    try:
        userCred = credParser()
        checkv2 = sessionInitiator(userCred['username'],userCred['password'],userCred['secret'])
        print("Connected to : "+checkv2.base_url)
        if(checkv2):
            query = "select id,Name,Email from user where Name like '%"+uname+"%'";
            op = checkv2.query_all(query)
            if(not(len(op['records'][0]['Id'])>0)):
                print(">User Not Found")
            else:
                passResetter(op['records'][0]['Id'])
    except:
        print("Cannot find user or you have entered some invalid input")

if __name__ == '__main__' :
    try:
        userCred = credParser()
        check = sessionInitiator(userCred['username'],userCred['password'],userCred['secret'])
        if(check):
            userChoice = str(input('[+]Please Enter the Name:'))
            query = "select id,Name,Email from user where Name like '%"+userChoice+"%'";
            op = check.query_all(query)
            print(op['records'][0]['Name'])
            print(op['records'][0]['Id'])
            print(op['records'][0]['Email'])

            ch = str(input('[+]Are you sure you want to reset password for this user.(Y or N)'))
            if(ch == 'Y' and len(op['records'][0]['Id'])>0):
                passResetter(op['records'][0]['Id'])
            else:
                print("[+] Session Terminated Successfully")
    except:
        print("[-]Failed to Initiate")
