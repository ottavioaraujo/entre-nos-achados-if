# Entre Nós — Achados e Perdidos do Campus

O Entre Nós aproxima quem perdeu um objeto de quem o encontrou. A comunidade pode consultar avisos, compartilhar informações sobre os itens e combinar a devolução.

**Site real:** [entre-nos-achados-if.vercel.app](https://entre-nos-achados-if.vercel.app/).

**Prévia visual:** [Entre Nós no GitHub Pages](https://ottavioaraujo.github.io/entre-nos-achados-if/). A prévia apresenta o visual; cadastros e gestão ficam nas aplicações Django.

## Demonstração

A pasta [`achados-if-demo`](achados-if-demo/) contém uma versão independente para apresentar e experimentar o portal. Ela vem com itens e fotos de exemplo, além de acessos de teste para conhecer a área do usuário e o painel administrativo.

### Executar a demonstração localmente

No macOS ou Linux, abra um terminal na pasta do repositório e execute:

```bash
cd achados-if-demo
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_demo
python manage.py runserver 127.0.0.1:8001
```

No Windows, use o PowerShell:

```powershell
cd achados-if-demo
py -m venv .venv
.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_demo
python manage.py runserver 127.0.0.1:8001
```

Abra [http://127.0.0.1:8001/](http://127.0.0.1:8001/) para ver a apresentação. O mural fica em `/mural/` e o acesso de teste em `/auth/teste/`.

Na demonstração local, use:

| Perfil | Usuário | Senha |
|---|---|---|
| Administração | `admin` | `1234` |
| Usuário | `user` | `1234` |

Esses acessos são apenas para a demonstração local; não pertencem ao SUAP nem ao sistema real.

## Projeto real

A pasta [`achados-if`](achados-if/) contém a aplicação principal. Ela integra o login institucional do SUAP IFRN e oferece recursos de consulta e gestão dos avisos para a comunidade do campus.

O projeto inclui:

- avisos de itens perdidos e encontrados;
- mural com busca e filtros por categoria e tipo;
- fotos dos objetos e contato por WhatsApp;
- área de gestão para acompanhar e atualizar avisos.

## Tecnologias

As aplicações usam Django e têm configurações e dados independentes: a demonstração serve para apresentação e testes locais, enquanto o projeto principal integra a autenticação institucional do SUAP.
