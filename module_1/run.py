"""
Ben L - 8.29.25
The run file to start the website.  The site is build using a package structure, so first import the app from the
package, then run the app.
I am hosting on 0.0.0.0 and port 8080
"""
from personal_website import app

if __name__ == '__main__':
    #Running with debug on, host = 0.0.0.0 and port = 8080
    app.run(debug=True, host= '0.0.0.0', port=8080)