import os
from html import escape
from datetime import datetime
from typing import Any

import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="IBERO ATENDE · RH", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--bg:#07111f;--panel:#0d1c2d;--panel2:#10243a;--line:rgba(132,178,218,.16);--cyan:#5ce1e6;--blue:#54a8ff;--muted:#91a6bc;--white:#f3f8fc;--green:#53dfb0;--amber:#ffc46b}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--white)}
.stApp{background:radial-gradient(ellipse at 85% 2%,rgba(33,113,157,.19),transparent 30%),radial-gradient(ellipse at 5% 60%,rgba(19,80,116,.12),transparent 28%),var(--bg)}
.block-container{padding:1.35rem 2.2rem 2rem;max-width:1600px}
header[data-testid="stHeader"]{background:transparent}
#MainMenu,footer{visibility:hidden}
.brand{font:700 1.08rem 'Space Grotesk';letter-spacing:.14em;color:#e9f6ff}
.brand span{color:var(--cyan)}
.eyebrow{font-size:.68rem;letter-spacing:.18em;text-transform:uppercase;color:var(--cyan);font-weight:700}
.hero-title{font:600 clamp(1.9rem,3.2vw,3.15rem) 'Space Grotesk';letter-spacing:-.045em;line-height:1.06;margin:.35rem 0 .45rem}
.subtle{color:var(--muted);font-size:.92rem}
.glass{background:linear-gradient(145deg,rgba(18,39,62,.94),rgba(10,24,40,.94));border:1px solid var(--line);border-radius:20px;padding:20px 22px;box-shadow:0 16px 44px rgba(0,0,0,.18)}
.metric-label{color:#9cb2c8;font-size:.74rem;letter-spacing:.1em;text-transform:uppercase}
.metric-value{font:600 1.8rem 'Space Grotesk';margin-top:.3rem}
.metric-note{font-size:.75rem;color:#89a2b9;margin-top:.15rem}
.section-title{font:600 1.15rem 'Space Grotesk';margin:0 0 .25rem}
.pill{display:inline-flex;align-items:center;gap:7px;border:1px solid rgba(83,223,176,.25);background:rgba(83,223,176,.09);color:var(--green);padding:7px 11px;border-radius:999px;font-size:.77rem;font-weight:700}
.pill.off{border-color:rgba(145,166,188,.2);background:rgba(145,166,188,.07);color:#aab9c8}
.ticket{background:linear-gradient(140deg,rgba(19,43,67,.94),rgba(13,29,47,.96));border:1px solid var(--line);border-radius:16px;padding:17px 18px;margin:10px 0}
.ticket-top{display:flex;justify-content:space-between;align-items:center;gap:12px}
.ticket-name{font:600 1rem 'Space Grotesk'}
.ticket-type{font-size:.69rem;letter-spacing:.08em;text-transform:uppercase;color:var(--cyan);font-weight:700}
.ticket-text{color:#a9bdd0;font-size:.86rem;line-height:1.45;margin:.65rem 0}
.ticket-meta{color:#7892a9;font-size:.74rem}
.profile-name{font:600 1rem 'Space Grotesk';margin-top:5px}.profile-role{font-size:.76rem;color:var(--muted)}
.profile-wrap{display:flex;align-items:center;justify-content:flex-end;gap:12px}
.orb{width:43px;height:43px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(135deg,#44d7df,#527cff);color:#061423;font:700 1rem 'Space Grotesk';box-shadow:0 0 25px rgba(68,215,223,.25)}
.stButton>button{border-radius:11px;border:1px solid rgba(91,175,226,.35);background:linear-gradient(135deg,#147a96,#2865b0);color:white;font-weight:700;min-height:43px;transition:.2s}
.stButton>button:hover{border-color:var(--cyan);box-shadow:0 0 18px rgba(92,225,230,.2);color:white}
.stTextInput input,.stTextArea textarea{background:#09192a;border:1px solid var(--line);border-radius:10px;color:#f3f8fc}
.stSelectbox div[data-baseweb="select"]>div{background:#09192a;border-color:var(--line);border-radius:10px;color:white}
hr{border-color:var(--line)}
div[data-testid="stImage"] img{border-radius:50%;border:2px solid rgba(92,225,230,.65);object-fit:cover}
div[data-testid="stFileUploader"]{font-size:.8rem}
@media(max-width:900px){.block-container{padding:1rem}.profile-wrap{justify-content:flex-start}.hero-title{font-size:2rem}}
</style>
""", unsafe_allow_html=True)

# ---------- Data gateway ----------
def secrets_value(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, default))
    except Exception:
        return os.getenv(name, default)

SUPABASE_URL = secrets_value("SUPABASE_URL").rstrip("/")
SUPABASE_KEY = secrets_value("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY = secrets_value("SUPABASE_ANON_KEY")
APP_URL = secrets_value("APP_URL", "https://hriberototem.streamlit.app").rstrip("/")

class Store:
    def __init__(self, url: str, key: str):
        self.url, self.key = url, key

    @property
    def headers(self):
        return {"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}

    def rows(self, table: str, query: str = "select=*") -> list[dict[str, Any]]:
        r = requests.get(f"{self.url}/rest/v1/{table}?{query}", headers=self.headers, timeout=12)
        r.raise_for_status()
        return r.json()

    def update(self, table: str, filters: str, payload: dict[str, Any]):
        h = {**self.headers, "Prefer": "return=representation"}
        r = requests.patch(f"{self.url}/rest/v1/{table}?{filters}", headers=h, json=payload, timeout=12)
        r.raise_for_status()
        return r.json()

    def upsert(self, table: str, payload: dict[str, Any], conflict: str):
        h = {**self.headers, "Prefer": "resolution=merge-duplicates,return=representation"}
        r = requests.post(f"{self.url}/rest/v1/{table}?on_conflict={conflict}", headers=h, json=payload, timeout=12)
        r.raise_for_status()
        return r.json()

    def upload_profile(self, user_key: str, content: bytes, mime: str) -> str:
        ext = "png" if "png" in mime else "jpg"
        path = f"rh/{user_key}.{ext}"
        r = requests.post(f"{self.url}/storage/v1/object/rh-profiles/{path}", headers={**self.headers, "Content-Type": mime, "x-upsert": "true"}, data=content, timeout=20)
        r.raise_for_status()
        return f"{self.url}/storage/v1/object/public/rh-profiles/{path}?v={int(datetime.now().timestamp())}"

store = Store(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ---------- Individual account in Supabase Auth ----------
if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_ANON_KEY:
    st.error("Configure SUPABASE_URL, SUPABASE_ANON_KEY e SUPABASE_SERVICE_ROLE_KEY nos Secrets do Streamlit Cloud.")
    st.stop()
store = Store(SUPABASE_URL, SUPABASE_KEY)

def auth_request(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{SUPABASE_URL}/auth/v1/{path}",
        headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
        json=payload,
        timeout=15,
    )
    data = response.json() if response.content else {}
    if not response.ok:
        message = data.get("msg") or data.get("message") or data.get("error_description") or "Falha na autenticação."
        raise ValueError(message)
    return data

def render_authentication():
    st.markdown('<div class="eyebrow">IBERO CONECTA · ACESSO RH</div><div class="hero-title">Central de atendimento</div><p class="subtle">Entre ou crie seu acesso individual usando um e-mail autorizado pela Ibero.</p>', unsafe_allow_html=True)
    sign_in, sign_up = st.tabs(["Entrar", "Cadastrar atendente"])
    with sign_in:
        with st.form("rh-login"):
            login_email = st.text_input("E-mail", autocomplete="email").strip().lower()
            login_password = st.text_input("Senha", type="password", autocomplete="current-password")
            submitted = st.form_submit_button("Entrar no painel", type="primary", use_container_width=True)
        if submitted:
            try:
                data = auth_request("token?grant_type=password", {"email": login_email, "password": login_password})
                account_email = (data.get("user") or {}).get("email", login_email).lower()
                st.session_state.rh_access_token = data["access_token"]
                st.session_state.rh_email = account_email
                st.session_state.rh_identity = (data.get("user") or {}).get("id", account_email)
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível entrar: {exc}")
    with sign_up:
        with st.form("rh-signup"):
            signup_name = st.text_input("Nome completo", max_chars=100)
            signup_email = st.text_input("E-mail", autocomplete="email").strip().lower()
            signup_password = st.text_input("Crie uma senha", type="password", max_chars=128)
            submitted_signup = st.form_submit_button("Criar meu acesso", type="primary", use_container_width=True)
        if submitted_signup:
            if not signup_name.strip() or "@" not in signup_email or len(signup_password) < 8:
                st.error("Informe nome, e-mail válido e senha com pelo menos 8 caracteres.")
            else:
                try:
                    redirect = requests.utils.quote(APP_URL, safe="")
                    data = auth_request(f"signup?redirect_to={redirect}", {"email": signup_email, "password": signup_password, "data": {"display_name": signup_name.strip()}})
                    new_user = data.get("user") or {}
                    if new_user.get("id"):
                        store.upsert("rh_staff_profiles", {
                            "email": signup_email,
                            "auth_user_id": new_user["id"],
                            "display_name": signup_name.strip(),
                            "approval_status": "pending",
                            "role": "attendant",
                            "is_available": False,
                        }, "email")
                    if data.get("access_token"):
                        st.session_state.rh_access_token = data["access_token"]
                        st.session_state.rh_email = (new_user.get("email") or signup_email).lower()
                        st.session_state.rh_identity = new_user.get("id", signup_email)
                        st.rerun()
                    else:
                        st.success("Cadastro recebido. Confirme o e-mail; depois o administrador autorizará seu acesso.")
                except Exception as exc:
                    st.error(f"Não foi possível criar o acesso: {exc}")
        resend_email = st.text_input("E-mail para reenviar a confirmação", key="resend_email", autocomplete="email")
        if st.button("Reenviar e-mail de confirmação", key="resend-confirmation"):
            if "@" not in resend_email:
                st.error("Informe o e-mail usado no cadastro.")
            else:
                try:
                    redirect = requests.utils.quote(APP_URL, safe="")
                    auth_request(f"resend?redirect_to={redirect}", {"type": "signup", "email": resend_email.strip().lower()})
                    st.success("Se houver um cadastro pendente para esse e-mail, a confirmação será enviada novamente.")
                except Exception as exc:
                    st.error(f"Não foi possível reenviar a confirmação: {exc}")
    st.stop()

if not st.session_state.get("rh_access_token"):
    render_authentication()

email = st.session_state.rh_email
identity_name = st.session_state.pop("rh_initial_name", email.split("@")[0])
identity_id = st.session_state.rh_identity
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Configure as chaves privadas do Supabase nos Secrets do Streamlit Cloud.")
    st.stop()
try:
    found_profile = store.rows("rh_staff_profiles", f"select=email,display_name,photo_url,is_available,approval_status,role&email=eq.{requests.utils.quote(email)}")
    if found_profile:
        profile = found_profile[0]
    else:
        profile = store.upsert("rh_staff_profiles", {"email": email, "auth_user_id": identity_id, "display_name": identity_name, "approval_status": "pending", "role": "attendant", "is_available": False}, "email")[0]
except Exception as exc:
    st.error("Não consegui carregar o perfil do RH. Confira a tabela rh_staff_profiles no Supabase.")
    st.caption(str(exc))
    st.stop()
st.session_state.profile = profile
st.session_state.rh_name = profile.get("display_name") or identity_name
st.session_state.profile_url = profile.get("photo_url") or ""
st.session_state.available = bool(profile.get("is_available", False))
if profile.get("approval_status") != "approved":
    if profile.get("approval_status") == "rejected":
        st.markdown('<div class="eyebrow">ACESSO NÃO LIBERADO</div><div class="hero-title">Cadastro não aprovado</div>', unsafe_allow_html=True)
        st.info("O administrador não liberou este cadastro. Procure o responsável pelo IBERO ATENDE.")
    else:
        st.markdown('<div class="eyebrow">CADASTRO RECEBIDO</div><div class="hero-title">Acesso aguardando liberação</div>', unsafe_allow_html=True)
        st.info("Seu cadastro foi criado. O administrador do IBERO ATENDE precisa aprovar o acesso antes de você receber atendimentos.")
    st.caption(f"Conta: {email} · Nome: {profile.get('display_name', identity_name)}")
    if st.button("Sair"):
        for key in ("rh_access_token", "rh_email", "rh_identity", "rh_name", "profile_url", "profile"):
            st.session_state.pop(key, None)
        st.rerun()
    st.stop()
st_autorefresh(interval=7000, key="rh_queue_refresh")

# ---------- Header / profile ----------
name = st.session_state.get("rh_name", "Atendimento RH")
profile_url = st.session_state.get("profile_url", "")
left, right = st.columns([7, 3], vertical_alignment="center")
with left:
    st.markdown('<div class="brand">IBERO <span>ATENDE</span></div><div class="subtle" style="margin-top:5px">Central de atendimento · ambiente privado</div>', unsafe_allow_html=True)
with right:
    p1, p2 = st.columns([1, 3], vertical_alignment="center")
    with p1:
        if profile_url:
            st.image(profile_url, width=48)
        else:
            st.markdown('<div class="orb">RH</div>', unsafe_allow_html=True)
    with p2:
        st.markdown(f'<div class="profile-name">{escape(name)}</div><div class="profile-role">{escape(email)}</div>', unsafe_allow_html=True)

st.markdown('<div class="eyebrow">VISÃO OPERACIONAL</div><div class="hero-title">Olá, equipe RH<span style="color:#5ce1e6">.</span></div><div class="subtle">Acompanhe a fila e fique disponível para receber o próximo contato.</div>', unsafe_allow_html=True)
st.write("")

if profile.get("role") == "admin":
    with st.expander("Administração de acessos", expanded=True):
        st.markdown("#### Cadastros aguardando aprovação")
        try:
            waiting = store.rows("rh_staff_profiles", "select=email,display_name,created_at&approval_status=eq.pending&order=created_at.asc")
            if not waiting:
                st.caption("Não há cadastros pendentes.")
            for person in waiting:
                pcol, approve_col, reject_col = st.columns([6, 1, 1], vertical_alignment="center")
                with pcol:
                    st.write(f"**{person.get('display_name','Atendente')}** · {person.get('email','')}")
                    st.caption(f"Solicitado em {str(person.get('created_at',''))[:16].replace('T',' ')}")
                with approve_col:
                    if st.button("Aprovar", key=f"approve-{person['email']}"):
                        store.update("rh_staff_profiles", f"email=eq.{requests.utils.quote(person['email'])}", {"approval_status":"approved"})
                        st.rerun()
                with reject_col:
                    if st.button("Rejeitar", key=f"reject-{person['email']}"):
                        store.update("rh_staff_profiles", f"email=eq.{requests.utils.quote(person['email'])}", {"approval_status":"rejected", "is_available":False})
                        st.rerun()
        except Exception as exc:
            st.error(f"Não foi possível carregar os cadastros: {exc}")

# Profile controls and status
control1, control2, control3 = st.columns([2, 2, 6], vertical_alignment="center")
with control1:
    available = st.toggle("Disponível para atender", value=st.session_state.available, key="availability_toggle")
    if available != st.session_state.available:
        try:
            store.update("rh_staff_profiles", f"email=eq.{requests.utils.quote(email)}", {"is_available": available})
            st.session_state.available = available
            st.rerun()
        except Exception as exc:
            st.error(f"Não foi possível atualizar sua disponibilidade: {exc}")
with control2:
    st.markdown('<span class="pill">● CONEXÃO SEGURA</span>' if store else '<span class="pill off">● MODO DEMONSTRAÇÃO</span>', unsafe_allow_html=True)
with control3:
    with st.expander("Editar foto de perfil"):
        edited_name = st.text_input("Nome de exibição", value=name, key="rh_name_input")
        upload = st.file_uploader("Escolha uma foto", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if st.button("Salvar nome", key="save-profile-name"):
            try:
                store.update("rh_staff_profiles", f"email=eq.{requests.utils.quote(email)}", {"display_name": edited_name.strip() or identity_name})
                st.session_state.rh_name = edited_name.strip() or identity_name
                st.success("Nome atualizado.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível atualizar o perfil: {exc}")
        if upload and st.button("Salvar foto", key="save-profile-photo"):
            try:
                profile_url = store.upload_profile(identity_id, upload.getvalue(), upload.type)
                store.update("rh_staff_profiles", f"email=eq.{requests.utils.quote(email)}", {"photo_url": profile_url})
                st.session_state.profile_url = profile_url
                st.success("Foto de perfil atualizada.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível salvar a foto. Confira o bucket rh-profiles: {exc}")

# Load queue or demo
DEMO = [
    {"id":"demo-01","nome":"Colaborador do Totem","tipo":"Videochamada","assunto":"Dúvida sobre benefício","descricao":"Preciso conversar com alguém do RH sobre meu benefício.","created_at":datetime.now().isoformat(),"status":"pendente"},
    {"id":"demo-02","nome":"Atendimento reservado","tipo":"Chat","assunto":"Solicitação de atendimento","descricao":"Gostaria de tirar uma dúvida em ambiente privado.","created_at":datetime.now().isoformat(),"status":"pendente"},
]
rooms, load_error = [], None
if store:
    try:
        rooms = store.rows("rh_rooms", "select=id,nome,tipo,assunto,descricao,created_at,status&status=in.(pendente,em_atendimento)&order=created_at.asc")
    except Exception as exc:
        load_error = str(exc)
else:
    rooms = DEMO if st.session_state.get("demo_queue", True) else []

# KPI cards
pending = sum(1 for x in rooms if x.get("status") == "pendente")
active = sum(1 for x in rooms if x.get("status") == "em_atendimento")
k1,k2,k3,k4 = st.columns(4)
for col, label, value, note in [
    (k1,"AGUARDANDO",pending,"solicitações na fila"),(k2,"EM ATENDIMENTO",active,"salas abertas agora"),
    (k3,"SEU STATUS","ONLINE" if st.session_state.available else "PAUSADA","visibilidade para o totem"),
    (k4,"TEMPO DE RESPOSTA","—","média desta sessão")]:
    with col: st.markdown(f'<div class="glass"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)

st.write("")
queue_col, profile_col = st.columns([1.55, 1], gap="large")
with queue_col:
    st.markdown('<div class="section-title">Fila de atendimento</div><div class="subtle">Novos contatos aparecem aqui em tempo real.</div>',unsafe_allow_html=True)
    if load_error:
        st.error("Não consegui carregar a fila do Supabase. Confira as Secrets e a tabela rh_rooms.")
    elif not rooms:
        st.markdown('<div class="glass" style="margin-top:14px;text-align:center;padding:40px"><div style="font-size:2rem">✦</div><div class="section-title">Tudo tranquilo por aqui</div><div class="subtle">Quando alguém chamar pelo totem, o pedido aparecerá nesta fila.</div></div>',unsafe_allow_html=True)
    else:
        for room in rooms:
            rid=str(room.get("id","")); is_demo=rid.startswith("demo-")
            tipo=escape(str(room.get("tipo") or "Atendimento"))
            solicitante=escape(str(room.get("nome") or "Colaborador"))
            assunto=escape(str(room.get("assunto") or "Contato privado"))
            descricao=escape(str(room.get("descricao") or "O colaborador solicitou atendimento."))
            criado=escape(str(room.get("created_at", ""))[:16].replace("T", " "))
            status=str(room.get("status") or "pendente")
            badge="AGUARDANDO" if status=="pendente" else "EM ATENDIMENTO"
            badge_class="" if status=="pendente" else "off"
            st.markdown(f'''<div class="ticket"><div class="ticket-top"><div><div class="ticket-type">{tipo}</div><div class="ticket-name">{solicitante}</div></div><span class="pill {badge_class}">{badge}</span></div><div class="ticket-text"><b>{assunto}</b><br>{descricao}</div><div class="ticket-meta">Solicitação privada · {criado}</div></div>''',unsafe_allow_html=True)
            if room.get("status")=="pendente":
                if st.button("Aceitar atendimento",key=f"accept-{rid}",disabled=not st.session_state.available,use_container_width=False):
                    if store and not is_demo:
                        try: store.update("rh_rooms",f"id=eq.{rid}",{"status":"em_atendimento","atendente":name,"accepted_at":datetime.now().isoformat()})
                        except Exception as exc: st.error(f"Falha ao aceitar: {exc}")
                    else:
                        st.session_state.demo_queue=False
                    st.session_state.current_room=room
                    st.success("Atendimento aceito. A sala está preparada para conectar o totem.")
                    st.rerun()
            elif st.button("Abrir sala",key=f"open-{rid}"):
                st.session_state.current_room=room

with profile_col:
    st.markdown('<div class="section-title">Seu perfil</div><div class="subtle">Como sua equipe aparece para o colaborador.</div>',unsafe_allow_html=True)
    st.markdown('<div class="glass" style="margin-top:14px;text-align:center;padding:28px 20px">',unsafe_allow_html=True)
    if profile_url: st.image(profile_url,width=104)
    else: st.markdown('<div class="orb" style="width:88px;height:88px;margin:0 auto;font-size:1.6rem">RH</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="profile-name">{escape(name or "Atendimento RH")}</div><div class="profile-role">IBERO · Recursos Humanos</div><hr><div class="subtle">{ "Disponível para receber contatos" if st.session_state.available else "Pausada · o totem verá que a equipe está indisponível" }</div></div>',unsafe_allow_html=True)
    if st.session_state.get("current_room"):
        room=st.session_state.current_room
        st.markdown("#### Sala selecionada")
        st.info(f"{room.get('tipo','Atendimento')} · {room.get('assunto') or 'Contato privado'}")
        st.caption("A conexão de chat e vídeo será ligada à sala compartilhada com o totem na próxima etapa.")
        if st.button("Encerrar visualização",key="close-room"):
            st.session_state.current_room=None; st.rerun()

st.markdown("<hr>",unsafe_allow_html=True)
foot1,foot2=st.columns([8,2])
with foot1: st.caption("IBERO ATENDE · Atendimentos privados · Não grave ou compartilhe dados do colaborador fora do fluxo autorizado.")
with foot2:
    if st.button("Sair do painel",use_container_width=True):
        for key in ("rh_access_token", "rh_email", "rh_identity", "rh_name", "profile_url", "profile", "current_room"):
            st.session_state.pop(key, None)
        st.rerun()
