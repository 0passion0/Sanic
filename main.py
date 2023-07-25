from aiohttp import web
from sanic import Sanic, response
from zsq import Lem
from motor import motor_asyncio

# 创建Sanic应用
app = Sanic(__name__)
la = Lem()


def db_setup():
    client = motor_asyncio.AsyncIOMotorClient("mongodb://127.0.0.1:27017")
    db = client['tlg']
    collection = db['book']
    return collection


# 在启动过程中将数据库实例存储在app.ctx属性中
@app.listener('before_server_start')
async def setup_db(app):
    app.ctx.db = db_setup()


async def setup_get(size):
    datas = await app.ctx.db.aggregate([{"$sample": {"size": size}}]).to_list(size)
    return datas


# 定义一个简单的路由处理函数
@app.route('/', methods=['GET'])
@la.template("books.html")
async def get_books(request):
    # temp = env.get_template("books.html")
    datas = await setup_get(10)
    # tlg = 444
    # return html(await temp.render_async({"tlg": datas}))
    return {"datas": datas}


@app.route('/book/<id>', methods=['GET'])
@la.template("findbooks.html")
async def get_book(request, id):
    try:
        id = float(id)  # 将id参数转换为浮点数
    except ValueError:
        return {'error': '无效的图书ID'}
    book_data = await app.ctx.db.find_one({'id': id})
    print(book_data)
    if book_data:
        return {"datas": book_data}
    else:
        return {'error': '未找到图书'}

# 定义一个简单的路由处理函数，用于返回createbooks.html页面
@app.route('/book/create', methods=['GET'])
@la.template("createbooks.html")
async def get_create_book(request):
    return {"datas": {}}

# 定义另一个处理函数来处理POST请求
@app.route('/book/create', methods=['POST'])
async def create_book(request):
    book_data = request.json  # 获取POST请求中的JSON数据，假设传递的数据是包含书籍信息的JSON对象
    print(book_data)
    if not book_data:
        return {'error': '请求数据为空'}
    try:
        # 将传递的id参数转换为浮点数
        book_data['id'] = float(book_data['id'])
    except (ValueError, KeyError):
        return {'error': '无效的图书ID'}

    # 在数据库中插入书籍数据
    result = await app.ctx.db.insert_one(book_data)
    if result.inserted_id:
        return response.redirect('/')
    else:
        return {'error': '书籍添加失败'}

@app.route('/book/delete/<id>', methods=['GET'])
async def delete_book(request, id):
    try:
        id = float(id)  # 将id参数转换为浮点数
    except ValueError:
        return {'error': '无效的图书ID'}
    result = await app.ctx.db.delete_one({'id': id})
    if result.deleted_count > 0:
        return {'message': '图书删除成功'}
    else:
        return {'error': '未找到图书'}
if __name__ == '__main__':
    app.run(port=8000)
