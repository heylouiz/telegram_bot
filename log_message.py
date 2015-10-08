#!/usr/bin/env python

class logMessage:
    def __init__(self, user_name='', message=''):
        self.user_name = user_name
        self.message = message
        
    def getMessage(self):
        return self.message
        
    def getUsername(self):
        return self.user_name