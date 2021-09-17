from bottle import route, run, request

xss_body = '''<html>
<head>
    <script>
        xss=false;
        function vuln(value) {{ xss=value; }}
        function alert(value) {{ xss=true; }}
    </script>
</head>
<body>
    {0}

    <a href={0}>link</a>

    <img src={0}>


    <script>
        // fire all event listeners .. only works in devtools
        /*for (let elem of document.body.getElementsByTagName("*")) {{
            var events=getEventListeners(elem);
            Object.values(events).forEach(function(e) {{
                e[0].listener()
            }})
        }}*/
    </script>
</body>
</html>
'''

@route('/xss')
def xss():
    return xss_body.format( request.GET.get('a', '').strip() )

run(host='0.0.0.0', port=8001, debug=True)
