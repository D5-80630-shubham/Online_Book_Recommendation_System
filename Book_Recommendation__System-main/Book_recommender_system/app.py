import json
import os
import urllib

from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd

popular_df_original = pd.read_pickle(open('popular.pkl','rb'))
popular_df=popular_df_original.sample(frac=1)
pt = pd.read_pickle(open('pt.pkl','rb'))
books = pd.read_pickle(open('books.pkl','rb'))
similarity_score = pd.read_pickle(open('similarity_score.pkl','rb'))
isbn_ref=pd.read_pickle(open('isbn_ref.pkl','rb'))
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author_name = list(popular_df['Book-Author'].values),
                           image = list(popular_df['Image-URL-M'].values),
                           votes = list(popular_df['num_ratings'].values),
                           ratings = list(popular_df['avg_ratings'].values),
                           isbn=list(popular_df['ISBN'].values)
                           )

@app.route('/details/',methods=['get'])
def details():
    isbn=request.args.get('isbn')
    name=request.args.get('name')
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key=AIzaSyBsuq-TMHIihs7E91X4bl1Ili4vBMm5BZM"
    response = urllib.request.urlopen(url)
    data = response.read()
    json_data = json.loads(data)
    data=[]
    index_check = np.where(pt.index == name)
    if (index_check[0]):
        print((index_check))
        index=index_check[0][0]
        similar_items = sorted(list(enumerate(similarity_score[index])),
                               key=lambda x: x[1], reverse=True)[1:5]
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(
                list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(
                list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(
                list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

            data.append(item)
    print(data)
    # return render_template('recommend.html', data=data)
    return render_template("details.html", details=json_data,data=data)

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    from flask import request
    user_input = request.form.get('user_input')
    index_check = np.where(pt.index == user_input)
    data=[]
    if index_check[0]:
        print(index_check)
        index=index_check[0][0]
        similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:5]
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            data.append(item)
    else:
        for idx, row in popular_df.head().iterrows():
            item=[]
            item.append(row['Book-Title'])
            item.append(row['Book-Author'])
            item.append(row['Image-URL-M'])
            data.append(item)
    print(data)
    return render_template('recommend.html',data=data)
if __name__ =='__main__':
    app.run(debug=True)