import streamlit as st
from seed_data import (
    SERVICES_BY_CATEGORY,
    todos_los_servicios,
    generar_estilistas,
)

st.set_page_config(page_title="Pelu Demo", page_icon="💇", layout="wide")

# ────── Session init ──────
if "ready" not in st.session_state:
    st.session_state.ready = True
    st.session_state.clients = {}
    st.session_state.queues = {c: [] for c in SERVICES_BY_CATEGORY}
    st.session_state.stylists = generar_estilistas()

SES = st.session_state


def svckey(cedula, categoria, servicio):
    return f"{cedula}||{categoria}||{servicio}"


def parsekey(key):
    parts = key.split("||", 2)
    return parts[0], parts[1], parts[2]


def get_svc(cedula, categoria, servicio):
    cl = SES.clients.get(cedula)
    if not cl:
        return None
    for s in cl["servicios"]:
        if s["categoria"] == categoria and s["servicio"] == servicio:
            return s
    return None


def busy(cedula):
    cl = SES.clients.get(cedula)
    if not cl:
        return False
    return any(s["status"] == "En servicio" for s in cl["servicios"])


def next_stylist(categoria):
    for st in SES.stylists.values():
        if st["categoria"] == categoria and not st["ocupado"]:
            return st
    return None


def svc_label(categoria, servicio):
    return f"{categoria} | {servicio}"


def parse_label(label):
    return label.split(" | ", 1)


def svc_options():
    opts = []
    for cat, svcs in SERVICES_BY_CATEGORY.items():
        for s in svcs:
            key = f"{cat}||{s}"
            lbl = svc_label(cat, s)
            opts.append(lbl)
    return opts


def label_to_catsvc(label):
    cat, svc = label.split(" | ", 1)
    return cat, svc


# ────── Actions ──────
def registrar_cliente(cedula, nombre, telefono, direccion, selected_labels):
    if not cedula.strip():
        st.error("Cédula es obligatoria", icon="⚠️")
        return
    if not nombre.strip():
        st.error("Nombre es obligatorio", icon="⚠️")
        return
    if not selected_labels:
        st.error("Seleccione al menos un servicio", icon="⚠️")
        return
    if cedula.strip() in SES.clients:
        st.error("Ya existe un cliente con esa cédula", icon="⚠️")
        return

    servicios = []
    for lbl in selected_labels:
        cat, svc = label_to_catsvc(lbl)
        servicios.append({
            "servicio": svc,
            "categoria": cat,
            "status": "En espera",
            "stylist_id": None,
        })

    SES.clients[cedula.strip()] = {
        "cedula": cedula.strip(),
        "nombre": nombre.strip(),
        "telefono": telefono.strip(),
        "direccion": direccion.strip(),
        "servicios": servicios,
    }

    for s in servicios:
        k = svckey(cedula.strip(), s["categoria"], s["servicio"])
        SES.queues[s["categoria"]].append(k)

    st.success(f"Cliente {nombre.strip()} registrado con {len(servicios)} servicio(s)")
    st.rerun()


def agregar_servicio_cliente(cedula, selected_label):
    if not cedula:
        st.error("Seleccione un cliente")
        return
    if not selected_label:
        st.error("Seleccione un servicio")
        return
    cl = SES.clients.get(cedula.strip())
    if not cl:
        st.error("Cliente no encontrado")
        return

    cat, svc = label_to_catsvc(selected_label)
    for s in cl["servicios"]:
        if s["categoria"] == cat and s["servicio"] == svc:
            st.warning("Este cliente ya tiene ese servicio")
            return

    new_svc = {
        "servicio": svc,
        "categoria": cat,
        "status": "En espera",
        "stylist_id": None,
    }
    cl["servicios"].append(new_svc)
    k = svckey(cedula.strip(), cat, svc)
    SES.queues[cat].append(k)
    st.success(f"Servicio '{svc}' agregado a {cl['nombre']}")
    st.rerun()


def asignar_siguiente(categoria):
    q = SES.queues[categoria]
    for _ in range(len(q)):
        k = q[0]
        ced, cat, svc = parsekey(k)
        service = get_svc(ced, cat, svc)

        if not service or service["status"] != "En espera":
            q.pop(0)
            continue

        if busy(ced):
            q.append(q.pop(0))
            continue

        stylist = next_stylist(categoria)
        if not stylist:
            st.warning(f"⚠️ No hay estilistas disponibles en {categoria}")
            return

        service["status"] = "En servicio"
        service["stylist_id"] = stylist["id"]
        stylist["ocupado"] = True
        stylist["cliente_actual"] = ced
        stylist["servicio_actual"] = svc
        q.pop(0)
        st.rerun()

    st.info(f"Todos los clientes en {categoria} están ocupados en otro servicio")


def finalizar_servicio(cedula, categoria, servicio):
    service = get_svc(cedula, categoria, servicio)
    if not service or service["status"] != "En servicio":
        return
    sid = service.get("stylist_id")
    if sid and sid in SES.stylists:
        st = SES.stylists[sid]
        st["ocupado"] = False
        st["cliente_actual"] = None
        st["servicio_actual"] = None
    service["status"] = "Finalizado"
    service["stylist_id"] = None
    st.rerun()


def pending_in_queue(categoria):
    pending = []
    for k in SES.queues[categoria]:
        ced, cat, svc = parsekey(k)
        service = get_svc(ced, cat, svc)
        if service and service["status"] == "En espera":
            pending.append((ced, service))
    return pending


def active_in_category(categoria):
    active = []
    for ced, cl in SES.clients.items():
        for s in cl["servicios"]:
            if s["status"] == "En servicio" and s["categoria"] == categoria:
                active.append((ced, cl, s))
    return active


def count_en_espera(categoria):
    return sum(1 for k in SES.queues[categoria]
               if get_svc(*parsekey(k)) and get_svc(*parsekey(k))["status"] == "En espera")


def count_en_servicio(categoria):
    return len(active_in_category(categoria))


def count_finalizados(categoria):
    count = 0
    for cl in SES.clients.values():
        count += sum(1 for s in cl["servicios"]
                     if s["categoria"] == categoria and s["status"] == "Finalizado")
    return count


def stylist_name(sid):
    if sid and sid in SES.stylists:
        return SES.stylists[sid]["nombre"]
    return "—"

# ────── UI ──────
st.title("💇 Peluquería — Demo de Cola Inteligente")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📋 Registro", "📊 Master (Recepción)", "💺 Estilistas"])

# ══════════════════════════════════════
# TAB 1 — REGISTRO
# ══════════════════════════════════════
with tab1:
    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.subheader("Nuevo Cliente")
        with st.form("registro_form", clear_on_submit=True):
            cedula = st.text_input("Cédula *", placeholder="Ej: 4.567.890-1")
            nombre = st.text_input("Nombre y apellido *", placeholder="Ej: Juan Pérez")
            telefono = st.text_input("Teléfono", placeholder="Ej: 099123456")
            direccion = st.text_input("Dirección", placeholder="Ej: Av. Italia 1234")
            servicios = st.multiselect(
                "Servicios a realizarse *",
                options=svc_options(),
                placeholder="Seleccione uno o más servicios...",
            )
            submitted = st.form_submit_button("✅ Registrar Cliente", use_container_width=True)
            if submitted:
                registrar_cliente(cedula, nombre, telefono, direccion, servicios)

    with col_b:
        st.subheader("Agregar Servicio a Cliente")
        if not SES.clients:
            st.info("No hay clientes registrados todavía")
        else:
            clientes_opts = [
                f"{c['cedula']} — {c['nombre']}" for c in SES.clients.values()
            ]
            ced_seleccionada = st.selectbox(
                "Cliente",
                options=clientes_opts,
                key="add_svc_client",
            )
            ced = ced_seleccionada.split(" — ")[0] if ced_seleccionada else ""
            svc_nuevo = st.selectbox(
                "Nuevo servicio",
                options=svc_options(),
                key="add_svc_svc",
            )
            if st.button("➕ Agregar servicio", use_container_width=True):
                agregar_servicio_cliente(ced, svc_nuevo)

    st.markdown("---")
    st.subheader("Clientes Registrados")
    if not SES.clients:
        st.info("No hay clientes registrados")
    else:
        for ced, cl in SES.clients.items():
            with st.expander(f"**{cl['nombre']}**  |  C.I. {cl['cedula']}  |  📞 {cl['telefono'] or '—'}  |  📍 {cl['direccion'] or '—'}"):
                for s in cl["servicios"]:
                    icon = {"En espera": "🔵", "En servicio": "🟡", "Finalizado": "🟢"}[s["status"]]
                    stn = stylist_name(s.get("stylist_id"))
                    st.markdown(
                        f"{icon} **{s['categoria']}** — {s['servicio']} "
                        f"`{s['status']}` "
                        + (f" · {stn}" if s.get("stylist_id") else "")
                    )

# ══════════════════════════════════════
# TAB 2 — MASTER
# ══════════════════════════════════════
with tab2:
    st.subheader("Panel de Control — Colas por Categoría")

    cats = list(SERVICES_BY_CATEGORY.keys())
    cols = st.columns(len(cats))

    for idx, categoria in enumerate(cats):
        with cols[idx]:
            espera = count_en_espera(categoria)
            servicio = count_en_servicio(categoria)
            finalizados = count_finalizados(categoria)
            libres = sum(
                1 for st in SES.stylists.values()
                if st["categoria"] == categoria and not st["ocupado"]
            )

            st.markdown(f"### 💇 {categoria}")
            st.caption(f"🔵 {espera} espera  ·  🟡 {servicio} en curso  ·  🟢 {finalizados} listos")
            st.caption(f"💺 {libres} estilistas libres de {len([s for s in SES.stylists.values() if s['categoria'] == categoria])}")

            if st.button(f"▶️ Iniciar próximo", key=f"assign_{categoria}", use_container_width=True):
                asignar_siguiente(categoria)

            st.markdown("---")

            pendientes = pending_in_queue(categoria)
            if pendientes:
                st.markdown("**🔵 En espera**")
                for i, (ced, svc) in enumerate(pendientes):
                    stn = stylist_name(svc.get("stylist_id"))
                    st.markdown(
                        f"{i+1}. **{SES.clients[ced]['nombre']}**\n\n"
                        f"   {svc['servicio']}",
                        help=f"C.I. {ced}"
                    )
            else:
                st.caption("Sin espera")

            activos = active_in_category(categoria)
            if activos:
                st.markdown("**🟡 En servicio**")
                for ced, cl, svc in activos:
                    stn = stylist_name(svc.get("stylist_id"))
                    st.markdown(
                        f"**{cl['nombre']}**\n\n"
                        f"   {svc['servicio']} · {stn}",
                        help=f"C.I. {ced}"
                    )
                    if st.button("⏹️ Finalizar", key=f"fin_m_{ced}_{categoria}_{svc['servicio']}", use_container_width=True):
                        finalizar_servicio(ced, categoria, svc["servicio"])

    # Sidebar with add-service to existing client
    with st.sidebar:
        st.markdown("## ➕ Agregar Servicio Existente")
        if not SES.clients:
            st.info("No hay clientes")
        else:
            clientes_sidebar = [
                f"{c['cedula']} — {c['nombre']}" for c in SES.clients.values()
            ]
            ced_sb_str = st.selectbox("Cliente", options=clientes_sidebar, key="sb_client")
            ced_sb = ced_sb_str.split(" — ")[0] if ced_sb_str else ""
            svc_sb = st.selectbox("Servicio", options=svc_options(), key="sb_svc")
            if st.button("➕ Agregar", key="sb_add", use_container_width=True):
                agregar_servicio_cliente(ced_sb, svc_sb)

# ══════════════════════════════════════
# TAB 3 — ESTILISTAS
# ══════════════════════════════════════
with tab3:
    st.subheader("Vista por Estilista")

    cat_sel = st.radio(
        "Categoría",
        options=list(SERVICES_BY_CATEGORY.keys()),
        horizontal=True,
        key="stylist_cat",
    )

    stylist_list = [st for st in SES.stylists.values() if st["categoria"] == cat_sel]

    st.markdown(f"### Estilistas de {cat_sel}")

    n_cols = 4
    rows = [stylist_list[i:i + n_cols] for i in range(0, len(stylist_list), n_cols)]

    for row in rows:
        cols = st.columns(n_cols)
        for i, styl in enumerate(row):
            with cols[i]:
                if styl["ocupado"]:
                    st.markdown(
                        f"**{styl['nombre']}**\n\n"
                        f"🔴 Ocupado\n\n"
                        f"Cliente: **{SES.clients.get(styl['cliente_actual'], {}).get('nombre', '—')}**\n\n"
                        f"Servicio: {styl['servicio_actual'] or '—'}"
                    )
                    if st.button("⏹️ Finalizar", key=f"fin_s_{styl['id']}", use_container_width=True):
                        ced = styl["cliente_actual"]
                        svc = styl["servicio_actual"]
                        if ced and svc:
                            finalizar_servicio(ced, cat_sel, svc)
                else:
                    st.markdown(
                        f"**{styl['nombre']}**\n\n"
                        f"🟢 Disponible"
                    )
