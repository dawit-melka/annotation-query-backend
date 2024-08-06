from app import app

if __name__ == '__main__':
    print("am running")
    app.run(debug=True, host='0.0.0.0', port=5000)
