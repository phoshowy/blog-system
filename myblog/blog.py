import os
import re

import sqlite3

import flask
from flask import Flask, render_template, request, url_for, flash, redirect, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'maishu is fat again, 555'


# 创建一个函数用来获取数据库链接
def get_db_connection():
    # 创建数据库链接到database.db文件
    conn = sqlite3.connect('database.db')
    # 设置数据的解析方法，有了这个设置，就可以像字典一样访问每一列数据
    conn.row_factory = sqlite3.Row
    return conn


# 根据post_id从数据库中获取post
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    return post


def get_user_info(user_id):
    conn = get_db_connection()
    result_info = conn.execute('SELECT * FROM users WHERE user_id = ?',
                               (user_id,)).fetchone()
    conn.close()
    return result_info


def get_comment_info(comment_id):
    conn = get_db_connection()
    comment_info = conn.execute('SELECT * FROM comments WHERE id = ?',
                                (comment_id,)).fetchall()
    conn.close()
    return comment_info


@app.route('/', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        user = flask.request.values.get("user", "")
        pwd = flask.request.values.get("pwd", "")

        if user != None and pwd != None:  # 验证通过
            msg = '用户名或密码错误'
            # 正则验证通过后与数据库中数据进行比较
            sql = "select * from users where user_name='" + \
                  user + "' and password='" + pwd + "';"
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            # 匹配得到结果即管理员数据库中存在此管理员
            if result:
                # 登陆成功
                conn = get_db_connection()
                user_info = conn.execute('SELECT * FROM users WHERE user_name = ?',
                                         (user,)).fetchone()
                conn.close()

                if user_info['role'] == 'admin':
                    return flask.redirect('/index_user')
                elif user_info['role'] == 'user':
                    return render_template('about.html', user_info=user_info)
                else:
                    return flask.redirect('/other')
                # return flask.redirect('/file')
        else:  # 输入验证不通过
            msg = '非法输入'
    else:
        msg = ''
        user = ''
    return flask.render_template('userlogin.html', msg=msg, user=user)


@app.route('/index')
def index():
    # 调用上面的函数，获取链接
    conn = get_db_connection()
    # 查询所有数据，放到变量posts中
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    # 把查询出来的posts传给网页
    return render_template('index.html', posts=posts)


@app.route('/posts/<int:post_id>')
def post(post_id):
    post = get_post(post_id)

    return render_template('post.html', post=post)


basedir = os.path.abspath(os.path.dirname(__file__))


@app.route('/posts/new', methods=('GET', 'POST'))
def new():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        brief = request.form['brief']
        tag = request.form['tag']
        img = request.files['img']
        filename=img.filename
        file_path = basedir + "/static/tmp/" +str(title)+".png" # basedir 代表获取当前位置的绝对路径
        img.save(file_path)  # 把图片保存到static 中的file 文件名

        file_path_url="/static/./tmp/"+title+".png"
        if not title:
            flash('标题不能为空!')
        elif not content:
            flash('内容不能为空')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content,brief,tag,img) VALUES (?,?, ?,?,?)',
                         (title, content, brief, tag, file_path_url))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))
    return render_template('news.html')


@app.route('/posts/<int:id>/edit', methods=['POST', 'GET'])
def edit(id):
    post = get_post(id)

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']

        brief = request.form['brief']
        tag = request.form['tag']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?,brief=?,tag=?'
                         ' WHERE id = ?',
                         (title, content, brief, tag, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/posts/<int:id>/edit_comment/<int:comment_id>', methods=['POST', 'GET'])
@app.route('/posts/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" 删除成功!'.format(post['title']))
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')


##########################################
@app.route('/index_user')
def index_user():
    # 调用上面的函数，获取链接
    conn = get_db_connection()
    # 查询所有数据，放到变量posts中
    posts_user = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    # 把查询出来的posts传给网页
    return render_template('index_user.html', posts_user=posts_user)


@app.route('/posts_user/<int:user_id>')
def post_user(user_id):
    post_user = get_user_info(user_id)
    return render_template('post_user.html', post_user=post_user)


@app.route('/posts_user/news_user', methods=('GET', 'POST'))
def new_user():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        role = request.form['role']

        if not user_name:
            flash('用户不能为空!')
        elif not password:
            flash('密码不能为空')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (user_name,password,role) VALUES (?,?,?)',
                         (user_name, password, role))
            conn.commit()
            conn.close()
            return redirect(url_for('index_user'))

    return render_template('news_user.html')


@app.route('/posts_user/<int:user_id>/edit_user', methods=['POST', 'GET'])
def edit_user(user_id):
    post_user = get_user_info(user_id)

    if request.method == 'POST':

        user_name = flask.request.values.get("user_name", "")
        password = flask.request.values.get("password", "")

        role = flask.request.values.get("role", "")

        if not user_name:
            flash('name is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE users SET user_name = ?, password = ?,role=?'
                         ' WHERE user_id = ?',
                         (user_name, password, role, user_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index_user'))

    return render_template('edit_user.html', post_user=post_user)


@app.route('/posts_user/<int:user_id>/delete_user', methods=('POST',))
def delete_user(user_id):
    post_user = get_user_info(user_id)
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash('"{}" 删除成功!'.format(post_user['user_name']))
    return redirect(url_for('index_user'))


@app.route('/other')
def other():
    # 调用上面的函数，获取链接
    conn = get_db_connection()
    # 查询所有数据，放到变量posts中
    posts = conn.execute('SELECT * FROM posts_other').fetchall()
    conn.close()
    # 把查询出来的posts传给网页

    return render_template('other.html', posts=posts)


################
@app.route('/index_comment')
def index_comment():
    # 调用上面的函数，获取链接
    conn = get_db_connection()
    # 查询所有数据，放到变量posts中
    comments = conn.execute('SELECT * FROM comments').fetchall()
    conn.close()
    # 把查询出来的posts传给网页
    return render_template('index_comment.html', comments=comments)


@app.route('/posts_comment/<int:comment_id>')
def post_comment(comment_id):
    post_comment = get_comment_info(comment_id)
    return render_template('post_comment.html', post_comment=post_comment)


@app.route('/news_comment', methods=('GET', 'POST'))
def new_comment():
    if request.method == 'POST':

        content = request.form['content']
        id = request.form['id']

        if not content:
            flash('content不能为空!')

        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO comments (id,content) VALUES (?,?)',
                         (id, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('news_comment.html')


@app.route('/posts_comment/<int:comment_id>/edit_comment', methods=['POST', 'GET'])
def edit_comment(comment_id):
    comment = get_comment_info(comment_id)

    if request.method == 'POST':

        content = flask.request.values.get("content", "")
        id = flask.request.values.get("id", "")

        if not content:
            flash('content is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE comments SET content = ?, id = ?'
                         ' WHERE comment_id = ?',
                         (content, id, comment_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index_comment'))

    return render_template('edit_comment.html', comment=comment)


@app.route('/posts_comment/<int:comment_id>/delete_comment', methods=('POST',))
def delete_comment(comment_id):
    post_comment = get_user_info(comment_id)
    conn = get_db_connection()
    conn.execute('DELETE FROM comments WHERE comment_id = ?', (comment_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index_comment'))
