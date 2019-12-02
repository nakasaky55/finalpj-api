import os
from dotenv import load_dotenv
load_dotenv()




class Config(object):
  DEBUG=True
  SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
  SECRET_KEY='supersecret'
  FLASK_ADMIN_SWATCH = 'cerulean'
  SEND_FILE_MAX_AGE_DEFAULT = 0
  API_MAIL_KEY = os.environ.get('API_MAIL_KEY')