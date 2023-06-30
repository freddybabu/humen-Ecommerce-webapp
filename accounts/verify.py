import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

TWILIO_VERIFY_SERVICE_SID='VA17d6c4e0348d4667123fc544b0830c25'
TWILIO_ACCOUNT_SID='AC529b57fdcebcfa5db3696c73959779e4'
TWILIO_AUTH_TOKEN='ca0ab8a793cb7534e8db3939ae6e983d'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
verify = client.verify.services(TWILIO_VERIFY_SERVICE_SID)


def send(phone):
    verify.verifications.create(to=phone, channel='sms')


def check(phone, code):
    try:
        result = verify.verification_checks.create(to=phone, code=code)
    except TwilioRestException:
        print('no')
        return False
    return result.status == 'approved'
