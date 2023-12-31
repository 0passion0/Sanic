from datetime import datetime
from sanic import Sanic
from zsq import Lem
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from 用户.异常 import *

app = Sanic(__name__)
la = Lem()


class DatabaseManager:
    def __init__(self, app: app, db_uri: str):
        self.app = app
        self.db_uri = db_uri
        self.client = None
        self.db = None
        self.user_collection = None
        self.permissions_collection = None
        self.departments_collection = None
    # 用户
    async def user_get(self, user_name):
        user = await app.ctx.user.find_one({"用户名": user_name})
        if user:

            a = await app.ctx.departments.find_one({"部门编号": user['部门编号']})
            data = {
                '工号': user['工号'],
                '姓名': user['姓名'],
                '职位': user['职位'],
                '部门': a['部门名']
            }
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
    # 权限
    async def permissions_create(self, json_permissions):
        nulldata(json_permissions)
        await app.ctx.permissions.insert_one(json_permissions)
        return json_permissions

    async def permissions_change(self,json_permissions):
        nulldata(json_permissions)
        n = await app.ctx.permissions.update_one({"权限名": json_permissions['权限名']},
                                                 {"$set": {"权限": json_permissions['权限']}})
        if n.modified_count == 1:
            return create_response(200, "权限更新成功")
        else:
            return create_response(500, "权限更新失败")

    async def permissions_delet(self, permission_name):
        nulldata(permission_name)
        result = await app.ctx.user.delete_one({"权限名": permission_name})
        if result.deleted_count > 0:
            return create_response(200, "权限删除成功")
        else:
            return create_response(404, "权限不存在")
    # 部门
    async def departments_create(self, json_departments):
        nulldata(json_departments)
        if json_departments['父节点']:
            result = await app.ctx.departments.find_one({"部门编号": json_departments['父节点']})
            divdata(result)
        else:
            await app.ctx.departments.insert_one(json_departments)
            return create_response(200, "部门创建成功", {})

    async def departments_change(self,json_departments):
        nulldata(json_departments)
        if json_departments['父节点']:
            result = await app.ctx.departments.find_one({"部门编号": json_departments['父节点']})
            divdata(result)
        id = json_departments["部门编号"]
        del json_departments["部门编号"]

        n = await app.ctx.departments.update_one({"部门编号": id}, {"$set": json_departments})
        if n.modified_count:
            return create_response(200, "部门更新成功")
        else:
            return create_response(500, "部门更新失败")



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


db_manager = DatabaseManager(app, "mongodb://127.0.0.1:27017")


@app.listener('before_server_start')
async def setup_db(app, loop):
    app.ctx.user, app.ctx.permissions, app.ctx.departments = await db_manager.setup_db()


@app.route('/user/<user_name>', methods=['GET'])
async def get_user(request, user_name):
    try:
        data = await db_manager.user_get(user_name)
        if data:
            return create_response(200, "用户信息获取成功", data)
        else:
            return create_response(404, "用户不存在")
    except Exception as e:
        print(e)
        return (exc(e))


@app.route('/user/create', methods=['GET', 'POST'])
@la.template("createuser.html")
async def create_user(request):
    if request.method == 'GET':
        return create_response(100, "准备创建用户", {})
    elif request.method == 'POST':
        try:
            json_data = db_manager.user_create(request.json)
            return create_response(200, "用户创建成功", json_data)
        except Exception as e:
            return exc(e)


@app.route('/user/delet/<user_name>', methods=['GET'])
async def delete_user(request, user_name):
    try:
        result = await db_manager.user_delet(user_name)
        if result.deleted_count > 0:
            return create_response(200, "用户删除成功")
        else:
            return create_response(404, "用户不存在")
    except Exception as e:
        return exc(e)


@app.route('/permissions/create', methods=['GET', 'POST'])
@la.template("create_permissions.html")
async def create_permissions(request):
    if request.method == 'GET':
        return create_response(100, "准备创建权限", {})
    elif request.method == 'POST':
        try:
            data=db_manager.permissions_create(request.json)
            return create_response(200, "权限创建成功", data)
        except Exception as e:
            return exc(e)


@app.route('/permissions/change', methods=['GET', 'POST'])
@la.template("create_change.html")
async def change_permissions(request):
    if request.method == 'GET':
        return create_response(100, "准备修改权限", {})
    elif request.method == 'POST':
        try:
            return db_manager.permissions_change(request.json)
        except Exception as e:
            return exc(e)


@app.route('/permissions/delet/<permissions_name>', methods=['GET'])
async def delete_permissions(request, permission_name):
    try:
        return db_manager.permissions_delet(permission_name)
    except Exception as e:
        return exc(e)


@app.route('/departments/create', methods=['GET', 'POST'])
@la.template("create_departments.html")
async def create_departments(request):
    if request.method == 'GET':
        return create_response(100, "准备创建部门", {})
    elif request.method == 'POST':
        try:
            return db_manager.departments_create(request.json)
        except Exception as e:
            return exc(e)


@app.route('/departments/change', methods=['GET', 'POST'])
@la.template("change_departments.html")
async def change_departments(request):
    if request.method == 'GET':
        return create_response(100, "准备修改权限", {})
    elif request.method == 'POST':
        try:
             return  db_manager.departments_change(request.json)
        except Exception as e:
            return exc(e)


if __name__ == '__main__':
    app.run(port=8000)
