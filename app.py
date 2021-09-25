import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging, os, sys

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUSECloudNativeApp'
app.config['DB_CONNECTION_COUNT'] = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    app.config['DB_CONNECTION_COUNT'] += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post



# Define Healthcheck endpoint
@app.route('/healthz')
def healthchecks():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status = 200,
        mimetype='application/json'
    )
    app.logger.info('HealthCheck request successful!')
    return response

# Define Metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    response =  app.response_class(
        response=json.dumps({
            "status":"success", "code": 0, "data": {
                "db_connection_count":app.config['DB_CONNECTION_COUNT'],
                "post_count": len(posts)
            }
        }),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Metrics request successful!')
    return response




# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()

    app.logger.info('TechTrends started successfully!')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error('Article {} not found'.format(post_id))
        return render_template('404.html'), 404
    else:
        app.logger.info('Article "{}" retrieved!'.format(post["title"]))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The "About Us" page is retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info('Article "{}" created succesfully!'.format(title))
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    #Set up logger
    logger = logging.getLogger("techtrends_logs")
    #Set loglevel to an Environment Variable
    loglevel = os.getenv("TECHTRENDS_LOGLEVEL", "DEBUG").upper()

    #Set logging output type dynamically depending on loglevel condition
    loglevel = (
        getattr(logging, loglevel)
        if loglevel in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING"]
        else logging.DEBUG
        )

    # Set logger to handle STDOUT and STDERR
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(loglevel)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    handlers = [stdout_handler, stderr_handler]

    # format output
    log_format = '%(levelname)s:%(name)s - - %(asctime)s %(message)s'

    logging.basicConfig(level=logging.DEBUG,
        format=log_format,  datefmt='%m/%d/%Y %I:%M:%S %p',  handlers=handlers
    )
   
   
    app.run(host='0.0.0.0', port='3111')
