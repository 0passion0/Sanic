from aiohttp import web
from sanic import Sanic, response
from zsq import Lem
from motor.motor_asyncio import AsyncIOMotorClient

# 创建Sanic应用
app = Sanic(__name__)
la = Lem()


class BookDB:
    def __init__(self, collection):
        self.collection = collection

    async def get_random_books(self, size):
        datas = await self.collection.aggregate([{"$sample": {"size": size}}]).to_list(size)
        return datas

    async def find_book_by_id(self, book_id):
        try:
            book_id = float(book_id)
        except ValueError:
            return None
        return await self.collection.find_one({'id': book_id})

    async def create_book(self, book_data):
        try:
            book_data['id'] = float(book_data['id'])
        except (ValueError, KeyError):
            return None
        result = await self.collection.insert_one(book_data)
        return result.inserted_id

    async def delete_book_by_id(self, book_id):
        try:
            book_id = float(book_id)
        except ValueError:
            return False
        result = await self.collection.delete_one({'id': book_id})
        return result.deleted_count > 0


def db_setup():
    # 建立数据库连接
    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")
    db = client['tlg']
    collection = db['book']
    return BookDB(collection)


# 在启动过程中将数据库实例存储在app.ctx属性中
@app.listener('before_server_start')
async def setup_db(app, loop):
    # 设置数据库实例到Sanic应用的上下文中
    app.ctx.db = db_setup()


# 统一的返回结构
def create_response(success, message, result=None):
    # 创建统一的响应结构，包含成功状态、消息和结果数据
    return {"success": success, "message": message, "result": result}


# 定义一个简单的路由处理函数
@app.route('/', methods=['GET'])
@la.template("books.html")
async def get_books(request):
    # 获取随机的书籍数据
    datas = await app.ctx.db.get_random_books(10)
    print(datas)
    return create_response(True, "成功获取图书数据", datas)


@app.route('/book/<id>', methods=['GET'])
@la.template("findbooks.html")
async def get_book(request, id):
    # 根据图书ID获取图书信息
    book_data = await app.ctx.db.find_book_by_id(id)
    if book_data:
        return create_response(True, "成功找到图书", book_data)
    else:
        return create_response(False, "未找到图书")


# 定义一个简单的路由处理函数，用于返回createbooks.html页面
@app.route('/book/create', methods=['GET'])
@la.template("createbooks.html")
async def get_create_book(request):
    return create_response(True, "准备创建图书", {})


# 定义另一个处理函数来处理POST请求
@app.route('/book/create', methods=['POST'])
async def create_book(request):
    # 获取POST请求中的JSON数据，假设传递的数据是包含书籍信息的JSON对象
    book_data = request.json
    if not book_data:
        return create_response(False, "请求数据为空")

    # 创建图书并插入数据库
    book_id = await app.ctx.db.create_book(book_data)
    if book_id:
        return create_response(True, "成功创建图书", {"id": book_id})
    else:
        return create_response(False, "无效的图书数据")


@app.route('/book/delete/<id>', methods=['GET'])
async def delete_book(request, id):
    # 根据图书ID删除图书
    result = await app.ctx.db.delete_book_by_id(id)
    if result:
        return create_response(True, "成功删除图书")
    else:
        return create_response(False, "未找到图书或无效的图书ID")


if __name__ == '__main__':
    app.run(port=8000)
