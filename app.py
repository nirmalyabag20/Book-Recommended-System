from flask import Flask,render_template,request
import pickle
import numpy as np
import pandas as pd

popular_books = pickle.load(open('popular_books.pkl','rb'))
pivot_table = pickle.load(open('pivot_table.pkl','rb'))
books_df = pickle.load(open('books_df.pkl','rb'))
similarity_score = pickle.load(open('similarity_score.pkl','rb'))
books_ratings = pickle.load(open('books_ratings.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_books['Book-Title'].values),
                           author=list(popular_books['Book-Author'].values),
                           image=list(popular_books['Image-URL-M'].values),
                           votes=list(popular_books['num_ratings'].values),
                           rating=list(popular_books['avg_ratings'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pivot_table.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books_ratings[books_ratings['Book-Title'] == pivot_table.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Publisher'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Year-Of-Publication'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html',data=data)


@app.route('/book/<title>')
def book_details(title):
    # Find the details of the selected book
    book_info = books_ratings[books_ratings['Book-Title'] == title].drop_duplicates('Book-Title')

    # Extract book details
    book_details = {
        'title': book_info['Book-Title'].values[0],
        'author': book_info['Book-Author'].values[0],
        'image': book_info['Image-URL-M'].values[0],
        'Publisher': book_info['Publisher'].values[0],
        'Year': book_info['Year-Of-Publication'].values[0],
        'Book_Rating': book_info['Book-Rating'].values[0],
        'num_ratings': book_info['num_ratings'].values[0],
        'avg_ratings': book_info['avg_ratings'].values[0]

        # Add other details as needed
    }

    # Get similar books
    index = np.where(pivot_table.index == title)[0][0]
    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:5]

    # Prepare similar books data
    similar_books = []
    for i in similar_items:
        temp_df = books_ratings[books_ratings['Book-Title'] == pivot_table.index[i[0]]].drop_duplicates('Book-Title')
        similar_books.append({
            'title': temp_df['Book-Title'].values[0],
            'author': temp_df['Book-Author'].values[0],
            'image': temp_df['Image-URL-M'].values[0],
            'Publisher': temp_df['Publisher'].values[0],
            'Year': temp_df['Year-Of-Publication'].values[0],
            'Book_Rating': temp_df['Book-Rating'].values[0],
            'Num_Ratings': temp_df['num_ratings'].values[0],
            'Avg_Ratings': temp_df['avg_ratings'].values[0]

        })
    print(similar_books)

    return render_template('book_details.html', book=book_details, similar_books=similar_books)


if __name__ == '__main__':
    app.run(debug=True)