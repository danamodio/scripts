from bottle import route, run, request

xss_body = '''<html>
<body>
    {0}
</body>
</html>
'''

@route('/xss')
def xss():
    return xss_body.format( request.GET.get('a', '').strip() )

run(host='127.0.0.1', port=8001, debug=True)
