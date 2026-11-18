"""
test_endpoints.py
-----------------
Testa a inicialização do app Flask, a rota /corridas-antigas,
a tabela de pódios, o login dos novos 3 administradores e as páginas principais.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from api.index import app
from db import get_db_connection

def run_tests():
    print("🧪 Iniciando bateria de testes do Setor F1...")

    client = app.test_client()

    # 1. Teste da página inicial (Home)
    res_home = client.get("/")
    assert res_home.status_code == 200, f"Erro ao acessar /: {res_home.status_code}"
    assert "Corridas Antigas" in res_home.get_data(as_text=True), "Link de Corridas Antigas não encontrado no menu"
    print("✅ Rota / (Home) OK!")

    # 2. Teste da nova página /corridas-antigas
    res_antigas = client.get("/corridas-antigas")
    assert res_antigas.status_code == 200, f"Erro ao acessar /corridas-antigas: {res_antigas.status_code}"
    html_antigas = res_antigas.get_data(as_text=True)
    assert "tabelaPodios" in html_antigas, "Tabela DataTables não encontrada"
    assert "datatables.net" in html_antigas or "DataTables" in html_antigas, "DataTables não referenciado"
    assert "Ver Perfil" in html_antigas, "Botão de perfil não encontrado"
    print("✅ Rota /corridas-antigas OK!")

    # 3. Teste do banco de dados de pódios
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM podios;")
    total_podios = cur.fetchone()["total"]
    assert total_podios >= 400, f"Poucos pódios: {total_podios}"
    print(f"✅ Banco de pódios OK! ({total_podios} registros)")

    # 4. Teste de login dos 3 novos admins
    admins_para_testar = [
        ("mariana@setorf1.com", "admin123", "Mariana Silva"),
        ("camila@setorf1.com", "admin123", "Camila Santos"),
        ("larissa@setorf1.com", "admin123", "Larissa Lima"),
        ("admin@setorf1.com", "admin123", "Administrador Setor F1")
    ]

    for email, senha, nome in admins_para_testar:
        with client.session_transaction() as sess:
            sess.clear()

        res_login = client.post("/login", data={
            "email": email,
            "senha": senha
        }, follow_redirects=True)

        assert res_login.status_code == 200, f"Erro no login de {email}: status {res_login.status_code}"
        with client.session_transaction() as sess:
            assert sess.get("usuario_id") is not None, f"Sessão vazia para {email}"
            assert sess.get("usuario_tipo") == "admin", f"Usuário {email} não é admin: {sess.get('usuario_tipo')}"

        # Verifica acesso ao painel admin
        res_admin = client.get("/admin")
        assert res_admin.status_code == 200, f"Admin não conseguiu acessar /admin: {email}"
        print(f"✅ Login e acesso ao painel Admin OK para {nome} ({email})!")

    # 5. Teste da página de pilotos e perfil
    cur.execute("SELECT id, nome FROM pilotos LIMIT 1;")
    primeiro_piloto = cur.fetchone()
    if primeiro_piloto:
        res_piloto = client.get(f"/piloto/{primeiro_piloto['id']}")
        assert res_piloto.status_code == 200, f"Erro ao acessar /piloto/{primeiro_piloto['id']}"
        print(f"✅ Perfil do piloto {primeiro_piloto['nome']} (/piloto/{primeiro_piloto['id']}) OK!")

    cur.close()
    conn.close()

    print("\n🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")

if __name__ == "__main__":
    run_tests()
