# 🔥 Braai Bites & Beverages

A modern Flask e-commerce application for braai equipment, craft beer, wine, spirits, and snacks. Features AliExpress API integration for product synchronization.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🛍️ **Product Management**: Browse and search products across multiple categories
- 🔍 **Advanced Search**: Full-text search with pagination
- 📱 **Responsive Design**: Mobile-first, fully responsive UI
- 🔄 **AliExpress Integration**: Sync products from AliExpress API
- 🔐 **Secure Configuration**: Environment-based configuration with validation
- 📊 **Database Migrations**: Flask-Migrate for database version control
- 🎨 **Modern UI**: Clean, professional design with smooth animations
- ⚠️ **Error Handling**: Comprehensive error handling and validation
- 📝 **Logging**: Application-wide logging for debugging and monitoring
- 🏗️ **Blueprint Architecture**: Organized, scalable code structure

## 📋 Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Syncing Products](#syncing-products)
- [Project Structure](#project-structure)
- [API Integration](#api-integration)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Requirements

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)
- AliExpress API credentials (App Key and App Secret)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd braaibitesbeverages_flask_final
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

### 2. Edit .env File

Open `.env` in your text editor and configure the following:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Database
DATABASE_URL=sqlite:///braaibites.db

# AliExpress API Credentials
ALIEXPRESS_APP_KEY=your_app_key_here
ALIEXPRESS_APP_SECRET=your_app_secret_here
ALIEXPRESS_API_URL=https://gw.api.alibaba.com/openapi/

# OAuth Configuration (if using OAuth)
ALIEXPRESS_REDIRECT_URI=https://yourdomain.com/auth/callback
ALIEXPRESS_AUTH_URL=https://sandbox.oauth.alibaba.com/authorize
ALIEXPRESS_TOKEN_URL=https://sandbox.oauth.alibaba.com/token
ALIEXPRESS_HOST=https://sandbox.api.alibaba.com
```

**Important:**
- Replace `your_app_key_here` and `your_app_secret_here` with your actual AliExpress API credentials
- Generate a strong `SECRET_KEY` for production using: `python -c "import secrets; print(secrets.token_hex(32))"`
- Never commit the `.env` file to version control

### 3. Get AliExpress API Credentials

1. Sign up at [AliExpress Open Platform](https://open.alibaba.com/)
2. Create a new application
3. Copy your App Key and App Secret
4. Add them to your `.env` file

## 🗄️ Database Setup

### 1. Initialize Database

The database will be automatically created when you first run the application. However, you can also use Flask-Migrate for better control:

```bash
# Initialize migrations (first time only)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

### 2. Verify Database

The SQLite database file will be created at `instance/braaibites.db`

## 🚀 Running the Application

### Development Server

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Server

For production, use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🔄 Syncing Products

The application includes a powerful sync utility for importing products from AliExpress.

### Quick Sync (API Key Method)

This is the simplest method that doesn't require OAuth:

```bash
python -m app.utils.aliexpress_sync sync
```

**Options:**
```bash
# Sync specific keywords
python -m app.utils.aliexpress_sync sync --keywords "craft beer" "wine"

# Limit pages per keyword
python -m app.utils.aliexpress_sync sync --pages 3
```

### OAuth Method

If you need OAuth authentication:

#### Step 1: Generate Auth URL
```bash
python -m app.utils.aliexpress_sync auth-url
```

This will output an authorization URL. Open it in your browser and authorize the application.

#### Step 2: Exchange Code for Token
After authorization, you'll receive a code. Exchange it for an access token:

```bash
python -m app.utils.aliexpress_sync fetch-token --code YOUR_AUTH_CODE
```

This will output an access token.

#### Step 3: Sync with Token
```bash
python -m app.utils.aliexpress_sync sync-oauth --token YOUR_ACCESS_TOKEN
```

### Default Product Categories

The sync utility searches for these categories by default:
- Braai Grill
- Braai Tools
- Craft Beer
- Wine
- Spirits
- Braai Snacks

## 📁 Project Structure

```
braaibitesbeverages_flask_final/
│
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── routes.py                # Blueprint routes
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       └── aliexpress_sync.py   # Product sync utility
│
├── templates/                    # HTML templates
│   ├── base.html               # Base template
│   ├── home.html               # Homepage
│   ├── about.html              # About page
│   ├── category.html           # Category listing
│   ├── product.html            # Product detail
│   ├── add_product.html        # Add product form
│   ├── search_results.html     # Search results
│   └── errors/                 # Error pages
│       ├── 404.html
│       └── 500.html
│
├── static/                       # Static files
│   └── css/
│       └── style.css           # Main stylesheet
│
├── instance/                     # Instance-specific files
│   └── braaibites.db           # SQLite database
│
├── venv/                         # Virtual environment
│
├── .env                          # Environment variables (not in git)
├── .env.example                  # Example environment file
├── .gitignore                    # Git ignore file
├── app.py                        # Application entry point
├── config.py                     # Configuration
├── extensions.py                 # Flask extensions
├── models.py                     # Database models
├── requirements.txt              # Python dependencies
├── manage.py                     # Database management
└── README.md                     # This file
```

## 🔌 API Integration

### AliExpress API

The application integrates with AliExpress Product API to fetch and sync products.

**Key Features:**
- MD5 signature-based authentication
- Support for both API key and OAuth methods
- Automatic rate limiting and error handling
- Batch product import
- Category-based organization

**API Documentation:**
- [AliExpress Open Platform](https://open.alibaba.com/)
- [API Reference](https://developers.aliexpress.com/)

## 💻 Development

### Running in Debug Mode

Set `FLASK_DEBUG=True` in your `.env` file for automatic reloading and detailed error pages.

### Code Structure

The application follows the **Application Factory Pattern** with Blueprints:

- **Main Blueprint** (`main_bp`): General pages (home, about)
- **Products Blueprint** (`products_bp`): Product-related functionality

### Adding New Features

1. Create new routes in `app/routes.py`
2. Add templates in `templates/`
3. Update models in `models.py` if needed
4. Create migrations: `flask db migrate -m "Description"`
5. Apply migrations: `flask db upgrade`

### Testing

```bash
# Run tests (when test suite is added)
pytest

# Check code style
flake8 app/

# Format code
black app/
```

## 🚢 Deployment

### Heroku Deployment

1. Create a `Procfile`:
```
web: gunicorn app:app
```

2. Create `runtime.txt`:
```
python-3.11.0
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
heroku run flask db upgrade
```

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t braaibites .
docker run -p 5000:5000 --env-file .env braaibites
```

### Production Checklist

- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up HTTPS/SSL
- [ ] Configure proper logging
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

## 🐛 Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'dotenv'**
```bash
pip install python-dotenv
```

**2. Database not found**
```bash
flask db upgrade
```

**3. AliExpress API errors**
- Verify your API credentials in `.env`
- Check that your App Key and Secret are correct
- Ensure you're using the correct API endpoint (sandbox vs production)

**4. Port already in use**
```bash
# Change port in app.py or use:
flask run --port 5001
```

**5. Template not found**
- Ensure templates are in the `templates/` directory
- Check file names match exactly (case-sensitive)

### Logs

Application logs are written to:
- Console (development)
- `app.log` file (production)

Check logs for detailed error information:
```bash
tail -f app.log
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask framework and community
- AliExpress Open Platform
- All contributors and testers

## 📞 Contact

For questions or support, please contact:
- Email: support@braaibitesbeverages.com
- Website: https://braaibitesbeverages.com

## 🔗 Useful Links

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [AliExpress API Docs](https://developers.aliexpress.com/)

---

Made with ❤️ for the braai community
