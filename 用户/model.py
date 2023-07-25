from mongoengine import connect, Document, StringField, DateTimeField
from datetime import datetime



# 定义用户数据模型
class User(Document):
    工号 = StringField(required=True)  # 用户工号，必填字段
    姓名 = StringField(required=True)  # 用户姓名，必填字段
    用户名 = StringField(required=True, unique=True)  # 用户名，必填字段且唯一
    电话 = StringField()  # 用户电话号码，可选字段
    邮箱 = StringField()  # 用户邮箱，可选字段
    入职时间 = DateTimeField()  # 用户入职时间，日期时间字段，可选
    职位 = StringField()  # 用户职位，可选字段
    部门编号 = StringField()  # 用户所属部门编号，可选字段
    权限 = StringField()  # 用户权限，可选字段

# 定义权限数据模型
class Permission(Document):
    权限名 = StringField(required=True, unique=True)  # 权限名称，必填字段且唯一
    权限 = StringField()  # 权限详细信息，可选字段

# 定义部门数据模型
class Department(Document):
    部门编号 = StringField(required=True, unique=True)  # 部门编号，必填字段且唯一
    部门名 = StringField()  # 部门名称，可选字段
    父节点 = StringField()  # 部门的父节点，可选字段
    部门简介 = StringField()  # 部门简介，可选字段
