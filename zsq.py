# 导入Sanic类
from sanic import Sanic
from functools import wraps
from sanic.response import html
from jinja2 import Environment, FileSystemLoader  # 使用FileSystemLoader替换PackageLoader
from motor import motor_asyncio
import asyncio
# 创建Sanic应用
app = Sanic(__name__)

# 定义Jinja2模板加载器
env = Environment(loader=FileSystemLoader("templates"), enable_async=True)  # templates为存放模板文件的目录

class Lem:
    @staticmethod
    def template(template_name):
        def wrapper(func):
            @wraps(func)
            async def inner(request, *args, **kwargs):
                template = env.get_template(template_name)
                content = await func(request, *args, **kwargs)  # 注意视图函数是异步的需要await
                return html(await template.render_async(content))
            return inner
        return wrapper

async def find():
    client =motor_asyncio.AsyncIOMotorClient("mongodb://127.0.0.1:27017")
    db=client['tlg']
    collection=db['book']
    ret=await collection.find_one({})
    print(ret)
    # cursor = collection.find({})  # 查询所有文档
    # async for document in cursor:
    #     print(document)
# if __name__ == '__main__':
#     asyncio.run(find())