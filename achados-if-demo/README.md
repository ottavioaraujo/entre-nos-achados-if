# Entre Nós — demonstração

Cópia independente para apresentar e testar o portal de achados e perdidos. Tem banco SQLite próprio, contas locais de demonstração e itens de exemplo. Não depende do SUAP nem reutiliza o banco ou as credenciais do projeto principal.

## Iniciar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_demo
python manage.py runserver 127.0.0.1:8001
```

Abra `http://127.0.0.1:8001/` para a landing page. O mural separado fica em `/mural/`; a tela de acesso de teste está em `/auth/teste/`.

## Contas locais

| Perfil | Usuário | Senha | Destino após entrar |
|---|---|---|---|
| Gestão | `admin` | `1234` | Painel de gestão |
| Usuário | `user` | `1234` | Área do usuário |

As contas são criadas pelo comando `setup_demo` e também podem ser inicializadas na primeira tentativa de login. O atalho de teste e a rota de login só funcionam com `DEBUG=True`.

## Itens e fotos

O comando cria seis avisos de exemplo; quatro já têm as fotos originais dos itens. A foto da comunidade também aparece como imagem principal da landing page. Os avisos usam um telefone fictício inválido para que os botões de WhatsApp não contatem pessoas reais. As imagens ficam em `portal/static/portal/demo-items/`; o comando `setup_demo` copia as fotos dos itens para `media/items/demo/`.

As imagens carregadas ficam em `media/items/`; o banco SQLite fica em `db.sqlite3`. Ambos pertencem somente a esta pasta.

## Funcionalidades incluídas

- mural público separado da landing page, com busca, filtros e cartões de itens;
- cadastro de itens perdidos e encontrados sem conta, pelo formulário pop-up com foto e WhatsApp;
- área do usuário para publicar e acompanhar avisos;
- painel de gestão para filtrar, editar, resolver e remover anúncios;
- banco independente e dados de demonstração reinicializáveis.

Este pacote serve para demonstração local. Não publique na internet com as senhas de teste; desative o modo de demonstração e configure autenticação adequada antes de qualquer implantação.
