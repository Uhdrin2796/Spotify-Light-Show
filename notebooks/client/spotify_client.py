#!/usr/bin/env python
# coding: utf-8

# In[1]:


import datetime
import base64
from urllib.parse import urlencode

import requests


# In[18]:


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"
    base_url = "https://api.spotify.com/v1"
    method = "POST"
    
    
    def __init__(self,client_id,client_secret,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret =client_secret
        
    def get_client_credentials(self):
        """"""
        "Returns a base64 encoded string"
        """"""
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exemption("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}" #Client details as string
        client_creds_b64 =base64.b64encode(client_creds.encode()) #Turn string into base64 type
        return client_creds_b64.decode() #Return as decoded base64 string
        
    def get_token_headers(self):
        
        client_creds_b64 = self.get_client_credentials() #get decoded client credentials.
        return {
            "Authorization" : f"Basic {client_creds_b64}" 
        }
    def get_token_data(self):
        return {
            "grant_type":"client_credentials"
        }
    
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200,299):
            raise Exception("Could not authenticate client")
            #return False
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        self.access_token = access_token
        expires_in = data['expires_in'] #in seconds
        token_type = data['token_type'] 
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True
        
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token
    
    def get_resource_headers(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        return headers
    
    def get_id(self,):
        pass
    
    def get_resource(self, lookup_id, resource_type='albums',version='v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_headers()
        r = requests.get(endpoint, headers = headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()
        
    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')
    
    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')
    
    def get_track(self,):
        pass
    def get_track_features(self,):
        pass
    def get_audio_analysis(self,):
        pass
        
    def base_search(self, query_params): #type is a built-in python operator
        headers = self.get_resource_headers()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        print(lookup_url)
        r = requests.get(lookup_url, headers=headers)
        print(r.status_code)
        if r.status_code not in range(200,299):
            return {}
        return r.json()
    
    def search(self, query=None, operator=None, operator_query=None,search_type='artist'):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query,dict):
            query = " ".join([f"{k}:{v}" for k,v in query.items()])
        if operator != None and operator_query != None:
            if operator == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
            operator = operator.upper()
        query_params = urlencode({"q": query, "type": search_type.lower()})
        print(query_params)
        return self.base_search(query_params)
    
    

