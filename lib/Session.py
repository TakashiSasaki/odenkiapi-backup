from __future__ import unicode_literals, print_function
from model.OdenkiUser import OdenkiUser
from lib.json.JsonRpcError import EntityNotFound
from model.TwitterUser import TwitterUser
from model.GmailUser import GmailUser
from model.EmailUser import EmailUser
from gdata.marketplace.data import Entity

def fillOdenkiUserByTwitterUser():
    try:
        odenki_user = OdenkiUser.loadFromSession()
        assert isinstance(odenki_user, OdenkiUser)
        return
    except EntityNotFound:
        twitter_user = TwitterUser.loadFromSession()
        assert isinstance(twitter_user, TwitterUser)
        odenki_user = OdenkiUser.getByOdenkiId(twitter_user.odenkiId)
        assert isinstance(odenki_user, OdenkiUser)
        odenki_user.saveToSession()

def fillOdenkiUserByGoogleUser():
    try:
        odenki_user = OdenkiUser.loadFromSession()
        assert isinstance(odenki_user, OdenkiUser)
        return
    except EntityNotFound:
        gmail_user = GmailUser.loadFromSession()
        assert isinstance(gmail_user, GmailUser)
        odenki_user = OdenkiUser.getByOdenkiId(gmail_user.odenkiId)
        assert isinstance(odenki_user, OdenkiUser)
        odenki_user.saveToSession()

def fillOdenkiUserByEmailUser():
    try:
        odenki_user = OdenkiUser.loadFromSession()
        assert isinstance(odenki_user, OdenkiUser)
        return
    except EntityNotFound:
        email_user = EmailUser.loadFromSession()
        assert isinstance(email_user, EmailUser)
        odenki_user = OdenkiUser.getByOdenkiId(email_user.odenkiId)
        assert isinstance(odenki_user, OdenkiUser)
        odenki_user.saveToSession()

def fillOdenkiUser():
    try: fillOdenkiUserByEmailUser()
    except EntityNotFound: pass
    try: fillOdenkiUserByGoogleUser()
    except EntityNotFound: pass
    try: fillOdenkiUserByTwitterUser()
    except EntityNotFound: pass

def fillUser():
    fillOdenkiUser()
    try: fillEmailUser()
    except EntityNotFound: pass
    try: fillGmailUser()
    except EntityNotFound: pass
    try: fillTwitterUser()
    except EntityNotFound: pass
    fillOdenkiUser()
    
def fillTwitterUser():
    odenki_user = OdenkiUser.loadFromSession()
    assert isinstance(odenki_user, OdenkiUser)
    try:
        twitter_user = TwitterUser.loadFromSession()
    except EntityNotFound:
        twitter_user = TwitterUser.getByOdenkiId(odenki_user.odenkiId)
    assert isinstance(twitter_user, TwitterUser)
    
    if twitter_user.odenkiId is None:
        twitter_user.odenkiId = odenki_user.odenkiId
        twitter_user.put()
    twitter_user.saveToSession()

def fillEmailUser():
    odenki_user = OdenkiUser.loadFromSession()
    assert isinstance(odenki_user, OdenkiUser)
    try:
        email_user = EmailUser.loadFromSession()
    except EntityNotFound: 
        email_user = EmailUser.getByOdenkiId(odenki_user.odenkiId)
    assert isinstance(email_user, EmailUser)

    if email_user.odenkiId is None:
        email_user.odenkiId = odenki_user.odenkiId
        email_user.put()
    email_user.saveToSession()

def fillGmailUser():
    odenki_user = OdenkiUser.loadFromSession()
    assert isinstance(odenki_user, OdenkiUser)
    try:
        gmail_user = GmailUser.loadFromSession()
    except EntityNotFound: 
        gmail_user = GmailUser.getByOdenkiId(odenki_user.odenkiId)
    assert isinstance(gmail_user, GmailUser)

    if gmail_user.odenkiId is None:
        gmail_user.odenkiId = odenki_user.odenkiId
        gmail_user.put()
    gmail_user.saveToSession()
