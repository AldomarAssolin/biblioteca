# Servidor Python da Biblioteca Digital (Hostinger VPS)

Este é o motor do seu aplicativo escrito 100% em **FastAPI (Python)**. Ele é quem faz todo o trabalho pesado de Login, Proteção com JWT, Rotaamento e Armazenamento Físico de PDFs no disco.

## Como colocar a "Opção 1" para funcionar na sua VPS:

### Passo 1: Transferir os Arquivos Históricos
1. Mova esta pasta inteira (`backend_build`) para a sua VPS da Hostinger (`python.manexlabs.dev`).
2. Entre na pasta do React (`app_build`) no seu computador e rode o comando:
   ```bash
   npm run build
   ```
3. O comando acima irá gerar uma pasta chamada `dist`. Copie essa pasta `dist` inteira e jogue-a dentro da sua antiga pasta `app_build` (ao lado de `backend_build` na VPS). O FastAPI vai detectar a pasta filha e servir o React perfeitamente!

### Passo 3: Iniciar o Contêiner com Traefik
Vá até a sua VPS, entre na pasta `hostinger_deploy` recém transferida e simplesmente inicie a máquina:
```bash
docker compose up -d
```

O Docker criará automaticamente o ambiente limpo do Python isolado e o seu **Traefik** baterá o olho no contêiner com label `biblioteca.manexlabs.dev`, pegando o roteamento dele automaticamente no mesmo segundo!

*(Atenção: Revise apenas se no arquivo `docker-compose.yml` o nome da `network` bate com a rede externa que seu Traefik usa - geralmente chama 'traefik' ou 'proxy' ou 'web')*

Pronto! Ao acessar o seu domínio, o FastAPI servirá o visual do React que bate no próprio FastAPI para buscar e carregar os livros! O Sistema SQLite (`library.db`) será criado automaticamente no primeiro acesso.
