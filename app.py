from flask import Flask, render_template,request,send_file,jsonify, redirect, session, jsonify
from audio_encrpy import Steganography
from audio_decrpy import Steganaograpy_decryption
#from image_encrpy import Steganography
#from image_decrpy import Steganaograpy_decryption
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import image_encrypt



app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    allowed = db.Column(db.String(120))

    def __repr__(self):
        return '<User %r>' % self.username

class Encrypted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    filetype = db.Column(db.String(80), nullable=False)
    allowed = db.Column(db.String(120), nullable=False)
    user = db.Column(db.String(120), nullable=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # user = db.relationship('User', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return '<User %r>' % self.username


db.create_all()
app.config['UPLOAD_FOLDER'] = './uploads'
app.secret_key = 'dsdsds34567890'
app.config['EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','wav'}



@app.route('/signin', methods = ["POST", "GET"])
def Signin():

    if request.method == 'POST':
        data = request.form
        
        user = User.query.filter_by(username = data.get('username')).first()
        if user:
            print(user)
            if user.password == data.get('password'):
                print('login success')
                session['user'] = user.username
                session['user_id'] = user.id
                return jsonify('success')
                
            else:
                return jsonify('failed')
        else:
            return jsonify('failed')

    return render_template('signin.html')

@app.route('/signup', methods = ["POST", "GET"])
def Signup():
    if request.method == 'POST':
        data = request.form
        user = User(username = data.get('username'),allowed = '', email = data.get('email'), password = data.get('password'))
        db.session.add(user)
        db.session.commit()
        print('data saved!!')
        return jsonify('success')

    return render_template('signup.html')

@app.route('/logout')
def Logout():
    session['user'] = None
    return redirect('/signin')

@app.route('/loader')
def loader():
    if not session.get('user'):
        return redirect('/signin')
    return render_template('loader.html', loggedin = session.get('user'))

@app.route('/')
def index():
    if not session.get('user'):
        return redirect('/signin')
    return render_template('homepage.html', loggedin = session.get('user'))


@app.route('/encode')
def encode():
    if not session.get('user'):
        return redirect('/signin')
    return render_template('audio_encrypt.html', loggedin = session.get('user'))
        

@app.route('/decode')
def decode():
    if not session.get('user'):
        return redirect('/signin')
    return render_template('audio_decrypt.html', loggedin = session.get('user'))


@app.route('/iencode')
def imageEncode():
    if not session.get('user'):
        return redirect('/signin')
    return render_template('image_encrypt.html', loggedin = session.get('user'))
        

@app.route('/idecode')
def imageDecode():
    if not session.get('user'):
        return redirect('/signin')
    return render_template('image_decrypt.html', loggedin = session.get('user'))


@app.route('/uploadfile',methods=[ "GET",'POST'])
def uploadLabel():
    file=request.files.get('file')
    print(file)
    print(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return jsonify({'message' : 'success'})

@app.route('/uploadimagefile',methods=[ "GET",'POST'])
def uploadImage():
    file=request.files.get('file')
    print(file)
    print(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'images', file.filename))
    return jsonify({'message' : 'success'})

@app.route('/encrypt',methods=["POST"])
def stegno_enc():
    msgs=request.form.get("message")
    print("msgs")
    sngs = request.files.get('file')
    
    file_name = secure_filename(sngs.filename)
    
    if file_name.endswith('.mp3'):
        print(file_name) 
        os.system(f"""static/exe/ffmpeg -i /uploads/{file_name} -acodec pcm_u8 -ar 22050 /uploads/{file_name.replace('.mp3','.wav')}""")
        file_name = f'{file_name[:-4]}.wav'
    # filename=file_name[:file_name.rindex(".")]+" encrypted.wav"\
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    if os.path.exists(filepath):
        sngs.save(filepath)
        print(filepath)
        file_path = Steganography().lsb(filepath,msgs)
        enc_file = Encrypted(filename = file_path, filetype = 'Audio', date = datetime.today().strftime('%d_%m_%Y'), allowed = '', user = session.get('user_id'))
    
        db.session.add(enc_file)
        db.session.commit()

        print("work done", file_name)
    else:
        print(filepath)
        print(os.listdir('uploads'))
        print('error finding wav file')
    session['encImgFile'] = 'outputs/encoded_'+file_name
    return jsonify('success')

@app.route('/encsuccess')
def EncSuccess():
    return render_template("encrpy_success.html", filename = session.get('encImgFile'))


@app.route('/encryptimage',methods=["POST"])
def stegno_image_enc():
    msgs=request.form.get("message")
    print(msgs)
    sngs = request.files.get('file')
    enc_file = Encrypted(filename = sngs.filename,filetype = 'Image', date = datetime.today().strftime('%d_%m_%Y'), allowed = '', user = session.get('user_id'))
    
    db.session.add(enc_file)
    db.session.commit()

    file_name = secure_filename(sngs.filename)
    
    # if file_name.endswith('.mp3'):
    #     print(file_name) 
    #     os.system(f"""static/exe/ffmpeg -i /uploads/{file_name} -acodec pcm_u8 -ar 22050 /uploads/{file_name.replace('.mp3','.wav')}""")
    #     file_name = f'{file_name[:-4]}.wav'
    # # filename=file_name[:file_name.rindex(".")]+" encrypted.wav"\

    filepath = os.path.join(app.config['UPLOAD_FOLDER'],'images', file_name)
    # if os.path.exists(filepath):
    #     sngs.save(filepath)
    #     print(filepath)
    #     file_data = Steganography().lsb(filepath,msgs)
    #     print("work done", file_name)
    # else:
    #     print(filepath)
    #     print(os.listdir('uploads'))
    #     print('error finding wav file')

    path = image_encrypt.encode(filepath, msgs)
    session['encImgFile'] = path
    return jsonify('success')


@app.route('/decrypt',methods=['POST'])
def stegno_dec():
    if not session.get('user'):
        return redirect('/signin')
    sngs = request.files.get('file')
    filename = secure_filename(sngs.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    sngs.save(filepath)
    print("till")
    decoded_msg=Steganaograpy_decryption().decoder(filepath)
    print("worked till here")
    print(decoded_msg)
    return render_template("decrpy_success.html",decoded_msg=decoded_msg, loggedin = session.get('user'))


@app.route('/decrypt-image',methods=['POST'])
def stegno_dec_image():
    sngs = request.files.get('file')
    filename = secure_filename(sngs.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'images', filename)
    sngs.save(filepath)
    print("till")
    decoded_msg=image_encrypt.decode(filepath)
    print("worked till here")
    print(decoded_msg)
    return render_template("image-decrpy_success.html",decoded_msg=decoded_msg)

@app.route("/return-file")
def return_file():
    filename= request.args.get('filename')
    if filename:
        if filename.endswith('png'):
            return send_file(os.path.join('./outputs/images', filename))
        else:
            return send_file(os.path.join('./outputs', filename))
    else:
        return send_file(session.get('encImgFile'))

@app.route('/processes',methods=['POST'])
def process():
    song=request.form["file"]

    mesg=request.form["message"]

    if song and mesg:
        return jsonify({"success":" encryption"})

    else:
        return jsonify({'error':"Missing data"})


@app.route('/sharedash')
def sharingDashboard():

    if not session.get('user'):
        return redirect('/signin')

    currentUser = User.query.filter_by(id = session.get('user_id')).first()

    all_users = User.query.all()
    # files = Encrypted.query.filter_by(user_id=session.get('user_id'))
    files = []
    for file in Encrypted.query.all():
        if file.user == str(session.get('user_id')):
            files.append(file)
    print(currentUser.allowed)
    shared_files = []
    for file in Encrypted.query.all():
        if str(file.id) in currentUser.allowed:
            shared_files.append(file)

    return render_template('sharedash.html', all_users = all_users, shared_files = shared_files,  files = files, loggedin = session.get('user'))

@app.route('/share')
def sharing():
    if not session.get('user'):
        return redirect('/signin')
    file_id = request.args.get('file_id')

    all_users = User.query.all()
    sel_file = Encrypted.query.filter_by(id=file_id).first()
    return render_template('sharefile.html', all_users = all_users, file = sel_file, loggedin = session.get('user'))

@app.route('/allow')
def allowuser():
    user_id = request.args.get('user_id')
    file_id = request.args.get('file_id')
    sel_user = User.query.filter_by(id=user_id).first()
    if file_id not in sel_user.allowed:
        sel_user.allowed +=f'{file_id},'
    # sel_user.update()
    db.session.commit()
    return jsonify('success')

@app.route('/shared')
def allowedfiles():

    if not session.get('user'):
        return redirect('/signin')

    files = User.query.filter(User.allowed.contains(session.get("username")))
    print(files)
    
    return render_template('shared.html', files = files, loggedin = session.get('user'))



@app.route('/viewfile')
def ViewFile():
    id = request.args.get('id')
    file = Encrypted.query.filter_by(id = id).first()
    sharedusers = []
    unsharedusers = []

    for user in User.query.all():
        if user.username == session.get('user'):
            continue
        if str(file.id) in user.allowed:
            sharedusers.append(user)
        else:
            unsharedusers.append(user)

    return render_template('filedash.html', file = file, sharedusers = sharedusers, unsharedusers = unsharedusers)
	
@app.route('/deleteuser')
def Delete():
    id = request.args.get('id')
    user = User.query.filter_by(id = id).first()
    db.session.delete(user)
    # db.session.commit()
    return 'User Deleted!!'

@app.route('/remuser')
def removeUser():
    user_id = request.args.get('user_id')
    file_id = request.args.get('file_id')
    print(file_id)
    sel_user = User.query.filter_by(id = user_id).first()
    sel = sel_user.allowed
    sel = sel.split(',')
    sel.remove(str(file_id))
    sel = ','.join(sel)
    print(sel)
    sel_user.allowed = sel
    sel_user.allowed.strip(',')
    db.session.commit()
    return redirect('/sharedash')

if __name__=="__main__":
    app.run(debug=True,threaded=True)

    
    
    

