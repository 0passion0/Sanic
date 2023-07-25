class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NullError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class intoError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def divdata(n):
    if n is None:
        raise CustomError("父节点不存在")
    return True


def nulldata(n):
    if n is None:
        raise NullError("前端返回数据为空")
    return True


def intodata(n):
    if n is None:
        raise NullError("部门不存在")
    return True


def exc(e):
    if "E11000 duplicate key error" in str(e):
        return create_response(501, "主键已被占用，请选择一个不同的主键")
    elif "父节点不存在" in str(e):
        return create_response(502, "父节点不存在")
    elif "前端返回数据为空" in str(e):
        # print("前端返回数据为空")
        return create_response(503, "前端返回数据为空")
    elif "部门不存在" in str(e):
        print("部门不存在")
        return create_response(504, "部门不存在")
    return create_response(500, str(e))
def create_response(code, msg, data=None):
    if data:
        return {"code": code, "msg": msg, "data": data}
    else:
        return {"code": code, "msg": msg}