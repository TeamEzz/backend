# test_login.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_login_tradicional():
    """Verifica que el endpoint /auth/login responde correctamente"""
    data = {
        "email": "usuario@ejemplo.com",  # usa un correo real registrado
        "password": "123456"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=data)

    print("📥 Código de estado:", response.status_code)
    print("📦 Respuesta JSON:", response.text)

    assert response.status_code == 200, "❌ El login no devolvió 200"
    json_data = response.json()
    assert "token" in json_data, "❌ No se encontró el token en la respuesta"
    assert "id" in json_data, "❌ Falta el ID del usuario"

if __name__ == "__main__":
    test_login_tradicional()
    print("✅ Test de login completado correctamente")
