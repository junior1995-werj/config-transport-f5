## Transport config F5

Este repositório visa concentrar código e documentos voltados à migração de configurações de balanceadores BIG-IPs.

##

### Informações básicas para uso do framework

###### 1. Requisitos:

- Versão mínima requerida do python: v3.11.0;
- Necessário o pacote `poetry` para virtualização do ambiente e;
- Para testes locais, a base de dados `PostgreSQL`.

<br>

###### 2. Instalação do projeto para contribuições no desenvolvimento:
- Necessário clonar o projeto localmente:

```shell
git clone git@gitlab.devops.somosagility.com.br:f5/transport-config-f5.git
```

- Para instalar as dependências:

```shell
poetry install
```

- Para ativar a virtual env:

```shell
poetry shell
```

- Atualizar as env vars:

```shell
cp local.env .env
```

- Atualizar a senha e usuário do `PostgreSQL` no arquivo .env.

- Criar uma nova branch, referente à task que será executada:
```shell
git checkout -b "nome-da-branch"
```

- Realizar o `pull` do projeto, para não sobrepor alterações já realizadas:
```shell
git pull
```

- Tendo realizado os devidos incrementos em códigos/documentos, fazer o stage das alterações com um dos dois comandos a seguir:
```shell
# Adiciona todos os arquivos alterados e criados:
git add .

# Adiciona um arquivo específico:
git add "nome-do-arquivo"
```

- E, após realizar o staging das alterações, commitar:
```shell
git commit -m "Mensagem genérica."
```

- Realizar o `push` do projeto com as devidas alterações para master/main:
```shell
git push
```

##

### Informações gerais da aplicação

###### 1. Link de acesso:

http://192.168.50.3:31779/

###### 2. Versionamento da aplicação:
Versão atual: v1.0.0.
