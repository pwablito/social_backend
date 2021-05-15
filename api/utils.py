import string
import random
import hashlib
import tempfile
import os
from .models import Friendship


def generate_unique_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def hash_password(plaintext, salt):
    return hashlib.md5((salt + plaintext).encode()).hexdigest()


def check_friends(first_user_id, second_user_id):
    is_friend = False
    if first_user_id == second_user_id:
        is_friend = True
    if Friendship.objects.all().filter(first_user_id=first_user_id,
                                       second_user_id=second_user_id).count() != 0:
        is_friend = True
    if Friendship.objects.all().filter(first_user_id=second_user_id,
                                       second_user_id=first_user_id).count() != 0:
        is_friend = True
    return is_friend


def send_email(content, subject, target_address, html=False, source_email="SMORP <no_reply@paulspencer.online>"):
    new_file, filename = tempfile.mkstemp()
    os.write(new_file, bytes(content, "utf-8"))
    os.close(new_file)
    email_headers = "From: {}".format(source_email)
    additional_options = ""
    if html:
        additional_options = "--content-type=text/html"
    os.system('mail -s "{}" -a "{}" {}  {} < {}'.format(
        subject,
        email_headers,
        additional_options,
        target_address,
        filename,
    ))
    os.remove(filename)
