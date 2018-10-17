from info.models import News
from info.utils.response_code import RET
from . import news_blue
from flask import render_template, current_app, jsonify, abort


# 获取新闻详情
# 请求路径: /news/<int:news_id>
# 请求方式: GET
# 请求参数:news_id
# 返回值: detail.html页面, 用户data字典数据
@news_blue.route('/<int:news_id>')
def news_detail(news_id):

    #1.根据新闻编号获取,新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="新闻获取失败")

    #2.判断新闻对象是否存在,后续会对404做统一处理
    if not news:
        abort(404)

    #2.1 热门新闻,按照新闻的点击量量,查询前十条新闻
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(8).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    #2.2 将新闻列表对象,字典列表对象
    click_news_list = []
    for news in news_list:
        click_news_list.append(news.to_dict())

    #3.携带新闻数据,到模板页面显示
    data = {
        "news":news.to_dict(),
        "click_news_list":click_news_list
    }

    return render_template("news/detail.html",data=data)