from flask import Flask, render_template,request
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
#load the dataset
df=pd.read_csv('movie_metadata.csv')
df.drop_duplicates(subset="movie_title",keep=False,inplace=True)
df['ID']=np.arange(len(df))
important_features=['ID','movie_title','director_name','genres','actor_1_name','actor_2_name','actor_3_name']
df=df[important_features]
#preprocesing  of data
for x in important_features:
    df[x]=df[x].fillna(' ')    
df['movie_title']=df['movie_title'].apply(lambda x:x.replace(u'\xa0',u''))
df['movie_title']=df['movie_title'].apply(lambda x:x.strip())
#function that combine director_name,genres,actor and return them as string
def combine(row):
        return row['director_name']+" "+row["genres"]+" "+row['actor_1_name']+" "+row['actor_2_name']+" "+row['actor_3_name']
df["combined"]=df.apply(combine,axis=1)
#Convert a collection of text documents to a matrix of token counts
cv=CountVectorizer()
count=cv.fit_transform(df["combined"])
#finding the  similarity
cosine_simi=cosine_similarity(count)
def get_tittle(Id):
    return df[df.ID==Id]["movie_title"].values[0]
def cont_recommend(user_liking,n):
    movie_index=get_id(user_liking)
    similar_movies=list(enumerate(cosine_simi[movie_index]))
    sorted_similar_movies=sorted(similar_movies,key=lambda x:x[1],reverse=True)
    sorted_similar_movies
    i=0
    j=0
    l=[1]*n
    for movie in sorted_similar_movies:    
        x=get_tittle(movie[0])
        if i==0:
            i=i+1
        else:    
            l[j]=x
            j=j+1
            i=i+1
        if i>n:
            break
    return l
# retuns id    
def get_id(tittle):
    if tittle in df.movie_title.unique():
        return  df[df.movie_title==tittle]['ID'].values[0]
    else:
        return -1         
df1=pd.read_csv('movies.csv')
df2=pd.read_csv('ratings.csv')
df1['title']=df1['title'].apply(lambda x:x.replace(x,x[:-6]))
df1['title']=df1['title'].apply(lambda x:x.strip())
df3=pd.merge(df1,df2,on='movieId')
important=['userId','movieId','title','rating']
df4=df3.pivot_table(index=['userId'],columns=['title'],values='rating').fillna(0)
df4=df4.T
model_knn=NearestNeighbors(metric='cosine',algorithm='auto')
n=model_knn.fit(df4)
#returns a list of recommended movies  but  if a movie is not present returns a message   
def collab_recommend(user_liking,nn):
    index=df4.index.get_loc(user_liking) 
    k=df4.iloc[index].values
    k=k.reshape(1,-1)
    distances,indices=n.kneighbors(k,n_neighbors=nn+1)
    l=[None]*nn
    for i in range(1,nn+1):
        l[i-1]=df4.index[indices.flatten()[i]]
    return l


app = Flask(__name__)

@app.route('/')
#home page
def home():
   return render_template('home.html')

@app.route('/predict',methods=['POST','GET'])
#output page
def predict():
    if request.method=='GET':
        user_liking=request.args.get('movie')
    else:
        user_liking=request.form['movie']
    l1=list(df['movie_title'])
    l2=list(df1['title'])
    if user_liking in l1 and user_liking in l2:
        c1=cont_recommend(user_liking,5)
        c2=collab_recommend(user_liking,5)
        output=c1+c2
        output=set(output)
        output=list(output)
    elif user_liking in l1:
        output=cont_recommend(user_liking,10)
    elif user_liking in l2:
        output=collab_recommend(user_liking,10)    
    return render_template('after.html',output=output)
if __name__ == '__main__':
   app.run(debug=True)