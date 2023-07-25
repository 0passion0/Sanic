from sanic import Sanic, response
from pymongo import MongoClient

app = Sanic(__name__)

# MongoDB setup
client = MongoClient('localhost', 27017)
database = client['tlg']
BookRepo = database['book_collection_name']

# Model for Book
class Book:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description

# 1. GET /books
@app.route('/', methods=['GET'])
async def get_books(request):
    books = []
    for book_data in BookRepo.find():
        book = Book(book_data['id'], book_data['title'], book_data['description'])
        books.append(book.__dict__)
    return response.json(books)

# 2. GET /book/id
@app.route('/book/<id>', methods=['GET'])
async def get_book(request, id):
    book_data = BookRepo.find_one({'id': id})
    if book_data:
        book = Book(book_data['id'], book_data['title'], book_data['description'])
        return response.json(book.__dict__)
    else:
        return response.json({'error': 'Book not found'}, status=404)

# 3. POST /book/create
@app.route('/book/create', methods=['POST'])
async def create_book(request):
    data = request.json
    book = Book(data['id'], data['title'], data['description'])
    BookRepo.insert_one(book.__dict__)
    return response.json({'message': 'Book created successfully'}, status=201)

# 4. PUT /book/update
@app.route('/book/update', methods=['PUT'])
async def update_book(request):
    data = request.json
    book = Book(data['id'], data['title'], data['description'])
    BookRepo.update_one({'id': data['id']}, {'$set': book.__dict__})
    return response.json({'message': 'Book updated successfully'})

# 5. DELETE /book/id
@app.route('/book/<id>', methods=['DELETE'])
async def delete_book(request, id):
    BookRepo.delete_one({'id': id})
    return response.json({'message': 'Book deleted successfully'})

if __name__ == '__main__':
    app.run(port=8000)
