"""
Application Routes using Blueprints
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from extensions import db
from models import Product
from sqlalchemy import or_

# Main blueprint for general pages
main_bp = Blueprint('main', __name__)

# Product blueprint for product-related pages
product_bp = Blueprint('products', __name__)


@main_bp.route('/')
def home():
    """Home page"""
    return render_template('home.html')


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@product_bp.route('/category/<category>')
def category_view(category):
    """View products by category with pagination and search"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        per_page = current_app.config.get('PRODUCTS_PER_PAGE', 20)

        # Build query
        query = Product.query.filter_by(category=category)

        # Add search filter if provided
        if search:
            search_filter = or_(
                Product.title.ilike(f'%{search}%'),
                Product.category.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)

        # Paginate results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return render_template(
            'category.html',
            products=pagination.items,
            pagination=pagination,
            category=category,
            search=search
        )

    except Exception as e:
        current_app.logger.error(f'Error in category view: {e}')
        flash('An error occurred while loading products.', 'error')
        return redirect(url_for('main.home'))


@product_bp.route('/<int:product_id>')
def product_view(product_id):
    """View individual product details"""
    try:
        product = Product.query.get_or_404(product_id)
        return render_template('product.html', product=product)
    except Exception as e:
        current_app.logger.error(f'Error loading product {product_id}: {e}')
        flash('Product not found.', 'error')
        return redirect(url_for('main.home'))


@product_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    """Add or update a product"""
    if request.method == 'POST':
        try:
            # Validate input
            product_id = request.form.get('id', type=int)
            title = request.form.get('title', '').strip()
            image = request.form.get('image', '').strip()
            price = request.form.get('price', type=float)
            stock = request.form.get('stock', type=int)
            category = request.form.get('category', '').strip()

            # Validation
            errors = []
            if not product_id or product_id <= 0:
                errors.append('Valid product ID is required.')
            if not title:
                errors.append('Product title is required.')
            if price is None or price < 0:
                errors.append('Valid price is required.')
            if stock is None or stock < 0:
                errors.append('Valid stock quantity is required.')
            if not category:
                errors.append('Category is required.')

            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('add_product.html')

            # Create or update product
            product = Product(
                id=product_id,
                title=title,
                image=image,
                price=price,
                stock=stock,
                category=category
            )

            db.session.merge(product)
            db.session.commit()

            flash(f'Product "{title}" added/updated successfully!', 'success')
            current_app.logger.info(f'Product {product_id} added/updated: {title}')

            return redirect(url_for('products.category_view', category=product.category))

        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'error')
            db.session.rollback()
        except Exception as e:
            current_app.logger.error(f'Error adding product: {e}')
            flash('An error occurred while adding the product.', 'error')
            db.session.rollback()

    return render_template('add_product.html')


@product_bp.route('/search')
def search():
    """Search products across all categories"""
    try:
        query_str = request.args.get('q', '', type=str).strip()
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('PRODUCTS_PER_PAGE', 20)

        if not query_str:
            flash('Please enter a search term.', 'warning')
            return redirect(url_for('main.home'))

        # Search in title and category
        search_filter = or_(
            Product.title.ilike(f'%{query_str}%'),
            Product.category.ilike(f'%{query_str}%')
        )

        pagination = Product.query.filter(search_filter).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return render_template(
            'search_results.html',
            products=pagination.items,
            pagination=pagination,
            query=query_str
        )

    except Exception as e:
        current_app.logger.error(f'Search error: {e}')
        flash('An error occurred during search.', 'error')
        return redirect(url_for('main.home'))
