from src import create_app
import os

app = create_app()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000), debug=True)
