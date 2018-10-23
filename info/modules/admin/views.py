import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, session, redirect, g, jsonify

from info import user_login_data
from info.models import User
from info.utils.response_code import RET
from . import admin_blue

#功能描述: 用户列表统计
# 请求路径: /admin/user_list
# 请求方式: GET
# 请求参数: p
# 返回值:渲染user_list.html页面,data字典数据
@admin_blue.route('/user_list')
def user_list():
    """
    - 1.获取参数
    - 2.参数类型转换
    - 3.分页查询
    - 4.获取分页对象属性,总页数,当前页,当前页对象
    - 5.将对象列表,转成字典列表
    - 6.携带数据渲染页面
    :return:
    """
    # - 1.获取参数
    page = request.args.get("p","1")

    # - 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # - 3.分页查询
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取用户失败")

    # - 4.获取分页对象属性,总页数,当前页,当前页对象
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # - 5.将对象列表,转成字典列表
    user_list = []
    for user in items:
        user_list.append(user.to_admin_dict())

    # - 6.携带数据渲染页面
    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "user_list":user_list
    }
    return render_template("admin/user_list.html",data=data)

# 用户统计
# 请求路径: /admin/user_count
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面user_count.html,字典数据
@admin_blue.route('/user_count')
def user_count():
    """
    - 1.查询总人数,不包含管理员
    - 2.查询月活人数
    - 3.查询日活人数
    - 4.时间段内的, 活跃人数
    - 5.携带数据,渲染页面
    :return:
    """
    # - 1.查询总人数,不包含管理员
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # - 2.查询月活人数
    cal = time.localtime()
    try:

        #2.1本月1号的0点, 的字符串表示
        month_startTime_str = "%d-%d-01"%(cal.tm_year,cal.tm_mon) # 2018-10-01
        # strptime()==> string parse time, 参数1: 表示时间字符串,  参数2: 格式
        month_startTime_date = datetime.strptime(month_startTime_str,"%Y-%m-%d")

        #2.2 此时的时间
        month_endTime_date = datetime.now()

        #2.3查询, 时间段内的人数
        month_count = User.query.filter(User.last_login >= month_startTime_date, User.last_login <= month_endTime_date,User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # - 3.查询日活人数
    try:

        #2.1本日的0点, 的字符串表示
        day_startTime_str = "%d-%d-%d"%(cal.tm_year,cal.tm_mon,cal.tm_mday) # 2018-10-01
        # strptime()==> string parse time, 参数1: 表示时间字符串,  参数2: 格式
        day_startTime_date = datetime.strptime(day_startTime_str,"%Y-%m-%d")

        #2.2 此时的时间
        day_endTime_date = datetime.now()

        #2.3查询, 时间段内的人数
        day_count = User.query.filter(User.last_login >= day_startTime_date, User.last_login <= day_endTime_date,User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # - 4.时间段内的, 活跃人数
    active_date = [] #活跃的日期
    active_count = [] #获取人数
    for i in range(0, 31):
        # 当天开始时间A
        begin_date = day_startTime_date - timedelta(days=i)
        # 当天开始时间, 的后一天B
        end_date = day_startTime_date - timedelta(days=i - 1)

        # 添加当天开始时间字符串到, 活跃日期中
        active_date.append(begin_date.strftime("%m-%d"))

        # 查询时间A到B这一天的注册人数
        everyday_active_count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                                  User.last_login <= end_date).count()

        # 添加当天注册人数到,获取数量中
        active_count.append(everyday_active_count)

    #为了方便查看图标反转图标
    active_date.reverse()
    active_count.reverse()

    # - 5.携带数据,渲染页面
    data = {
        "total_count":total_count,
        "month_count":month_count,
        "day_count":day_count,
        "active_date":active_date,
        "active_count":active_count
    }
    return render_template("admin/user_count.html",data=data)


#显示管理员首页页面
# 请求路径: /admin/index
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面index.html,user字典数据
@admin_blue.route('/index')
@user_login_data
def admin_index():
    admin = g.user.to_dict() if g.user else ""
    return render_template("admin/index.html",admin=admin)


#显示登录页面
# 请求路径: /admin/login
# 请求方式: GET,POST
# 请求参数:GET,无, POST,username,password
# 返回值: GET渲染login.html页面, POST,login.html页面,errmsg
@admin_blue.route('/login',methods=["GET","POST"])
def admin_login():
    """
    - 1.判断请求方式,如果是GET请求,直接返回登陆页面
    - 2.如果是POST,获取参数
    - 3.校验参数,为空校验
    - 4.通过用户名,查询管理员对象, 并判断管理员是否存在
    - 5.判断密码是否正确
    - 6.记录管理员session信息
    - 7.重定向到首页
    :return:
    """
    # - 1.判断请求方式,如果是GET请求,直接返回登陆页面
    if request.method == 'GET':

        #判断管理员是否,已经登陆过
        if session.get("is_admin"):
            return redirect("/admin/index")

        return render_template("admin/login.html")

    # - 2.如果是POST,获取参数
    username = request.form.get("username")
    password = request.form.get("password")

    # - 3.校验参数,为空校验
    if not all([username,password]):
        return render_template("admin/login.html",errmsg="参数不全")

    # - 4.通过用户名,查询管理员对象, 并判断管理员是否存在
    try:
        admin = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html",errmsg="获取管理员失败")

    if not admin:
        return render_template("admin/login.html",errmsg="管理员不存在")

    # - 5.判断密码是否正确
    if not admin.check_passowrd(password):
        return render_template("admin/login.html",errmsg="密码错误")

    # - 6.记录管理员session信息
    session["user_id"] = admin.id
    session["nick_name"] = admin.nick_name
    session["mobile"] = admin.mobile
    session["is_admin"] = admin.is_admin

    # - 7.重定向到首页
    return redirect("/admin/index")