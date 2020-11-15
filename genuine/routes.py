import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from genuine import app, db, bcrypt, mail
from genuine.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm)
from genuine.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import Flask, Response

from flask import Flask, make_response
import re
import csv
import re
import emoji
import nltk
import pandas as pd
import numpy as np
import tweepy  # To consume Twitter's API  # For number computing
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, send_file
#from geopy.exc import GeocoderTimedOut
#from geopy.geocoders import Nominatim
from textblob import TextBlob
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import TweetTokenizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from sklearn.feature_extraction.text import TfidfVectorizer
from keras.models import Sequential
from keras.layers import Dense
import h5py
from tensorflow.keras.models import load_model
from scipy.sparse import hstack
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import csv
import re
import emoji
import nltk
import pandas as pd
import numpy as np
import tweepy  # To consume Twitter's API  # For number computing
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, send_file

from textblob import TextBlob
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import TweetTokenizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from sklearn.feature_extraction.text import TfidfVectorizer
from keras.models import Sequential
from keras.layers import Dense
import h5py
from tensorflow.keras.models import load_model
from scipy.sparse import hstack

#nltk.download()
import collections
from nltk.corpus import stopwords
stemmer=nltk.PorterStemmer()
stops = set(stopwords.words("english"))


@app.route("/")

@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@app.route('/credentials',methods=['GET','POST'])
def credentials():
    password=request.form['password']
    if(password=="open"):
        return redirect(url_for('login'))
    return('Wrong Access Code')



@app.route("/register", methods=['GET', 'POST'])
def register():
    #if current_user.is_authenticated:
     #   return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    #if current_user.is_authenticated:
     #   return render_template('analysis.html')         #redirect(url_for(' #home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('analysis'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='mlgssnhb@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    #if current_user.is_authenticated:
     #   return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    #if current_user.is_authenticated:
     #   return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

consumer_key ='VTJBKxgKMle3ajF6yKGlMgB3f'
consumer_secret='PPOikMrLC33ZIwLMhpHsejE2QDbawo5ONmOz2zVjQ3xRoEnlAg'

access_token='1154630220558696448-KDqGJGhimyFYk4nlPJ1xiKdOaMk6ZO'
access_token_secret='esQD1aO6SPKL7eusI4FUSJUNlam4ulEi1HIkvTQniga2O'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
size=1000

# Return API with authentication:
api = tweepy.API(auth)

@app.route('/index',methods=['GET','POST'])
def analysis():

    if request.method=="POST":
        topic=request.form['topic'] #topic request keyword
        topic=topic+'-filter:retweets'
        test_data=api.search(topic, count =size,lang="en",tweet_mode='extended')
        user_name=[]
        loc=[]
        timezone=[]
        creationdatee=[]
        polarity=[]
        image=[]
        follower_count=[]
        verified_check=[]
        following_count=[]
        retweets_count=[]
        favourite_count=[]
        tweet_id=[]
        actual_tweets=[]
        emoji_count=[] #to store the number of emojis used
        words_number=[] #to store the number of words
        # gender = [] how to get it? how to use this API https://genderapi.io/api-documentation ?
        bio=[]

        #emoji dictionary
        emoji_dict={'👿': -4.0, '🖕': -4.0, '😾': -4.0, '😡': -4.0, '😠': -3.0, '😧': -3.0, '💔': -3.0, '💩': -3.0, '😱': -3.0,
                     '🙀': -3.0, '😈': -3.0, '😭': -3.0, '😟': -3.0, '👎': -2.0, '😰': -2.0, '😖': -2.0, '😕': -2.0, '😢': -2.0, '😿': -2.0,
                     '😞': -2.0, '🤕': -2.0, '😨': -2.0, '😳': -2.0, '☹️': -2.0, '😬': -2.0, '🤥': -2.0, '🤢': -2.0, '😮': -2.0, '😣': -2.0,
                     '💀': -2.0, '☠️': -2.0, '🤧': -2.0, '😫': -2.0, '😒': -2.0, '😩': -2.0, '😥': -1.0, '😵': -1.0, '🤒': -1.0, '👊': -1.0, '😦': -1.0,
                     '👻': -1.0, '😯': -1.0, '😷': -1.0, '🤓': -1.0, '😔': -1.0, '🙄': -1.0, '🙁': -1.0, '😜': -1.0, '😓': -1.0, '🤔': -1.0, '🤐': -1.0,
                     '🤡': 0.0, '🤤': 0.0, '😑': 0.0, '🤑': 0.0, '😐': 0.0, '😶': 0.0, '😴': 0.0, '😪': 0.0, '😝': 0.0, '😤': 0.0, '🙃': 0.0,
                     '🤝': 1.0, '😆': 1.0, '🙏': 1.0, '🙂': 1.0, '😛': 1.0, '😎': 1.0, '👍': 2.0, '😲': 2.0, '😊': 2.0, '🤠': 2.0, '🤞': 2.0,
                     '😁': 2.0, '😀': 2.0, '🤗': 2.0, '💋': 2.0, '😗': 2.0, '😽': 2.0, '😚': 2.0, '😙': 2.0, '👄': 2.0, '👌': 2.0, '☺️': 2.0,

                     '😌': 2.0, '😄': 2.0, '😸': 2.0, '😃': 2.0, '😺': 2.0, '😏': 2.0, '😼': 2.0, '😅': 2.0, '✌️': 2.0, '💯': 3.0, '🖤': 3.0,
                     '💙': 3.0, '👏': 3.0, '💘': 3.0, '💝': 3.0, '💚': 3.0, '❤️': 3.0, '😍': 3.0, '😻': 3.0, '💓': 3.0, '💗': 3.0, '😇': 3.0,
                     '😂': 3.0, '😹': 3.0, '😘': 3.0, '💜': 3.0, '💞': 3.0, '💖': 3.0, '💕': 3.0, '😉': 3.0, '💛': 3.0, '😋': 3.0, '🙌': 4.0, '🤣': 4.0,
                     '☠️': -2.0,
                 '☹️': -2.0,'☺️': 2.0, '✌️': 2.0, '❤️': 3.0,'👄': 2.0,'👊': -1.0,'👌': 2.0,'👍': 2.0, '👎': -2.0, '👏': 3.0,'👻': -1.0,'👿': -4.0,'💀': -2.0,'💋': 2.0,
                 '💓': 3.0, '💔': -3.0, '💕': 3.0,'💖': 3.0,'💗': 3.0, '💘': 3.0,'💙': 3.0, '💚': 3.0,
                 '💛': 3.0,
                 '💜': 3.0,
                 '💝': 3.0,
                 '💞': 3.0,
                 '💩': -3.0,
                 '💯': 3.0,
                 '🖕': -4.0,
                 '🖤': 3.0,
                 '😀': 2.0,
                 '😁': 2.0,
                 '😂': 3.0,
                 '😃': 2.0,
                 '😄': 2.0,
                 '😅': 2.0,
                 '😆': 1.0,
                 '😇': 3.0,
                 '😈': -3.0,
                 '😉': 3.0,
                 '😊': 2.0,
                 '😋': 3.0,
                 '😌': 2.0,
                 '😍': 3.0,
                 '😎': 1.0,
                 '😏': 2.0,
                 '😐': 0.0,
                 '😑': 0.0,
                 '😒': -2.0,
                 '😓': -1.0,
                 '😔': -1.0,
                 '😕': -2.0,
                 '😖': -2.0,
                 '😗': 2.0,
                 '😘': 3.0,
                 '😙': 2.0,
                 '😚': 2.0,
                 '😛': 1.0,
                 '😜': -1.0,
                 '😝': 0.0,
                 '😞': -2.0,
                 '😟': -3.0,
                 '😠': -3.0,
                 '😡': -4.0,
                 '😢': -2.0,
                 '😣': -2.0,
                 '😤': 0.0,
                 '😥': -1.0,
                 '😦': -1.0,
                 '😧': -3.0,
                 '😨': -2.0,
                 '😩': -2.0,
                 '😪': 0.0,
                 '😫': -2.0,
                 '😬': -2.0,
                 '😭': -3.0,
                 '😮': -2.0,
                 '😯': -1.0,
                 '😰': -2.0,
                 '😱': -3.0,
                 '😲': 2.0,
                 '😳': -2.0,
                 '😴': 0.0,
                 '😵': -1.0,
                 '😶': 0.0,
                 '😷': -1.0,
                 '😸': 2.0,
                 '😹': 3.0,
                 '😺': 2.0,
                 '😻': 3.0,
                 '😼': 2.0,
                 '😽': 2.0,
                 '😾': -4.0,
                 '😿': -2.0,
                 '🙀': -3.0,
                 '🙁': -1.0,
                 '🙂': 1.0,
                 '🙃': 0.0,
                 '🙄': -1.0,
                 '🙌': 4.0,
                 '🙏': 1.0,
                 '🤐': -1.0,
                 '🤑': 0.0,
                 '🤒': -1.0,
                 '🤓': -1.0,
                 '🤔': -1.0,
                 '🤕': -2.0,
                 '🤗': 2.0,
                 '🤝': 1.0,
                 '🤞': 2.0,
                 '🤠': 2.0,
                 '🤡': 0.0,
                 '🤢': -2.0,
                 '🤣': 4.0,
                 '🤤': 0.0,
                 '🤥': -2.0,
                 '🤧': -2.0}

        def truncate(f, n):
            '''Truncates/pads a float f to n decimal places without rounding'''
            s = '{}'.format(f)
            if 'e' in s or 'E' in s:
                return '{0:.{1}f}'.format(f, n)
            i, p, d = s.partition('.')
            return '.'.join([i, (d + '0' * n)[:n]])

        def extract_emojis(s):
            # a: str = ''.join(c for c in s if c in emoji.UNICODE_EMOJI)
            a: str = ''.join(c for c in s if c in emoji_dict.keys())
            if (a == ''):
                return None
            else:
                return a

        for tweet in test_data:
            user_name.append(tweet.user.screen_name)
            loc.append(tweet.user.location)
            timezone.append(tweet.user.time_zone)
            creationdatee.append(tweet.created_at)
            polarity.append(truncate((TextBlob(tweet.full_text).sentiment.polarity), 3))
            image.append(tweet.user.profile_image_url_https)
            follower_count.append(tweet.user.followers_count)
            verified_check.append(tweet.user.verified)
            following_count.append(tweet.user.friends_count)
            retweets_count.append(tweet.retweet_count)
            favourite_count.append(tweet.favorite_count)
            tweet_id.append(tweet.id)
            actual_tweets.append(tweet.full_text)
            bio.append(tweet.user.description)

            # himu
        emojis = []
        for t in test_data:
            emojis.append(extract_emojis(t.full_text))

        for i in emojis:
            if (i == None):
                emoji_count.append(0)
            else:
                emoji_count.append(len(i))

        def word_count(text):
            text = str(text)
            word_list = []
            data = text.split(" ")
            return (len(data))

        for i in test_data:
            words_number.append(word_count(i.full_text))

        def val(emoj):
            if (emoj == None):
                return 0
            for i in emoj:
                sum = 0
                if (i in emoji_dict.keys()):
                    sum = sum + emoji_dict[i]
            return sum

        def calculate_emoji_strength(emoj):
            if emoj == None:
                return 0
            else:
                for i in emoj:
                    if (len(i) == 0):
                        return 0
                    elif (len(i) == 1):
                        return emoji_dict[emoj[0]]
                    else:
                        list_of_emoji_scores = []
                        for i in emoj:
                            list_of_emoji_scores.append(emoji_dict[i])

                        max_score = max(list_of_emoji_scores)
                        min_score = min(list_of_emoji_scores)
                        return max_score + min_score

        emoji_score = []

        for i in emojis:
            if (i == None):
                emoji_score.append(0)
            else:
                emoji_score.append(val(i))

        emoj_strength = []
        for i in emojis:
            emoj_strength.append(calculate_emoji_strength(i))

        creationdate = []
        for i in creationdatee:
            creationdate.append(i.strftime('%m/%d/%Y %I:%M:%S'))

        loca = []
        for i in loc:
            loca.append(re.sub("[^a-zA-Z]", "", i))

        location = []
        for l in loca:
            if not len(l) > 0:
                location.append(l.replace(l, 'India'))
            else:
                location.append(l)

        preprocessed_words = []

        def preprocessing(raw_data):
            review_text = BeautifulSoup(raw_data, "html5lib").get_text()  # removes html tags
            x = re.sub("[@]\w+", " ", review_text)  # remove usertags
            x = re.sub("[^a-zA-Z]", " ", x)
            x = re.sub("[#\(\)\[\]]", " ", x)  # remove brackets and from hashtags
            x = re.sub("https?[\w./:]+", " ", x)  # remove urls
            x = re.sub("\.{2,}", " ", x)  # replacing 2+ dots to space
            x = re.sub("(.)\1+", "\1\1", x)  # replace multiple chars to 2 chars
            x = re.sub("(-|\')", " ", x)  # removing -|\''
            words = x.lower().split()  # split into words
            meaningful_words = list(filter(lambda x: (stemmer.stem(x)), words))
            meaningful_words = [w for w in meaningful_words if not w in stops]
            for wo in meaningful_words:
                if not 2 < len(wo) < 31:
                    meaningful_words.remove(wo)

            for we in meaningful_words:
                preprocessed_words.append(we)

        clean_test_reviews = []
        # cleaning the tweet text
        for tweet in actual_tweets:
            # review_text = BeautifulSoup(tweet.text, "html5lib").get_text()
            x = re.sub("[@]\w+", " ", tweet)  # remove usertags
            x = re.sub("[^a-zA-Z]", " ", x)
            x = re.sub("[#\(\)\[\]]", " ", x)  # remove brackets and from hashtags
            x = re.sub("https?[\w./:]+", " ", x)  # remove urls
            x = re.sub("\.{2,}", " ", x)  # replacing 2+ dots to space
            x = re.sub("(.)\1+", "\1\1", x)  # replace multiple chars to 2 chars
            x = re.sub("(-|\')", " ", x)  # removing -|\''
            x = x.strip()  # to remove trailing spaces
            clean_test_reviews.append(x)

        top_words1 = []
        for tweet1 in test_data:
            preprocessing(tweet1.full_text)

        final_words_count = collections.Counter(preprocessed_words)

        for letter, count in final_words_count.most_common(30):
            top_words1.append(letter)

        top_words = top_words1[10:30]

        output = pd.DataFrame(data={"SentimentText": actual_tweets[0:size], "Cleaned_text": clean_test_reviews[0:size],
                                    "UserName": user_name[0:size], "CreationDate": creationdate[0:size],
                                    "Image": image[0:size], "Location": location[0:size],
                                    "FollowerCount": follower_count[0:size], "FollowingCount": following_count[0:size],
                                    "Verified": verified_check[0:size], "ReTweet": retweets_count[0:size],
                                    "Likes": favourite_count[0:size], "ID": tweet_id[0:size], "emoji_": emojis[0:size],
                                    "emoji_count": emoji_count[0:size], "number_of_words": words_number[0:size],
                                    "emoji_score": emoji_score[0:size], "emoji_strength": emoj_strength[0:size],
                                    "Polarity": polarity[0:size], "bio": bio[0:size]})

        X = output.loc[:,['Cleaned_text', 'FollowerCount', 'FollowingCount', 'emoji_count', 'number_of_words', 'emoji_score',
             'emoji_strength', 'bio']]
        tokenizer = TweetTokenizer()

        def tokenize(tweet):
            try:
                tweet = tweet.lower()
                tokens = tokenizer.tokenize(tweet)
                tokens = list(filter(lambda t: not t.startswith('@'), tokens))
                tokens = list(filter(lambda t: not t.startswith('#'), tokens))
                tokens = list(filter(lambda t: not t.startswith('http'), tokens))
                return tokens
            except:
                return 'NC'

        vocab_size = 1000

        vectorizer = CountVectorizer(stop_words='english', max_features=vocab_size, tokenizer=tokenize)
        vectorizer.fit(X.loc[:, 'Cleaned_text'])

        train_embeddings = vectorizer.transform(X.loc[:, 'Cleaned_text'])

        mean_train = X.loc[:, 'emoji_count'].mean()
        std_train = X.loc[:, 'emoji_count'].std()

        mean_train_cnt = X.loc[:, 'number_of_words'].mean()
        std_train_cnt = X.loc[:, 'number_of_words'].std()

        mean_train_f = X.loc[:, 'FollowerCount'].mean()
        std_train_f = X.loc[:, 'FollowerCount'].std()

        mean_train_f1 = X.loc[:, 'FollowingCount'].mean()
        std_train_f1 = X.loc[:, 'FollowingCount'].std()

        mean_train_p1 = X.loc[:, 'emoji_score'].mean()
        std_train_p1 = X.loc[:, 'emoji_score'].std()

        mean_train_s1 = X.loc[:, 'emoji_strength'].mean()
        std_train_s1 = X.loc[:, 'emoji_strength'].std()

        X['std_cnt_emoji'] = X['emoji_count'].map(lambda x: (x - mean_train) / std_train)
        X['std_cnt_word'] = X['number_of_words'].map(lambda x: (x - mean_train_cnt) / std_train_cnt)
        X['std_followers'] = X['FollowerCount'].map(lambda x: (x - mean_train_f) / std_train_f)
        X['std_following'] = X['FollowingCount'].map(lambda x: (x - mean_train_f1) / std_train_f1)
        X['std_emoji_pop'] = X['emoji_score'].map(lambda x: (x - mean_train_p1) / std_train_p1)
        X['std_emoji_strength'] = X['emoji_strength'].map(lambda x: (x - mean_train_s1) / std_train_s1)

        Xtrain_embedded = hstack((train_embeddings, np.array(X['std_cnt_emoji'])[:, None])).tocsr()
        Xtrain_embedded = hstack((Xtrain_embedded, np.array(X['std_cnt_word'])[:, None])).tocsr()
        Xtrain_embedded = hstack((Xtrain_embedded, np.array(X['std_followers'])[:, None])).tocsr()
        Xtrain_embedded = hstack((Xtrain_embedded, np.array(X['std_following'])[:, None])).tocsr()
        Xtrain_embedded = hstack((Xtrain_embedded, np.array(X['std_emoji_pop'])[:, None])).tocsr()
        Xtrain_embedded = hstack((Xtrain_embedded, np.array(X['std_emoji_strength'])[:, None])).tocsr()

        #model = load_model("sentiment_82.h5")
        Xtrain_embedded = Xtrain_embedded[0:100]
        Xtrain_embedded = Xtrain_embedded.todense()

        def adjust(np_array):
            for i in range(len(np_array)):
                if (np_array[i] < -0.2):
                    np_array[i] = -1
                elif (np_array[i] >= -0.2 and np_array[i] <= 0.2):
                    np_array[i] = 0
                else:
                    np_array[i] = 1
            return np_array

        # y = adjust(y_pred)
        # output["Polarity"]= y

        # polarity =y

        output.to_csv("Entire_Output.csv", index=False)
        with open("Entire_Output.csv", newline='') as csvfile:
            spamreader = csv.DictReader(csvfile)
            sortedlist = sorted(spamreader, key=lambda row: (row['Polarity']), reverse=True)

        with open('Sorted_Entire_Output.csv', 'w') as f:
            fieldnames = ['SentimentText', 'Cleaned_text', 'UserName', 'CreationDate', 'Image', 'Location',
                          'FollowerCount', 'FollowingCount', 'Verified', 'ReTweet', 'Likes', 'ID', 'emoji_',
                          'emoji_count', 'number_of_words', 'emoji_score', 'emoji_strength', 'Polarity', 'bio']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in sortedlist:
                writer.writerow(row)

        with open("Sorted_Entire_Output.csv", newline='') as f0:
            reader = csv.DictReader(f0)
            rows0 = [row for row in reader if float(row['Polarity']) > 0]

        with open('Positive_Output.csv', 'w') as f:
            fieldnames = ['SentimentText', 'Cleaned_text', 'UserName', 'CreationDate', 'Image', 'Location',
                          'FollowerCount', 'FollowingCount', 'Verified', 'ReTweet', 'Likes', 'ID', 'emoji_',
                          'emoji_count', 'number_of_words', 'emoji_score', 'emoji_strength', 'Polarity', 'bio']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows0:
                writer.writerow(row)

        with open("Sorted_Entire_Output.csv", newline='') as f0:
            reader = csv.DictReader(f0)
            rows1 = [row for row in reader if float(row['Polarity']) < 0]

        with open('Negative_Output.csv', 'w') as f:
            fieldnames = ['SentimentText', 'Cleaned_text', 'UserName', 'CreationDate', 'Image', 'Location',
                          'FollowerCount', 'FollowingCount', 'Verified', 'ReTweet', 'Likes', 'ID', 'emoji_',
                          'emoji_count', 'number_of_words', 'emoji_score', 'emoji_strength', 'Polarity', 'bio']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows1:
                writer.writerow(row)

        with open("Sorted_Entire_Output.csv", newline='') as f0:
            reader = csv.DictReader(f0)
            rows2 = [row for row in reader if float(row['Polarity']) == 0.0]

        with open('Neutral_Output.csv', 'w') as f:
            fieldnames = ['SentimentText', 'Cleaned_text', 'UserName', 'CreationDate', 'Image', 'Location',
                          'FollowerCount', 'FollowingCount', 'Verified', 'ReTweet', 'Likes', 'ID', 'emoji_',
                          'emoji_count', 'number_of_words', 'emoji_score', 'emoji_strength', 'Polarity', 'bio']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows2:
                writer.writerow(row)

        df0 = pd.read_csv("Positive_Output.csv")
        sentiment_text0 = df0['SentimentText']
        user_name0 = df0['UserName']
        polarity0 = df0['Polarity']
        creationdate0 = df0['CreationDate']
        image0 = df0['Image']
        follower_count0 = df0["FollowerCount"]
        following_count0 = df0["FollowingCount"]
        verified0 = df0['Verified']
        retweets_count0 = df0['ReTweet']
        favourite_count0 = df0['Likes']
        tweet_id0 = df0['ID']
        bio0 = df0['bio']
        row0, column0 = df0.shape

        df1 = pd.read_csv("Negative_Output.csv")
        sentiment_text1 = df1['SentimentText']
        user_name1 = df1['UserName']
        polarity1 = df1['Polarity']
        creationdate1 = df1['CreationDate']
        image1 = df1['Image']
        follower_count1 = df1["FollowerCount"]
        following_count1 = df1["FollowingCount"]
        verified1 = df1['Verified']
        retweets_count1 = df1['ReTweet']
        favourite_count1 = df1['Likes']
        tweet_id1 = df1['ID']
        bio1 = df1['bio']
        row1, column1 = df1.shape

        df2 = pd.read_csv("Neutral_Output.csv")
        sentiment_text2 = df2['SentimentText']
        user_name2 = df2['UserName']
        polarity2 = df2['Polarity']
        creationdate2 = df2['CreationDate']
        image2 = df2['Image']
        follower_count2 = df2["FollowerCount"]
        following_count2 = df2["FollowingCount"]
        verified2 = df2['Verified']
        retweets_count2 = df2['ReTweet']
        favourite_count2 = df2['Likes']
        tweet_id2 = df2['ID']
        bio2 = df2['bio']
        row2, column2 = df2.shape

        # with open("Sorted_Entire_Output.csv", 'r') as data:
        #  counter = Counter()
        # for row in csv.DictReader(data):
        #   counter[row['Sentiment']] += 1

        positive = row0
        negative = row1
        neutral = row2

        labels = ["Positive", "Negative", "Neutral"]
        values = [positive, negative, neutral]
        colors = ["#70db70", " #ff6666", "#4dffff"]

        return render_template('analysis.html', topic=topic, set=zip(values, labels, colors), values=values, colors=colors,
                               labels=labels, sentiment_text1=sentiment_text1, sentiment_text0=sentiment_text0,
                               sentiment_text2=sentiment_text2,
                               user_name1=user_name1, user_name0=user_name0, user_name2=user_name2, polarity1=polarity1,
                               polarity0=polarity0, polarity2=polarity2, creationdate1=creationdate1,
                               creationdate0=creationdate0,creationdate2=creationdate2, image0=image0, image1=image1, image2=image2,
                               pol="Polarity : ", follower_count0=follower_count0, follower_count1=follower_count1,
                               follower_count2=follower_count2,
                               following_count0=following_count0, following_count1=following_count1,
                               following_count2=following_count2, verified0=verified0, verified1=verified1,
                               verified2=verified2, followers="Followers : ", following="Following : ",
                               retweets_count0=retweets_count0, retweets_count1=retweets_count1,
                               retweets_count2=retweets_count2, favourite_count0=favourite_count0,
                               favourite_count1=favourite_count1, favourite_count2=favourite_count2,
                               tweet_id0=tweet_id0, tweet_id1=tweet_id1, tweet_id2=tweet_id2, top_words=top_words,
                               bio0=bio0, bio1=bio1, bio2=bio2, output=output)

    return render_template('analysis.html')