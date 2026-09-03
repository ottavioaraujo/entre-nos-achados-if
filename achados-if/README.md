# Entre Nós — Achados e Perdidos do Campus

O **Entre Nós** aproxima estudantes e servidores que perderam ou encontraram objetos no campus do IFRN. A comunidade pode consultar o mural, publicar avisos e combinar a devolução dos itens.

**Acessar o site:** [entre-nos-achados-if.vercel.app](https://entre-nos-achados-if.vercel.app)

## O projeto publicado

O site público é a aplicação oficial do projeto, desenvolvida em Django. O mural pode ser consultado e os avisos podem ser publicados sem criar uma conta. O acesso SUAP permite acompanhar os próprios registros, e a equipe autorizada dispõe de um painel de gestão.

Entre os recursos disponíveis estão:

- avisos de itens perdidos e encontrados com foto, local e período aproximado;
- busca e filtros por categoria e tipo de aviso;
- página própria para cada anúncio, com foto em destaque e comentários;
- contato por WhatsApp com mensagem inicial preenchida;
- autenticação institucional do SUAP e painel de gestão restrito;
- layout adaptado para computadores e celulares.

## Demonstração

Há também uma cópia independente para apresentações, com banco local, itens de exemplo, fotos e acesso de teste. Essa demonstração não usa o SUAP nem compartilha o banco ou os registros do site publicado. O endereço acima sempre abre o projeto real.

## Tecnologias

- Python e Django
- MySQL compatível com TiDB
- OAuth2 do SUAP para autenticação institucional
- Vercel para publicação

## Estrutura do projeto

```text
config/                     Configuração e rotas Django
db/schema.sql               Estrutura inicial do banco MySQL
portal/                     Modelos, formulários, views e painel administrativo
portal/migrations/          Migrações do banco
portal/static/portal/       CSS, JavaScript e imagens do site
portal/templates/portal/    Páginas e componentes Django
seo/                        Arquivos de indexação e descoberta do site
manage.py                   Utilitário de gerenciamento Django
```

## Páginas principais

- `/` — apresentação do projeto;
- `/mural/` — busca e publicação de avisos;
- `/itens/<id>/` — detalhes, foto e comentários de um anúncio;
- `/conta/` — área de quem entrou com SUAP;
- `/gestao/` — painel de gestão para contas autorizadas.
