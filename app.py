from app import create_app

if __name__ == '__main__':
    
    app = create_app()
    app.run(debug=True, port=5000)  # Acessível localmente e na porta 5000