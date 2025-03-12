from flask import Flask, render_template, request
import pickle
import numpy as np

# Load the pickled data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    # Get user input from the form
    user_input = request.form.get('user-input')
    
    try:
        # Fetch the index of the book from the pivot table (pt)
        index = np.where(pt.index == user_input)[0][0]
    except IndexError:
        print("Book name not found in pivot table.")
        return render_template('recommend.html', error="Book not found in our database.")

    # Find the most similar books, excluding the first one (the book itself)
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

    # Prepare the data for the recommended books
    data = []
    for i in similar_items:
        items = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        
        # Ensure unique values for book title, author, and image URL
        items.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        items.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        items.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(items)
    
    print(data)  # Printing the data for debugging

    # Pass the recommended books data to the template
    return render_template('recommend.html', recommended_books=data)

if __name__ == '__main__':
    app.run(debug=True)
