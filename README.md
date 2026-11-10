# IBERO ATENDE · Painel RH Cloud

Painel Streamlit com cadastro individual, e-mail e senha, perfil com foto e aprovação pelo administrador.

## Como funciona o acesso

1. A atendente cria a conta com nome, e-mail e senha.
2. O Supabase Auth cria a conta e armazena a senha de forma protegida (o app e o administrador não recebem nem exibem a senha).
3. O perfil entra com status **pendente**; a atendente confirma o e-mail se a confirmação estiver habilitada.
4. Um administrador aprova ou rejeita o cadastro pela seção **Administração de acessos**.
5. Depois de aprovada, a atendente entra, ajusta o nome e envia sua foto.

## Configuração inicial

1. No Supabase, execute `supabase_setup.sql`.
2. Crie o primeiro usuário administrador pelo formulário de cadastro, confirme o e-mail e use o trecho indicado no SQL para promovê-lo a `admin` e `approved`.
3. Crie no Storage o bucket público de leitura `rh-profiles`. O app transforma as fotos em JPG otimizado; se configurar tipos permitidos no bucket, permita `image/jpeg` e confira o limite de tamanho.
4. Em **Settings → Secrets** do Streamlit Cloud, copie os três valores de `.streamlit/secrets.toml.example` com as chaves reais do projeto.
5. No Supabase Auth, habilite confirmação de e-mail para os novos cadastros.
6. Envie esta pasta ao GitHub e crie um app no Streamlit Community Cloud apontando para `app.py`.

Mantenha `SUPABASE_SERVICE_ROLE_KEY` somente nos Secrets do Streamlit Cloud. Nunca publique essa chave no GitHub. O app pode ficar acessível pela URL do Streamlit: quem não estiver aprovado só verá a tela de pendência e não terá acesso à fila.

## Totem IBERO CONECTA

A tela pública do totem fica em `https://hriberototem.streamlit.app/?modo=totem`. Ela não pede login do atendente e não expõe a chave privada no navegador. O totem envia um chamado temporário ao Supabase; o painel RH recebe e aceita pela fila. Após a aceitação, **Abrir sala** conecta um chat ao vivo entre o totem e o atendente usando Supabase Realtime Broadcast. As mensagens são transmitidas entre os navegadores e não são inseridas em tabela nem mantidas como histórico; a sala usa um token aleatório temporário.

O upload do perfil envia uma imagem JPG redimensionada. Se o Supabase recusar, o painel mostra o código e a mensagem devolvidos pelo Storage para identificar se o problema é no bucket, no tipo de arquivo ou nos limites configurados.

Para integrar o fluxo existente do IBERO CONECTA, aplique o patch mais recente do totem sobre a pasta do sistema. As opções já existentes de chat, voz e vídeo encaminham para o RH Cloud na mesma guia, levando a preferência escolhida. A tela Cloud oferece **Voltar ao IBERO CONECTA** para retornar ao totem. O totem precisa ter acesso HTTPS à internet; o RH acessa o painel Streamlit Cloud.

A sala aberta aparece logo abaixo dos indicadores no painel RH. No totem, a tela fica compacta durante o atendimento para manter a conversa acessível sem rolagem. As mensagens usam transmissão em tempo real e não são gravadas pelo app.

Quando o colaborador escolhe **Videochamada**, RH e colaborador devem tocar em **Ativar câmera e microfone** e permitir o acesso no navegador. O vídeo usa WebRTC com STUN para tentar conexão direta entre os dois dispositivos. Redes com firewall restritivo podem exigir um servidor TURN configurado; nesses casos, a tela mostra o estado ou o erro da conexão. A opção **Voz** sem vídeo ainda não está habilitada. Não há gravação de áudio ou vídeo.

## Atualização da sala de chat

No Supabase SQL Editor, execute novamente `supabase_setup.sql` para adicionar a coluna `room_token` à tabela `rh_rooms` existente. A alteração é aditiva e preserva os chamados. Depois atualize o repositório GitHub com os arquivos deste pacote e aguarde o Streamlit Cloud publicar.

## Confirmação de e-mail

No Supabase, em **Authentication → URL Configuration**, defina o **Site URL** como `https://hriberototem.streamlit.app` e inclua esse mesmo endereço em **Redirect URLs**. A confirmação não deve redirecionar para `localhost`. Depois de alterar a configuração, a pessoa deve usar **Reenviar e-mail de confirmação** no app; links antigos expirados não são recuperados.
