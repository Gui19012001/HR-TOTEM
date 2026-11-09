# IBERO ATENDE · Painel RH Cloud

Painel inicial em Streamlit para a equipe de RH receber e aceitar pedidos de atendimento do totem. Interface em português, perfil com foto, disponibilidade, fila e cartões de status.

## Publicar

1. Envie esta pasta para um repositório GitHub.
2. No Streamlit Community Cloud, crie um app apontando para `app.py`.
3. Em **Settings → Secrets**, copie os valores do arquivo `.streamlit/secrets.toml.example` e substitua pelos valores reais. Nunca publique o `secrets.toml` nem coloque chaves no código.
4. Execute `supabase_setup.sql` no SQL Editor do projeto Supabase e crie o bucket `rh-profiles` no Storage.

Se as credenciais do Supabase ainda não estiverem configuradas, o app abre em modo demonstração com pedidos de exemplo. Com Supabase configurado, lê a tabela `rh_rooms` e permite aceitar os pedidos.

## Importante para esta primeira versão

- O código de acesso `RH_ACCESS_CODE` é uma proteção provisória compartilhada, não um login individual. Defina-o em Secrets e distribua somente à equipe autorizada.
- O app ainda não faz a chamada de vídeo/chat com o totem. Esta etapa prepara a central do RH; a próxima conecta o totem aos mesmos pedidos e cria a sala temporária.
- Não há gravação de áudio ou vídeo. A tabela mantém apenas metadados da solicitação ativa; configure a limpeza indicada no SQL.
- A foto precisa do bucket de Storage `rh-profiles` configurado para upload. Para produção, restrinja as políticas de escrita e acesso às fotos.
