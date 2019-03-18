from Pathways.app import app
from Pathways.utils import Utils

if __name__ == '__main__':
    INITIATE = True
    app.run_server(debug=False)
    U = Utils()
    if INITIATE:
        U.initDB()