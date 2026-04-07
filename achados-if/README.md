# Entre Nós — Achados e Perdidos do Campus

Portal de achados e perdidos do campus, feito em Django com MySQL. A landing page é a entrada do site; o mural público permite consultar e cadastrar itens sem conta em um formulário pop-up. O acesso SUAP segue disponível para usuários que querem acompanhar os próprios avisos; administradores têm um painel para moderar os registros.

## Estrutura

```text
achados-if/
├── config/                 # settings e URLs do projeto Django
├── db/schema.sql           # cria o schema base para MySQL Workbench
├── media/items/            # fotos enviadas, criadas em runtime
├── portal/                 # modelos, formulário, views e admin
│   ├── migrations/
│   ├── static/portal/      # CSS
│   └── templates/portal/   # mural, área do aluno e painel de gestão
├── manage.py
├── prototype-static.html  # versão HTML anterior, sem backend Django
├── requirements.txt
└── .env.example
```

## Banco MySQL / MySQL Workbench

1. Inicie o MySQL local e abra `db/schema.sql` no MySQL Workbench.
2. Execute o script para criar o banco `entre_nos`.
3. Copie `.env.example` para `.env` e preencha usuário, senha e host de conexão. Para XAMPP, confira se o serviço MySQL está ativo e ajuste as credenciais conforme sua instalação.
4. O Django usa o driver `mysqlclient`. Instale dependências e aplique as migrations para criar as tabelas:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abra `http://127.0.0.1:8000/`. A aplicação cria a tabela `portal_campusitem` por migration. O arquivo SQL só cria o schema; mantenha o esquema das tabelas sob controle das migrations do Django.

**Não abra `portal/templates/portal/index.html` diretamente como arquivo (`file://`).** Ele é um template Django: `{% static %}` precisa ser processado pelo servidor para apontar para `/static/portal/site.css`. Inicie o projeto com `python manage.py runserver` e acesse o endereço acima.

Para executar sem um servidor MySQL disponível, defina `DB_ENGINE=sqlite` no `.env`; o Django usará um banco local `db.sqlite3`. Sem essa opção, o projeto usa MySQL por padrão.

## Login SUAP e painel de gestão

O login usa OAuth2 Authorization Code, seguindo a configuração indicada pelo [cliente Django oficial do IFRN](https://github.com/ifrn-oficial/cliente_suap_django). Cadastre uma aplicação confidencial na [área de APIs do SUAP do IFRN](https://suap.ifrn.edu.br/api/), habilite o grant `Authorization Code` e cadastre exatamente esta URL de retorno: `http://127.0.0.1:8000/auth/suap/callback/`. Depois preencha em `.env`:

```env
SUAP_BASE_URL=https://suap.ifrn.edu.br
SUAP_CLIENT_ID=seu-client-id
SUAP_CLIENT_SECRET=seu-client-secret
SUAP_REDIRECT_URI=http://127.0.0.1:8000/auth/suap/callback/
SUAP_ADMIN_IDS=matricula1,matricula2
```

O `client_secret` deve ficar somente no `.env` local, que não é versionado. Após entrar, alunos e servidores podem publicar e acompanhar os próprios avisos em `/conta/`. Apenas as matrículas listadas em `SUAP_ADMIN_IDS` (ou superusuários Django) acessam `/gestao/`, onde podem filtrar, editar, resolver, reabrir e excluir avisos. O access token do SUAP é usado para validar o perfil e não é persistido.

## O que vai para o MySQL

`CampusItem` guarda tipo (perdido/encontrado), nome, categoria, data, local, descrição, telefone, caminho da foto, estado de resolução e data de criação. O arquivo da foto fica em `media/`; o MySQL armazena apenas o caminho.

Campos principais da tabela `portal_campusitem`:

| Campo | Tipo | Uso |
|---|---|---|
| `kind` | `varchar(8)` | `lost` ou `found` |
| `name` | `varchar(70)` | Nome do objeto |
| `category` | `varchar(24)` | Categoria escolhida |
| `event_date` | `date` | Dia aproximado em que foi perdido/encontrado |
| `location` | `varchar(80)` | Local no campus |
| `description` | `varchar(300)` | Detalhes do aviso |
| `contact_phone` | `varchar(20)` | WhatsApp com DDD |
| `photo` | `varchar(100)` | Caminho em `media/`, a imagem fica no disco |
| `reporter_id` | `bigint` | Conta SUAP local que publicou, vazio para registros antigos |
| `is_resolved` | `boolean` | Oculta avisos resolvidos do mural |
| `created_at` | `datetime` | Data de publicação |

## WhatsApp

O número é validado e normalizado para código do país + DDD. `CampusItem.whatsapp_url` monta um link `wa.me` com mensagem específica de item perdido ou encontrado. A pessoa ainda confirma e envia a mensagem no WhatsApp.

## Acesso às páginas

- `/` — landing page.
- `/mural/` — consulta pública e cadastro de avisos sem conta.
- `/itens/publicar/` — envio do formulário pop-up de item perdido ou encontrado.
- `/auth/suap/login/` — entrada pela conta institucional do SUAP.
- `/conta/` — cadastro e acompanhamento dos próprios avisos, para usuários autenticados.
- `/gestao/` — painel administrativo restrito às matrículas autorizadas.
- `/admin/` — administração padrão do Django para superusuários e equipe autorizada.

Antes de publicar em produção, configure HTTPS, mantenha `SECRET_KEY` e credenciais fora do repositório e defina a lista `SUAP_ADMIN_IDS` com as matrículas autorizadas.
