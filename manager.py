"""
项目的初始化配置信息:
项目的初始化配置信息:

1.数据库配置

2.redis配置

3.csrf配置,对'POST', 'PUT', 'PATCH', 'DELETE'请求方式做保护

4.session配置,为了后续登陆保持,做铺垫

5.日志信息配置

6.数据库迁移配置

"""""

from info import create_app

#调用业务模块获取app
app = create_app("develop")


@app.route('/')
def hello_world():

    #测试redis,存取数据
    # redis_store.set("name","laowang")
    # print(redis_store.get("name"))

    #测试session,存取数据
    # session["age"] = "13"
    # print(session.get("age"))

    return "helloworld100"

if __name__ == '__main__':
    app.run()