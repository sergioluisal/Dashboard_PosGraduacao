import os
from flask import Flask

# Importa as páginas (Blueprints)
from pages.page1 import page1_bp
from pages.page2 import page2_bp
from pages.page3 import page3_bp
from pages.page4 import page4_bp
from pages.page5 import page5_bp
from pages.page6 import page6_bp

app = Flask(__name__)

# Registra as páginas no servidor Flask
app.register_blueprint(page1_bp)
app.register_blueprint(page2_bp)
app.register_blueprint(page3_bp)
app.register_blueprint(page4_bp)
app.register_blueprint(page5_bp)
app.register_blueprint(page6_bp)

if __name__ == "__main__":
    # Render injeta a porta dinamicamente através de variáveis de ambiente.
    port = int(os.environ.get("PORT", 5000))
    # 0.0.0.0 permite conexões externas no ambiente em nuvem
    app.run(host="0.0.0.0", port=port, debug=False)
