from flask import render_template, flash, redirect, request, session, url_for
from GroceryStore import app, db
from GroceryStore.forms import RegistrationForm, LoginForm, AdminLoginForm, CategoryForm, ProductForm, ProductSearchForm
from GroceryStore.models import User, Category, Product
from datetime import datetime
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import and_

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        if form.is_admin.data:
            new_user.is_admin = True
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html", title='Register', form=form)

@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, password=form.password.data, is_admin=False).first()
        if user:
            login_user(user)
            if user.is_admin:
                flash('Admin login successful!', 'success')
            else:
                flash('Login successful!', 'success')
            return redirect(url_for('user_products'))
        else:
            flash('Login failed. Invalid email or password.', 'danger')
            session['login_failed'] = True
    
    if session.pop('login_failed', False):
        flash('Login failed. Invalid email or password.', 'danger')

    return render_template("login.html", title='Login', form=form)

@app.route("/admin", methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = User.query.filter_by(email=form.email.data, password=form.password.data, is_admin=True).first()
        if admin:
            login_user(admin)
            flash('Admin login successful!', 'success')
            return redirect(url_for('user_products'))
        else:
            flash('Login failed. Invalid email or password.', 'danger')
            session['login_failed'] = True

    if session.pop('login_failed', False):
        flash('Login failed. Invalid email or password.', 'danger')
    
    return render_template("adminlogin.html", title='Admin Login', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    print("Is authenticated:", current_user.is_authenticated)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route("/cart", methods=['GET', 'POST'])
@login_required
def cart():
    user = current_user
    cart_items = user.purchases.all()
    total_amount = sum(cart_item.rate_per_unit * cart_item.quantity for cart_item in cart_items)

    if request.method == 'POST':

        user.purchases = []
        db.session.commit()

        flash('Purchase successful! Your cart is now empty.', 'success')
        return redirect(url_for('buy_success'))

    return render_template("cart.html", cart_items=cart_items, total_amount=total_amount, title='Cart')

@app.route("/manage_categories", methods=['GET', 'POST'])
@login_required
def manage_categories():
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('login'))

    form = CategoryForm()

    if form.validate_on_submit():
        new_category = Category(name=form.name.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('manage_categories'))

    categories = Category.query.all()
    return render_template("categories.html", form=form, categories=categories, title='Manage Categories')

@app.route("/add_category", methods=['GET', 'POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('login'))

    form = CategoryForm()

    if form.validate_on_submit():
        new_category = Category(name=form.name.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('manage_categories'))

    return render_template("add_category.html", form=form, title='Add Category')

@app.route("/edit_category/<int:category_id>", methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('login'))

    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('manage_categories'))

    return render_template("edit_category.html", form=form, category=category, title='Edit Category')


@app.route("/delete_category/<int:category_id>", methods=['POST'])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('login'))

    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('manage_categories'))

@app.route("/manage_products", methods=['GET', 'POST'])
@login_required
def manage_products():
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('login'))

    form = ProductForm()

    categories = Category.query.all()
    form.category.choices = [(category.id, category.name) for category in categories]

    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            manufacture_date=form.manufacture_date.data,
            expiry_date=form.expiry_date.data,
            rate_per_unit=form.rate_per_unit.data,
            category_id=form.category.data,
            units=form.units.data
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('manage_products'))
    
    products = db.session.query(Product, Category.name).join(Category).all()
    return render_template("manage_products.html", form=form, products=products, title='Manage Products')


@app.route("/edit_product/<int:product_id>", methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('login'))

    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    categories = Category.query.all()

    form.category.choices = [(category.id, category.name) for category in categories]

    if form.validate_on_submit():

        product.name = form.name.data
        product.manufacture_date = form.manufacture_date.data
        product.expiry_date = form.expiry_date.data
        product.rate_per_unit = form.rate_per_unit.data
        product.category_id = form.category.data
        product.units = form.units.data
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('manage_products'))

    return render_template("edit_product.html", form=form, product=product, categories=categories, title='Edit Product')


@app.route("/delete_product/<int:product_id>", methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('login'))

    product = Product.query.get_or_404(product_id)

    for user in product.buyers:
        user.purchases.remove(product)

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('manage_products'))

@app.route("/user_products", methods=['GET', 'POST'])
@login_required
def user_products():
    categories = Category.query.all()
    products_by_category = {}

    for category in categories:
        products = Product.query.filter_by(category_id=category.id).all()
        products_by_category[category] = products

    search_form = ProductSearchForm()

    if search_form.validate_on_submit():
        min_price = search_form.min_price.data
        max_price = search_form.max_price.data
        start_date = search_form.start_date.data
        end_date = search_form.end_date.data

        filter_criteria = []
        if min_price:
            filter_criteria.append(Product.rate_per_unit >= min_price)
        if max_price:
            filter_criteria.append(Product.rate_per_unit <= max_price)
        if start_date:
            filter_criteria.append(Product.manufacture_date >= start_date)
        if end_date:
            filter_criteria.append(Product.manufacture_date >= end_date)

        filtered_products = Product.query.filter(and_(*filter_criteria)).all()

        products_by_category = {'Filtered Products': filtered_products}

    return render_template("user_products.html", products_by_category=products_by_category, search_form=search_form, title='User Products')


@app.route("/add_to_cart/<int:product_id>", methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity'))

    if quantity <= 0:
        flash('Quantity must be greater than 0.', 'danger')
        return redirect(url_for('user_products'))

    if product.units <= 0:
        flash(f"'{product.name}' is out of stock.", 'danger')
        return redirect(url_for('user_products'))

    if quantity > product.units:
        flash(f"Available quantity for '{product.name}' is {product.units}.", 'danger')
        return redirect(url_for('user_products'))

    user = current_user
    existing_purchase = user.purchases.filter_by(id=product_id).first()

    if existing_purchase:
        existing_purchase.quantity += quantity
    else:
        new_purchase = Product.query.get_or_404(product_id)
        new_purchase.units -= quantity
        new_purchase.quantity = quantity
        user.purchases.append(new_purchase)

    db.session.commit()

    flash(f'{quantity} {product.name}(s) added to your cart.', 'success')
    return redirect(url_for('user_products'))

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    categories = Category.query.all()
    search_form = ProductSearchForm()
    search_form.category.choices = [(category.id, category.name) for category in categories]

    if search_form.validate_on_submit():
        category_id = search_form.category.data
        min_price = search_form.min_price.data
        max_price = search_form.max_price.data
        start_date = search_form.start_date.data
        end_date = search_form.end_date.data

        query = db.session.query(Product, Category.name).join(Category)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if min_price:
            query = query.filter(Product.rate_per_unit >= min_price)
        if max_price:
            query = query.filter(Product.rate_per_unit <= max_price)
        if start_date:
            query = query.filter(Product.manufacture_date >= start_date)
        if end_date:
            query = query.filter(Product.expiry_date >= end_date)

        filtered_products = query.all()

        return render_template("search_results.html", products=filtered_products, title='Search Results')

    return render_template("search.html", search_form=search_form, title='Search Products')

@app.route("/buy_success", methods=['GET','POST'])
@login_required
def buy_success():

    user = current_user
    user.purchases = []
    db.session.commit()

    return render_template("buy_success.html", title='Purchase Success')


@app.route("/clean_cart", methods=['POST'])
@login_required
def clean_cart():
    user = current_user
    for cart_item in user.purchases:
        cart_item.quantity = 0
    db.session.commit()
    flash('Cart cleaned successfully!', 'success')
    return redirect(url_for('cart'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    user = current_user
    cart_items = user.purchases.all()
    total_amount = sum(cart_item.rate_per_unit * cart_item.quantity for cart_item in cart_items)

    return render_template("account.html", user=user, cart_items=cart_items, total_amount=total_amount, title='Account')
