# Entre Nós — Achados e Perdidos do Campus

Portal Django para publicar, consultar e administrar avisos de itens perdidos e encontrados no campus.

Prévia no GitHub Pages: <https://ottavioaraujo.github.io/entre-nos-achados-if/>.

## Pastas

- `achados-if/`: aplicação principal com autenticação SUAP e painel de gestão.
- `achados-if-demo/`: demonstração local independente, com itens e fotos de exemplo.
- `docs/`: prévia visual estática usada pelo GitHub Pages. Ela não salva cadastros nem substitui o Django.

Os dois projetos Django têm dependências, configurações e bancos separados. Arquivos `.env`, bancos SQLite, uploads e ambientes virtuais ficam fora do Git.

## GitHub Pages

O Pages publica apenas `docs/`. Após criar o repositório, em **Settings → Pages**, escolha **GitHub Actions** como fonte. O workflow `.github/workflows/pages.yml` publica a prévia a cada atualização da pasta `docs/`.

O GitHub Pages serve arquivos estáticos; por isso a prévia não oferece login, banco, formulário funcional ou painel administrativo. A aplicação Django deve ser hospedada em um serviço que execute Python, como a Vercel.

## Preparar a aplicação principal na Vercel

Importe este repositório e defina a pasta raiz do projeto como `achados-if`. A detecção de Django/Python da Vercel cuida do roteamento e dos arquivos estáticos; não é necessário um `vercel.json` personalizado.

Configure os valores abaixo em **Project Settings → Environment Variables**. Não publique valores secretos no repositório.

```text
SECRET_KEY=<chave aleatória longa>
DEBUG=False
ALLOWED_HOSTS=.vercel.app,seu-dominio
CSRF_TRUSTED_ORIGINS=https://seu-projeto.vercel.app,https://seu-dominio
DB_ENGINE=mysql
DB_NAME=<nome do banco MySQL externo>
DB_USER=<usuário do banco>
DB_PASSWORD=<senha do banco>
DB_HOST=<servidor do banco>
DB_PORT=3306
SUAP_BASE_URL=https://suap.ifrn.edu.br
SUAP_CLIENT_ID=<client id>
SUAP_CLIENT_SECRET=<client secret>
SUAP_REDIRECT_URI=https://seu-projeto.vercel.app/auth/suap/callback/
SUAP_ADMIN_IDS=<matrículas separadas por vírgula>
```

Crie o banco MySQL em um provedor externo e aplique as migrações com `python manage.py migrate` usando essas credenciais antes de usar o site. Cadastre a URL pública de retorno no SUAP IFRN.

As fotos enviadas por usuários ainda usam armazenamento local. Em funções serverless, arquivos locais não são armazenamento persistente; antes de aceitar cadastros com fotos em produção, configure um serviço durável de objetos e conecte-o ao Django. As fotos de exemplo da pasta `portal/static/` são arquivos estáticos e podem ser servidas pela CDN.

### Demonstração

Para publicar a demonstração em vez da versão SUAP, selecione `achados-if-demo` como pasta raiz na Vercel. Ela usa SQLite por padrão apenas para desenvolvimento local e o login de teste fica desativado quando `DEBUG=False`. Configure um banco MySQL externo e contas administrativas reais para uso hospedado.

## Desenvolvimento local

Em cada pasta de projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Na demonstração, execute também `python manage.py setup_demo` e use a porta 8001. Nunca adicione `.env` ao Git; mantenha os segredos apenas no arquivo local ou no painel de ambiente da hospedagem.
