def application(environ, start_response):
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        import sys
        status = '200 OK'
        output = f'FLASK OK!\nPython: {sys.executable}\nFlask: {Flask.__version__}'.encode()
    except Exception as e:
        status = '500 Internal Server Error'
        output = f'ERROR: {type(e).__name__}: {e}\nPython: {sys.executable}'.encode()
    
    response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]