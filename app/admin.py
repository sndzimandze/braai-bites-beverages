"""
Admin routes and authentication
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from functools import wraps
from models import db, Product
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin area.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Get credentials from environment variables
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')

        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    try:
        total_products = Product.query.count()
        in_stock = Product.query.filter(Product.stock > 0).count()
        out_of_stock = Product.query.filter(Product.stock == 0).count()

        # Get products by category
        categories = db.session.query(
            Product.category,
            db.func.count(Product.id).label('count')
        ).group_by(Product.category).all()

        return render_template('admin/dashboard.html',
                             total_products=total_products,
                             in_stock=in_stock,
                             out_of_stock=out_of_stock,
                             categories=categories)
    except Exception as e:
        current_app.logger.error(f'Error in admin dashboard: {e}')
        flash('An error occurred while loading the dashboard.', 'error')
        return redirect(url_for('main.home'))


@admin_bp.route('/products')
@login_required
def products():
    """Product management page"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        category_filter = request.args.get('category', '', type=str)
        per_page = 20

        query = Product.query

        if search:
            query = query.filter(
                db.or_(
                    Product.title.ilike(f'%{search}%'),
                    Product.category.ilike(f'%{search}%')
                )
            )

        if category_filter:
            query = query.filter_by(category=category_filter)

        query = query.order_by(Product.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Get all categories for filter dropdown
        categories = db.session.query(Product.category).distinct().order_by(Product.category).all()
        categories = [cat[0] for cat in categories]

        return render_template('admin/products.html',
                             products=pagination.items,
                             pagination=pagination,
                             search=search,
                             category_filter=category_filter,
                             categories=categories)
    except Exception as e:
        current_app.logger.error(f'Error in admin products: {e}')
        flash('An error occurred while loading products.', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product"""
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            image = request.form.get('image', '').strip()
            price = request.form.get('price', type=float)
            stock = request.form.get('stock', type=int)
            category = request.form.get('category', '').strip()

            # Validation
            if not title or not price or stock is None or not category:
                flash('Please fill in all required fields.', 'error')
                return render_template('admin/product_form.html', product=None, action='Add')

            if price < 0:
                flash('Price must be a positive number.', 'error')
                return render_template('admin/product_form.html', product=None, action='Add')

            if stock < 0:
                flash('Stock must be a positive number.', 'error')
                return render_template('admin/product_form.html', product=None, action='Add')

            # Create product
            product = Product(
                title=title,
                image=image if image else None,
                price=price,
                stock=stock,
                category=category
            )

            db.session.add(product)
            db.session.commit()

            flash(f'Product "{title}" has been added successfully!', 'success')
            return redirect(url_for('admin.products'))

        except ValueError:
            flash('Invalid price or stock value.', 'error')
            return render_template('admin/product_form.html', product=None, action='Add')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error adding product: {e}')
            flash('An error occurred while adding the product.', 'error')
            return render_template('admin/product_form.html', product=None, action='Add')

    return render_template('admin/product_form.html', product=None, action='Add')


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit existing product"""
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            image = request.form.get('image', '').strip()
            price = request.form.get('price', type=float)
            stock = request.form.get('stock', type=int)
            category = request.form.get('category', '').strip()

            # Validation
            if not title or not price or stock is None or not category:
                flash('Please fill in all required fields.', 'error')
                return render_template('admin/product_form.html', product=product, action='Edit')

            if price < 0:
                flash('Price must be a positive number.', 'error')
                return render_template('admin/product_form.html', product=product, action='Edit')

            if stock < 0:
                flash('Stock must be a positive number.', 'error')
                return render_template('admin/product_form.html', product=product, action='Edit')

            # Update product
            product.title = title
            product.image = image if image else None
            product.price = price
            product.stock = stock
            product.category = category

            db.session.commit()

            flash(f'Product "{title}" has been updated successfully!', 'success')
            return redirect(url_for('admin.products'))

        except ValueError:
            flash('Invalid price or stock value.', 'error')
            return render_template('admin/product_form.html', product=product, action='Edit')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating product: {e}')
            flash('An error occurred while updating the product.', 'error')
            return render_template('admin/product_form.html', product=product, action='Edit')

    return render_template('admin/product_form.html', product=product, action='Edit')


@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete product"""
    try:
        product = Product.query.get_or_404(product_id)
        title = product.title

        db.session.delete(product)
        db.session.commit()

        flash(f'Product "{title}" has been deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting product: {e}')
        flash('An error occurred while deleting the product.', 'error')

    return redirect(url_for('admin.products'))
