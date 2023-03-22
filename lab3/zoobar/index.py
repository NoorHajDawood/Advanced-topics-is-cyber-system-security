from flask import g, render_template, request
from login import requirelogin
from debug import *
from zoodb import *
from PIL import Image
# max image size is 2MB
MAX_IMAGE_SIZE = 2 * 1024 * 1024
# array of valid image types same as 'image/*'
VALID_IMAGE_TYPES = ['jpg', 'jpeg', 'png']
@catch_err
@requirelogin
def index():
    if 'picture_upload' in request.files:
        persondb = person_setup()
        person = persondb.query(Person).get(g.user.person.username)
        if person is None:
            return render_template('index.html')
        # check file type before saving
        if request.files['picture_upload'].filename == '':
            return render_template('index.html')
        if request.files['picture_upload'].filename.split('.')[-1].lower() not in VALID_IMAGE_TYPES:
            return render_template('index.html')
        pil_image = Image.open(request.files['picture_upload'])
        pil_image = pil_image.resize((200, 200), Image.ANTIALIAS)
        pil_image = pil_image.convert('RGB')
        pil_image.save('zoobar/static/pictures/%s.jpg' % person.username)
        person.picture = '/zoobar/static/pictures/%s.jpg' % person.username
        persondb.commit()

        ## also update the cached version (see login.py)
        g.user.person.picture = person.picture
    if 'profile_update' in request.form:
        persondb = person_setup()
        person = persondb.query(Person).get(g.user.person.username)
        person.profile = request.form['profile_update']
        persondb.commit()

        ## also update the cached version (see login.py)
        g.user.person.profile = person.profile
    return render_template('index.html')
