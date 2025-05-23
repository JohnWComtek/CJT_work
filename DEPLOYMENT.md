# Deploying to Vercel

This guide outlines the steps to deploy the Job Tracking System on Vercel.

## Prerequisites

1. Node.js installed (required for Vercel CLI)
2. Vercel account (sign up at vercel.com)
3. Vercel CLI installed:
   ```bash
   npm i -g vercel
   ```

## Project Configuration

### 1. Create Vercel Configuration

Create a `vercel.json` file in your project root:

```json
{
    "version": 2,
    "builds": [
        {
            "src": "app.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "app.py"
        }
    ],
    "env": {
        "FLASK_ENV": "production",
        "FLASK_APP": "app.py"
    }
}
```

### 2. Create Requirements File
Ensure your `requirements.txt` is up to date:
```bash
pip freeze > requirements.txt
```

### 3. Database Configuration

For production, you'll need a proper database. We recommend using PostgreSQL:

1. Create a PostgreSQL database (you can use providers like Supabase or Railway)
2. Update `config.py` to use environment variables:

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///jobtracker.db')
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### 4. Static Files

For static file hosting, we'll use Vercel's built-in static file handling:

1. Create a `static` directory if not exists
2. Move all static assets (images, CSS, JS) to this directory
3. Update templates to use absolute paths for static files

## Deployment Steps

1. Login to Vercel CLI:
   ```bash
   vercel login
   ```

2. Initialize Vercel project:
   ```bash
   vercel init
   ```

3. Deploy the project:
   ```bash
   vercel
   ```

4. Set environment variables:
   ```bash
   vercel env add SECRET_KEY
   vercel env add DATABASE_URL
   ```

5. Deploy to production:
   ```bash
   vercel --prod
   ```

## Environment Variables

Set these environment variables in your Vercel project settings:

- `SECRET_KEY`: Your Flask secret key
- `DATABASE_URL`: Your PostgreSQL connection string
- `FLASK_ENV`: Set to 'production'
- `FLASK_APP`: Set to 'app.py'

## Database Migration

After deploying, run migrations on your production database:

1. Install Heroku CLI (for running one-off commands):
   ```bash
   npm install -g heroku
   ```

2. Run migrations:
   ```bash
   heroku run "flask db upgrade" --app your-app-name
   ```

## File Storage

For job image uploads, configure cloud storage:

1. Sign up for AWS S3 or similar service
2. Add these environment variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_BUCKET_NAME`

3. Update the image upload code to use cloud storage

## Post-Deployment Checklist

- [ ] Verify all environment variables are set
- [ ] Run database migrations
- [ ] Test user authentication
- [ ] Verify file uploads
- [ ] Check email functionality
- [ ] Test all CRUD operations
- [ ] Monitor application logs
- [ ] Set up SSL certificate (automatic with Vercel)

## Monitoring and Maintenance

1. Set up monitoring:
   - Use Vercel Analytics
   - Configure error tracking (e.g., Sentry)
   - Set up performance monitoring

2. Regular maintenance:
   - Monitor database size
   - Check application logs
   - Update dependencies
   - Backup database regularly

## Troubleshooting

Common issues and solutions:

1. Database connection issues:
   - Verify DATABASE_URL is correct
   - Check database credentials
   - Ensure database is accessible from Vercel's servers

2. Static files not loading:
   - Check file paths in templates
   - Verify static files are in the correct directory
   - Clear browser cache

3. Application errors:
   - Check Vercel logs: `vercel logs`
   - Enable debug mode temporarily
   - Check application logs

## Security Considerations

1. Enable security headers:
   ```python
   from flask_talisman import Talisman
   Talisman(app, content_security_policy=None)
   ```

2. Set secure cookie settings:
   ```python
   app.config['SESSION_COOKIE_SECURE'] = True
   app.config['SESSION_COOKIE_HTTPONLY'] = True
   ```

3. Configure CORS if needed:
   ```python
   from flask_cors import CORS
   CORS(app, resources={r"/api/*": {"origins": "*"}})
   ```

## Scaling

To handle increased load:

1. Configure caching:
   - Use Redis for session storage
   - Cache database queries
   - Implement API caching

2. Optimize database:
   - Add appropriate indexes
   - Optimize queries
   - Set up database monitoring

3. Configure auto-scaling:
   - Set up Vercel auto-scaling
   - Monitor resource usage
   - Set up alerts for high usage

## Support and Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/) 