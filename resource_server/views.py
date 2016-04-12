from resource_server import app


@app.route('/api/doit', methods=['POST'])
def doit():
    pass


@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    pass
