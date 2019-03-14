from Pathways.app import app
from Pathways.utils import Utils

if __name__ == '__main__':
    INITIATE = True
    app.run_server(debug=True, host='localhost')
    U = Utils()
    if INITIATE:
        U.initDB()