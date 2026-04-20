# Entre Nós — Achados e Perdidos do Campus

O Entre Nós aproxima quem perdeu um objeto de quem o encontrou. A comunidade pode consultar avisos, compartilhar informações sobre os itens e combinar a devolução.

**Prévia visual:** [entre-nos no GitHub Pages](https://ottavioaraujo.github.io/entre-nos-achados-if/). Esta página apresenta o visual do projeto; os cadastros e a gestão ficam nas aplicações Django.

## Demonstração

A pasta [`achados-if-demo`](achados-if-demo/) contém uma versão independente para apresentar e experimentar o portal. Ela vem com itens e fotos de exemplo, além de acessos de teste para conhecer a área do usuário e o painel administrativo.

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
