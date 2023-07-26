# 导入必要的库
from sanic import Sanic, response
from pymongo import MongoClient

# 创建 Sanic 应用实例
app = Sanic(__name__)

client = MongoClient('localhost', 27017)
# 访问 'tlg' 数据库（如果不存在，将会被创建）
database = client['tlg']
# 访问 'book_collection_name' 集合（如果不存在，将会被创建）
BookRepo = database['book_collection_name']

# Book 模型
class Book:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description

# 1. GET /books
# 获取所有图书信息的路由
@app.route('/books', methods=['GET'])
async def get_books(request):
    books = []
    # 遍历数据库中的所有图书数据
    for book_data in BookRepo.find():
        # 创建 Book 实例并将其添加到 books 列表中
        book = Book(book_data['id'], book_data['title'], book_data['description'])
        books.append(book.__dict__)
    # 返回 JSON 格式的图书信息列表
    return response.json(books)

# 2. GET /book/id
# 获取指定图书信息的路由
@app.route('/book/<id>', methods=['GET'])
async def get_book(request, id):
    # 在数据库中查找具有给定 id 的图书数据
    book_data = BookRepo.find_one({'id': id})
    # 如果找到了图书数据
    if book_data:
        # 创建 Book 实例并返回 JSON 格式的图书信息
        book = Book(book_data['id'], book_data['title'], book_data['description'])
        return response.json(book.__dict__)
    else:
        # 如果未找到图书，则返回 JSON 格式的错误消息和状态码 404
        return response.json({'error': '未找到图书'}, status=404)

# 3. POST /book/create
# 创建图书的路由
@app.route('/book/create', methods=['POST'])
async def create_book(request):
    # 获取客户端发送的 JSON 数据
    data = request.json
    # 创建 Book 实例
    book = Book(data['id'], data['title'], data['description'])
    # 将图书数据插入到数据库中
    BookRepo.insert_one(book.__dict__)
    # 返回 JSON 格式的成功消息和状态码 201
    return response.json({'message': '图书创建成功'}, status=201)

# 4. PUT /book/update
# 更新图书信息的路由
@app.route('/book/update', methods=['PUT'])
async def update_book(request):
    # 获取客户端发送的 JSON 数据
    data = request.json
    # 创建 Book 实例
    book = Book(data['id'], data['title'], data['description'])
    # 在数据库中更新具有给定 id 的图书数据
    BookRepo.update_one({'id': data['id']}, {'$set': book.__dict__})
    # 返回 JSON 格式的成功消息
    return response.json({'message': '图书更新成功'})

# 5. DELETE /book/id
# 删除指定图书的路由
@app.route('/book/<id>', methods=['DELETE'])
async def delete_book(request, id):
    # 在数据库中删除具有给定 id 的图书数据
    BookRepo.delete_one({'id': id})
    # 返回 JSON 格式的成功消息
    return response.json({'message': '图书删除成功'})

if __name__ == '__main__':
    # 启动应用，监听端口 8000
    app.run(port=8000)
