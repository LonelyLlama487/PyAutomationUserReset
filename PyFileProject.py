from simple_salesforce import Salesforce as sf
import requests as req
import configparser as cfg

def credParser():
    cg = cfg.ConfigParser()
    cg.read('creds.ini')
    connVals = {}
    if 'CREDS' in cg :
        connVals = {'username': cg['CREDS']['username'],
                    'password': cg['CREDS']['password'],
                    'secret': cg['CREDS']['sec'],
                    'consumer_key': cg['CREDS']['consumer_key'],
                    'consumer_secret': cg['CREDS']['consumer_secret'],
                    'access_token':cg['CREDS']['access_token']}
    return connVals

def sessionInitiator(uname,passkey,sec):
    try:
        s = sf(username=uname,password=passkey,security_token=sec)
        print('Connected to : '+s.base_url)
        return s
    except:
        print("An exception occurred")


userCred = credParser()
check = sessionInitiator(userCred['username'],userCred['password'],userCred['secret'])
if(check):
    userChoice = str(input('Please Enter the username:'))
    query = "select id,Name,Email from user where Name like '%"+userChoice;
    op = check.query_all(query+"%'")
    print(op['records'][0]['Name'])
    print(op['records'][0]['Id'])
    print(op['records'][0]['Email'])
    #print(check.User.describe())


    ch = str(input('Are you sure you want to reset password for this user.(Y or N)'))
    if(ch == 'Y' and len(op['records'][0]['Id'])>0):
        payload = {
            'grant_type': 'password',
            'client_id': userCred['consumer_key'],
            'client_secret': userCred['consumer_secret'],
            'username': userCred['username'],
            'password': userCred['password']+userCred['secret']
        }
        prod_url="https://login.salesforce.com/services/oauth2/token"
        resp = req.post(prod_url, data=payload, json={})
        if(resp.ok):
            print(resp.json())
            tok = resp.json()['access_token']
            chk_url = resp.json()['instance_url']+"/services/apexrest/User/"
            r = req.post(chk_url, headers = {"Authorization":"Bearer " + tok},json={"uid" : op['records'][0]['Id']})
            print(r.json())
            
            
