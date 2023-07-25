from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from 用户.main import app
from 用户.异常 import *



class DatabaseManager:
    def __init__(self, app, db_uri):
        self.app = app
        self.db_uri = db_uri
        self.client = None
        self.db = None
        self.user_collection = None
        self.permissions_collection = None
        self.departments_collection = None

    async def user_get(self, user_name):
        user = await app.ctx.user.find_one({"用户名": user_name})
        print(user)
        if user:

            a = await app.ctx.departments.find_one({"部门编号": user['部门编号']})
            data = {
                '工号': user['工号'],
                '姓名': user['姓名'],
                '职位': user['职位'],
                '部门': a['部门名']
            }
            print(data)
            return data
        else:
            return None

    async def user_create(self, json_data):
        nulldata(json_data)
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        json_data['入职时间'] = datetime.strptime(json_data['入职时间'], date_format)
        intodata(await app.ctx.departments.find_one({"部门编号": json_data['部门编号']}))
        await app.ctx.user.insert_one(json_data)
        return json_data

    async def user_delet(self, user_name):
        nulldata(user_name)
        result = await app.ctx.user.delete_one({"用户名": user_name})
        return result

    async def create_unique_index(self, collection: AsyncIOMotorCollection, field: str):
        await collection.create_index([(field, 1)], unique=True)

    async def db_setup(self):
        try:
            self.client = AsyncIOMotorClient(self.db_uri)
            self.db = self.client['tlg']
            self.user_collection = self.db['users']
            self.permissions_collection = self.db['permissions']
            self.departments_collection = self.db['departments']

            # await self.user_collection.drop()
            # await self.permissions_collection.drop()
            # await self.departments_collection.drop()

            await self.create_unique_index(self.user_collection, '用户名')
            await self.create_unique_index(self.permissions_collection, '权限名')
            await self.create_unique_index(self.departments_collection, '部门编号')

            return self.user_collection, self.permissions_collection, self.departments_collection
        except Exception as e:
            print(f"数据库连接错误；错误信息: {e}")
            return str(e)

    async def setup_db(self):
        return await self.db_setup()
