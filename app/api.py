from flask import current_app, url_for, request, render_template, redirect, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from app.utils.user_util import validate_user, register_user
from uuid import uuid4
from json import dumps
from app import db
from app.models import Item, ItemImage, UserAddress, ItemOrder
import os

def init_api(app):

    @app.route('/var/<path:filename>')
    def var_file(filename):
        return send_from_directory(current_app.config['VAR_DIR'], filename, as_attachment=True)

    @app.route('/')
    def index():
        # items = Item.query.filter_by(status=1).order_by(Item.created_time.desc()).all()
        dig_items = Item.query.filter_by(status=1, category=0).order_by(Item.created_time.desc()).limit(4).all()
        print(dig_items)
        bk_items = Item.query.filter_by(status=1, category=1).order_by(Item.created_time.desc()).limit(4).all()
        oth_items = Item.query.filter_by(status=1, category=2).order_by(Item.created_time.desc()).limit(4).all()
        return render_template('index.html', dig_items=dig_items, bk_items=bk_items, oth_items=oth_items)

    # 商品分类
    @app.route('/category_items')
    def category_items():
        category_num = int(request.args.get('category'))
        items = Item.query.filter_by(status=1, category=category_num).order_by(Item.created_time.desc()).all()
        return render_template('category_items.html', items=items)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            if current_user and current_user.is_authenticated:
                logout_user()
            return render_template('register.html')

        account = request.form['account']
        password = request.form['password']
        user = register_user(account, password)
        if not user:
            return redirect(url_for('.register'))
        login_user(user)
        return redirect(url_for('.index'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            if current_user and current_user.is_authenticated:
                return redirect(url_for('.index'))
            return render_template('login.html')

        account = request.form['account']
        password = request.form['password']
        user = validate_user(account, password)
        if not user:
            return redirect(request.url)
        login_user(user)
        return_url = request.args.get('return')
        if return_url:
            return redirect(return_url)
        return redirect(url_for('.index'))

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('.index'))


    @app.route('/page/home')
    @login_required
    def page_home():
        items = Item.query.filter_by(user_sn=current_user.sn).filter(Item.status!=4).order_by(Item.created_time.desc()).all()
        return render_template('home_index.html', items=items)

    @app.route('/page/edit_item')
    @login_required
    def page_edit_item():
        item_sn = request.args.get('sn')
        print(item_sn)
        item = Item.query.filter_by(sn=item_sn).first()
        if item:
            item_dict = {'name': item.name,
                'price': item.price,
                'category': item.category,
                'describe': item.describe}
        else:
            item_dict = ''
        return render_template('edit_item.html', item=item_dict)
        

    @app.route('/profile_image', methods=['POST'])
    @login_required
    def upload_profile_image():
        file = request.files['file']
        if not file:
            return dumps({'code': -1, 'msg': 'file is none'})

        file_dir = current_app.config['VAR_DIR'] + 'profile_images/' 
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        file_ext = os.path.splitext(file.filename)[1]
        if not file_ext or file_ext == '.':
            return dumps({'code': -2, 'msg': 'file_ext is none'})

        file_name = str(uuid4()).replace('-', '') + file_ext
        file.save(file_dir + file_name)

        current_user.profile_image = file_name
        db.session.add(current_user)
        db.session.commit()

        return dumps({'code': 0, 'filename': file_name})

    @app.route('/page/address')
    @login_required
    def page_address():
        addresss = UserAddress.query.filter_by(user_sn=current_user.sn, deleted=False).order_by(UserAddress.created_time.desc()).all()
        return render_template('home_address.html', addresss=addresss)

    @app.route('/address/<address_sn>', methods=['DELETE'])
    @login_required
    def del_address(address_sn):
        UserAddress.query.filter_by(sn=address_sn).update({'deleted': True})
        db.session.commit()
        return dumps({'code': 0})

    @app.route('/address', methods=['POST'])
    @login_required
    def add_address():
        address = request.form['address']
        people = request.form['people']
        mobile = request.form['mobile']

        print(address, people, mobile)

        add = UserAddress(user_sn=current_user.sn, address=address, people=people, mobile=mobile)
        db.session.add(add)
        db.session.commit()
        return redirect(url_for('.page_address'))


    @app.route('/item/filter', methods=['GET'])
    def filter_item():
        condition = request.args.get('condition')
        print(condition)
        items = Item.query.filter(Item.name.like('%'+condition+'%')).filter_by(status=1).all()
        return render_template('category_items.html', items=items)

    @app.route('/item/<item_sn>', methods=['GET'])
    @login_required
    def get_item_images(item_sn):
        item = Item.query.filter_by(sn=item_sn).first()
        if not item:
            return dumps({'code': -1, 'msg': 'not find item'})
        item_dict = {'name': item.name,
                    'price': item.price,
                    'category': item.category,
                    'describe': item.describe,
                    'update_time': str(item.update_time)}

        item_images = ItemImage.query.filter_by(item_sn=item_sn,deleted=False).all()
        print(item_images)
        images = [{'filename': image.filename,'is_main': image.is_main} for image in item_images]
        return dumps({'code': 0, 'item': item_dict, 'images': images})

    # 商品详情
    @app.route('/page/item/<item_sn>', methods=['GET'])
    def page_item(item_sn):
        item = Item.query.filter_by(sn=item_sn).first()
        if not item:
            return dumps({'code': -1, 'msg': 'not find item'})
        if item.status != 1:
            return dumps({'code':-2, 'msg':'status is not allowed'})

        item_images = ItemImage.query.filter_by(item_sn=item_sn,deleted=False).all()
        print(item_images)
        images = [{'filename': image.filename,'is_main': image.is_main} for image in item_images]
        return render_template('detail_item.html', item=item, images=images)

    @app.route('/item', methods=['POST'])
    @login_required
    def upload_item():
        item_sn = request.form['item_sn']
        item_name = request.form['item_name']
        item_price = request.form['item_price']
        item_category = request.form['item_category']
        item_describe = request.form['item_describe']
        item_status = request.form['item_status']

        item_price = int(item_price) if item_price else 0

        print(item_sn)
        if item_sn:
            item = Item(user_sn=current_user.sn, name=item_name, price=item_price, category=item_category, describe=item_describe)
            print(">>>>>>>")
            print(item)
            db.session.add(item)
            db.session.commit()
            db.session.flush()
            db.session.refresh(item)
        else:
            Item.query.filter_by(sn=item_sn).update({'name': item_name,
                                                    'price': item_price,
                                                    'category': item_category,
                                                    'describe': item_describe,
                                                    'status': item_status})
            db.session.commit()
            print(current_user)
            item = Item.query.filter_by(sn=item_sn).first()
        item_sn = item.sn

        file_dir = current_app.config['VAR_DIR'] + 'item_images/'
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        for i in request.files:
            file = request.files[i]

            file_ext = os.path.splitext(file.filename)[1]
            if not file_ext or file_ext == '.':
                continue

            filename = str(uuid4()).replace('-', '') + file_ext
            file.save(file_dir + filename)

            image = ItemImage(item_sn=item_sn, filename=filename)
            db.session.add(image)
        db.session.commit()
        return dumps({'code': 0, 'item_sn': item_sn})

    @app.route('/item/<item_sn>/status/<new_status>')
    @login_required
    def chagne_item_status(item_sn, new_status):
        allow_change_status = {0:[0,1,2,4], 1:[0,1,2,3,4], 2:[0,1,2,3], 3:[3,4], 4:[4]}
        old_status = db.session.query(Item.status).filter_by(sn=item_sn).limit(1).scalar()

        if int(new_status) not in allow_change_status[old_status]:
            return dumps({'code': -1, 'msg':'not allow change this status'})

        item = Item.query.filter_by(sn=item_sn,user_sn=current_user.sn).update({'status':new_status})
        db.session.commit()
        return dumps({'code': 0})

    @app.route('/item/<item_sn>/main_image/<filename>')
    @login_required
    def set_item_main_image(item_sn, filename):
        ItemImage.query.filter_by(item_sn=item_sn).update({'is_main':False})
        ItemImage.query.filter_by(item_sn=item_sn,filename=filename).update({'is_main':True})
        Item.query.filter_by(sn=item_sn).update({'main_image': filename})
        db.session.commit()
        return dumps({'code': 0})

    @app.route('/item/<item_sn>/item_image/<filename>', methods=['DELETE'])
    @login_required
    def delete_item_image(item_sn, filename):
        ItemImage.query.filter_by(item_sn=item_sn,filename=filename).update({'deleted': True})
        db.session.commit()
        return dumps({'code': 0})

    @app.route('/page/confirm_order/<item_sn>', methods=['GET', 'POST'])
    @login_required
    def page_confirm_order(item_sn):
        item = Item.query.filter_by(sn=item_sn).first()
        if item.status != 1:
            return dumps({'code':-1, 'msg':'status is not allowed'})

        default_address = UserAddress.query.filter_by(user_sn=current_user.sn,is_default=True,deleted=False).first()
        if not default_address:
            default_address = UserAddress.query.filter_by(user_sn=current_user.sn,deleted=False).order_by(UserAddress.created_time.desc()).first()

        return render_template('order_confirm.html', item=item, address=default_address)



    @app.route('/order', methods=['POST'])
    @login_required
    def add_order():
        item_sn = request.form.get('item_sn')
        address_sn = request.form.get('address_sn')
        print(item_sn)
        item = Item.query.filter_by(sn=item_sn, deleted=False).first()
        if not item:
            return dumps({'code':-1, 'msg':'no item'})

        address = UserAddress.query.filter_by(sn=address_sn).first()
        if not address:
            return dumps({'code':-2, 'msg':'no address'})

        order = ItemOrder(user_sn=current_user.sn, 
                        seller_sn=item.user_sn, 
                        item_sn=item.sn, 
                        item_name=item.name, 
                        item_price=item.price, 
                        main_image=item.main_image, 
                        people=address.people, 
                        mobile=address.mobile, 
                        address=address.address)
        db.session.add(order)

        Item.query.filter_by(sn=item_sn).update({'status':2})
        db.session.commit()

        
        return dumps({'code':0, 'order_sn':order.sn})


    @app.route('/page/orders')
    @login_required
    def page_orders():
        orders = ItemOrder.query.filter_by(user_sn=current_user.sn, deleted=False).all()
        return render_template('home_order.html', orders=orders)


    @app.route('/page/order/<order_sn>')
    @login_required
    def page_pay(order_sn):
        order = ItemOrder.query.filter_by(sn=order_sn, deleted=False).first()
        return render_template('order.html', order=order)


    @app.route('/pay_order/<order_sn>')
    @login_required
    def pay_order(order_sn):
        order = ItemOrder.query.filter_by(sn=order_sn, deleted=False).first()
        if not order:
            return dumps({'code':-1, 'msg':'no order'})
        if order.status == 1:
            return dumps({'code':-2, 'msg':'order already paid'})

        ItemOrder.query.filter_by(sn=order_sn).update({'status':1})
        Item.query.filter_by(sn=order.item_sn).update({'status':3})
        db.session.commit()

        return dumps({'code':0})
