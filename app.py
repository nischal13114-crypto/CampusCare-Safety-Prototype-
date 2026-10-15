import streamlit as st
import pandas as pd
from datetime import datetime
from database import (
    init_db, list_incidents, create_incident, update_incident_status,
    list_contacts, add_contact, update_contact, delete_contact,
    seed_demo_data, reset_demo_data, count_incidents
)

st.set_page_config(page_title="CampusCare | Student Safety", page_icon="🛡️", layout="wide")
init_db()
seed_demo_data()

NAV = ["Home", "Emergency assistance", "Report an incident", "Emergency contacts",
       "Location & nearby services", "Safety instructions", "Admin dashboard"]

st.markdown("""
<style>
:root { --navy:#142b4a; --blue:#2764a5; --pale:#eaf3fc; --line:#d8e5f2; }
.block-container {padding-top:1.4rem; max-width:1200px;}
h1,h2,h3 {color:#142b4a;}
div[data-testid="stMetric"] {background:#eef5fc; border:1px solid #d8e5f2; padding:14px; border-radius:14px;}
.stButton>button {border-radius:10px; font-weight:600; min-height:2.5rem;}
div[data-testid="stAlert"] {border-radius:12px;}
.hero {background:linear-gradient(115deg,#142b4a,#2764a5);padding:28px;border-radius:18px;color:white;margin-bottom:18px;}
.hero h1 {color:white;margin:0;font-size:2.2rem;}
.hero p {color:#e8f2ff;margin:.5rem 0 0 0;}
.soft {background:#eef5fc;border:1px solid #d8e5f2;padding:16px;border-radius:14px;}
.small-note {color:#52657c;font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "emergency_category" not in st.session_state:
    st.session_state.emergency_category = "Medical"
if "sos_confirmed" not in st.session_state:
    st.session_state.sos_confirmed = False
if "last_incident_id" not in st.session_state:
    st.session_state.last_incident_id = None

def go(page):
    st.session_state.page = page

def navigate_to(page):
    # Runs before Streamlit rebuilds the sidebar radio widget.
    st.session_state.page = page
    st.session_state.nav_radio = page

def choose_emergency(category):
    st.session_state.emergency_category = category
    st.session_state.sos_confirmed = False
    navigate_to("Emergency assistance")

def tel_link(number):
    digits = "".join(ch for ch in str(number) if ch.isdigit() or ch == "+")
    return f"tel:{digits}"

def show_contacts():
    contacts = list_contacts()
    if not contacts:
        st.info("No contacts have been added yet.")
        return
    for c in contacts:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.markdown(f"**{c['name']}**  \n{c['category']} · {c['phone']}")
            col2.link_button("📞 Call", tel_link(c["phone"]), use_container_width=True)
            col3.button("Copy number", key=f"copy_{c['id']}", on_click=lambda n=c["phone"]: st.session_state.update({"copied_number": n}), use_container_width=True)
            if st.session_state.get("copied_number") == c["phone"]:
                st.caption(f"Number ready to copy: `{c['phone']}` (select and copy)")

def incident_form(default_category="Medical", key_prefix="incident"):
    categories = ["Medical", "Fire", "Harassment", "Lost Person", "Unsafe Situation", "Other"]
    with st.form(f"{key_prefix}_form", clear_on_submit=False):
        category = st.selectbox("Emergency category", categories, index=categories.index(default_category) if default_category in categories else 0)
        description = st.text_area("What happened? *", placeholder="Briefly describe the situation and immediate needs.")
        occurred = st.datetime_input("Date and time", value=datetime.now())
        location = st.text_input("Location / last-known location", placeholder="Building, room, gate, landmark, or manually entered coordinates")
        contact = st.text_input("Optional contact information", placeholder="Only share information needed to follow up")
        missing_person = st.text_input("Missing person reference (optional)", placeholder="Name or short description, if relevant")
        consent = st.checkbox("I understand this is a local demo report and consent to storing the details entered above.")
        submitted = st.form_submit_button("Record incident", type="primary", use_container_width=True)
    if submitted:
        if not description.strip():
            st.error("Please enter a short description before submitting.")
        elif not consent:
            st.error("Please confirm consent before submitting.")
        else:
            iid = create_incident(category, description.strip(), occurred.isoformat(timespec="minutes"),
                                  location.strip(), contact.strip(), missing_person.strip(), is_demo=0)
            st.session_state.last_incident_id = iid
            st.session_state.last_incident_category = category
            st.session_state.last_incident_time = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
            st.session_state.last_incident_page = st.session_state.get("page", "")
            st.success(f"Incident recorded locally. Reference ID: **{iid}**")
            st.info("This prototype has not contacted emergency services or campus security. If there is immediate danger, use the call link for the configured emergency number.")

def emergency_guidance(category):
    guidance = {
        "Medical": ["Call qualified emergency responders for serious or life-threatening symptoms.", "Keep the area safe and follow dispatcher instructions.", "Do not move someone with a possible serious injury unless there is immediate danger."],
        "Fire": ["Raise the alarm and leave by the nearest safe exit.", "Do not use lifts. Stay low if smoke is present.", "Once outside, move to the assembly point and do not re-enter."],
        "Harassment": ["Move toward a safer, populated place if possible.", "Contact campus security or a trusted adult/support service.", "Record only details you feel safe sharing; avoid confronting the person if it may increase risk."],
        "Lost Person": ["Notify campus security and share the last-known location and description.", "For a child or person in immediate danger, contact emergency services.", "Preserve relevant information and avoid spreading unverified claims."],
        "Unsafe Situation": ["Move away from the immediate hazard if safe to do so.", "Tell campus security or a trusted staff member.", "Give a clear location and concise description of the concern."]
    }
    for item in guidance.get(category, ["Move to a safer place if possible.", "Contact appropriate emergency responders or campus support."]):
        st.markdown(f"- {item}")
    st.caption("General information only; this app does not replace professional emergency advice.")

st.sidebar.markdown("## 🛡️ CampusCare")
st.sidebar.caption("Student Safety & Emergency Response")
st.sidebar.warning("DEMO MODE · Reports are stored locally only.")
page = st.sidebar.radio("Navigate", NAV, index=NAV.index(st.session_state.page), key="nav_radio")
st.session_state.page = page
st.sidebar.markdown("---")
st.sidebar.markdown("**Immediate danger?**")
st.sidebar.link_button("Call India emergency number · 112", "tel:112", use_container_width=True)
st.sidebar.caption("No automatic dispatch or message delivery is implemented.")

if page == "Home":
    st.markdown('<div class="hero"><h1>CampusCare</h1><p>Student Safety & Emergency Response System · Get help, share essential details, stay informed.</p></div>', unsafe_allow_html=True)
    st.warning("Safety notice: this is a student-built demonstration. It does not dispatch emergency services. For immediate danger in India, call 112.")
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Need assistance?")
        st.markdown("Choose a category to open a guided workflow.")
        categories = [("🩺", "Medical"), ("🔥", "Fire"), ("🤝", "Harassment"), ("🔎", "Lost Person"), ("⚠️", "Unsafe Situation")]
        cols = st.columns(2)
        for i, (emoji, cat) in enumerate(categories):
            with cols[i % 2]:
                st.button(
                    f"{emoji}  {cat}",
                    key=f"home_{cat}",
                    use_container_width=True,
                    on_click=choose_emergency,
                    args=(cat,)
                )
        st.button(
            "🆘 SOS / Emergency assistance",
            type="primary",
            use_container_width=True,
            on_click=navigate_to,
            args=("Emergency assistance",)
        )
    with right:
        st.subheader("Quick contacts")
        st.markdown('<div class="soft"><b>India national emergency number</b><br>112 · Police, fire and medical emergency response</div>', unsafe_allow_html=True)
        st.link_button("📞 Call 112", "tel:112", use_container_width=True)
        st.markdown("**Campus security**")
        cs = [c for c in list_contacts() if c["category"].lower() == "campus security"]
        if cs:
            st.write(f"{cs[0]['name']} · {cs[0]['phone']} *(demo contact)*")
        else:
            st.write("Add your institution's real contact in the contact directory.")
        st.subheader("Location status")
        st.info("Location not accessed. Open Location & nearby services to choose browser permission or enter a location manually.")
    st.subheader("Recent incident records")
    inc = list_incidents(limit=5)
    if inc:
        df = pd.DataFrame(inc)
        st.dataframe(df[["incident_id","category","created_at","status","is_demo"]].rename(columns={"incident_id":"Reference","created_at":"Recorded at","is_demo":"Demo data"}), hide_index=True, use_container_width=True)
    else:
        st.info("No incidents recorded yet.")
    st.subheader("Quick safety reminders")
    a,b,c = st.columns(3)
    a.markdown('<div class="soft">**Know your exits**<br>Identify safe exits and assembly points.</div>', unsafe_allow_html=True)
    b.markdown('<div class="soft">**Save key contacts**<br>Keep emergency numbers accessible.</div>', unsafe_allow_html=True)
    c.markdown('<div class="soft">**Share only what is needed**<br>Protect personal information.</div>', unsafe_allow_html=True)

elif page == "Emergency assistance":
    st.title("Emergency assistance")
    st.markdown("Follow the steps below. Submitting records the incident on this device only.")
    if st.session_state.get("last_incident_id") and st.session_state.get("last_incident_page") == "Emergency assistance":
        st.success(f"Last submission saved locally · Reference ID: {st.session_state.last_incident_id}")
        st.caption(f"Recorded at {st.session_state.get('last_incident_time', 'time unavailable')}. This confirmation remains visible until you navigate away or submit another report.")
    if st.button("🆘 SOS — start guided workflow", type="primary"):
        st.session_state.sos_confirmed = True
    if st.session_state.sos_confirmed:
        st.warning("Confirm you want to open the incident workflow. This will not call or message anyone.")
        c1,c2 = st.columns(2)
        if c1.button("Continue to emergency workflow", type="primary", use_container_width=True):
            st.session_state.sos_confirmed = False
            st.session_state.emergency_category = "Unsafe Situation"
            st.rerun()
        if c2.button("Cancel SOS", use_container_width=True):
            st.session_state.sos_confirmed = False
            st.rerun()
    category = st.selectbox("Select emergency type", ["Medical","Fire","Harassment","Lost Person","Unsafe Situation"],
                            index=["Medical","Fire","Harassment","Lost Person","Unsafe Situation"].index(st.session_state.emergency_category)
                            if st.session_state.emergency_category in ["Medical","Fire","Harassment","Lost Person","Unsafe Situation"] else 0)
    st.session_state.emergency_category = category
    st.subheader(f"{category} — immediate guidance")
    emergency_guidance(category)
    st.markdown("### Record essential details")
    incident_form(category, "assistance")
    st.markdown("### Relevant contacts")
    show_contacts()

elif page == "Report an incident":
    st.title("Report an incident")
    st.write("Submit only information necessary to understand and follow up on the concern.")
    if st.session_state.get("last_incident_id") and st.session_state.get("last_incident_page") == "Report an incident":
        st.success(f"Last submission saved locally · Reference ID: {st.session_state.last_incident_id}")
        st.caption(f"Recorded at {st.session_state.get('last_incident_time', 'time unavailable')}. This confirmation remains visible until you navigate away or submit another report.")
    incident_form("Unsafe Situation", "report")

elif page == "Emergency contacts":
    st.title("Emergency contacts")
    st.caption("India national emergency number: 112. Campus-specific examples are fictional and must be replaced.")
    q = st.text_input("Search contacts", placeholder="Search name, category or number")
    cat = st.selectbox("Filter by category", ["All","National Emergency","Ambulance","Fire","Police","Campus Security","Student Support","Trusted Contact"])
    contacts = list_contacts()
    contacts = [c for c in contacts if (cat=="All" or c["category"]==cat) and q.lower() in (c["name"]+" "+c["category"]+" "+c["phone"]).lower()]
    if contacts:
        st.dataframe(pd.DataFrame(contacts)[["name","category","phone","is_demo"]].rename(columns={"is_demo":"Fictional demo entry"}), hide_index=True, use_container_width=True)
        for c in contacts:
            col1,col2,col3 = st.columns([3,1,1])
            col1.write(f"**{c['name']}** · {c['category']} · `{c['phone']}`")
            col2.link_button("Call", tel_link(c["phone"]), key=f"contact_call_{c['id']}")
            col3.button("Copy number", key=f"contact_copy_{c['id']}", on_click=lambda n=c["phone"]: st.session_state.update({"copied_number": n}))
    else:
        st.info("No matching contacts.")
    st.caption("Copy-number controls display the number for manual copying; clipboard access varies by browser.")
    with st.expander("Add a campus contact (demo admin function)"):
        with st.form("add_contact_form"):
            name = st.text_input("Contact name")
            category_new = st.selectbox("Category", ["Ambulance","Fire","Police","Campus Security","Student Support","Trusted Contact"])
            phone = st.text_input("Phone number")
            demo = st.checkbox("This is fictional demo data", value=True)
            if st.form_submit_button("Add contact"):
                if not name.strip() or not phone.strip():
                    st.error("Name and phone are required.")
                else:
                    add_contact(name.strip(), category_new, phone.strip(), int(demo))
                    st.success("Contact added.")
                    st.rerun()

elif page == "Location & nearby services":
    st.title("Location & nearby services")
    st.warning("Location is optional. Nothing is sent to another person by this demo.")
    st.markdown("Browser location requires permission and generally works on `localhost` or a secure HTTPS site.")
    st.components.v1.html("""
    <div style="font-family:Arial;padding:14px;border:1px solid #d8e5f2;border-radius:12px;background:#eef5fc;color:#142b4a">
      <b>Use your current browser location</b>
      <p>Choose Allow when your browser asks. Nearby-service links below will be built from the coordinates actually returned by your device.</p>
      <button onclick="getLocation()" style="padding:10px 14px;border:0;border-radius:8px;background:#2764a5;color:white;cursor:pointer">Find my current location</button>
      <p id="result">Location has not been accessed.</p>
      <div id="nearby" style="display:none;gap:8px;flex-wrap:wrap">
        <a id="hosp" target="_blank" rel="noopener" style="display:inline-block;padding:9px 12px;background:white;border:1px solid #b8cde4;border-radius:8px;color:#245d9c">Nearby hospitals</a>
        <a id="police" target="_blank" rel="noopener" style="display:inline-block;padding:9px 12px;background:white;border:1px solid #b8cde4;border-radius:8px;color:#245d9c">Nearby police stations</a>
        <a id="fire" target="_blank" rel="noopener" style="display:inline-block;padding:9px 12px;background:white;border:1px solid #b8cde4;border-radius:8px;color:#245d9c">Nearby fire services</a>
        <a id="map" target="_blank" rel="noopener" style="display:inline-block;padding:9px 12px;background:white;border:1px solid #b8cde4;border-radius:8px;color:#245d9c">Open my location on map</a>
      </div>
      <script>
      function getLocation(){
        const out=document.getElementById('result');
        const nearby=document.getElementById('nearby');
        if(!navigator.geolocation){out.innerText='Geolocation is not supported by this browser. Use manual entry below.';return;}
        out.innerText='Waiting for permission and GPS/network location…';
        navigator.geolocation.getCurrentPosition(
          p=>{
            const lat=p.coords.latitude, lon=p.coords.longitude;
            const latS=lat.toFixed(6), lonS=lon.toFixed(6);
            out.innerHTML='Current device coordinates: <b>'+latS+', '+lonS+'</b><br>Accuracy: approximately '+Math.round(p.coords.accuracy)+' metres. Nearby links will open centered on these coordinates.';
            document.getElementById('hosp').href='https://www.google.com/maps/search/hospitals/@'+lat+','+lon+',14z';
            document.getElementById('police').href='https://www.google.com/maps/search/police+stations/@'+lat+','+lon+',14z';
            document.getElementById('fire').href='https://www.google.com/maps/search/fire+stations/@'+lat+','+lon+',14z';
            document.getElementById('map').href='https://www.openstreetmap.org/?mlat='+latS+'&mlon='+lonS+'#map=16/'+latS+'/'+lonS;
            nearby.style.display='flex';
          },
          e=>{
            nearby.style.display='none';
            const msg = e.code===1 ? 'Location permission was denied.' : (e.code===2 ? 'The device could not determine your location.' : 'Location request timed out.');
            out.innerText=msg+' Please allow location permission and try again, or use manual location entry below.';
          },
          {enableHighAccuracy:true,timeout:20000,maximumAge:0});
      }
      </script>
    </div>
    """, height=260)
    st.subheader("Manual location entry")
    with st.form("manual_location"):
        manual = st.text_input("Location, coordinates, building or landmark")
        saved = st.form_submit_button("Use this location")
    if saved and manual.strip():
        st.session_state.manual_location = manual.strip()
        st.success(f"Manual location saved for this session: {manual.strip()}")
    from urllib.parse import quote_plus
    st.markdown("**Search around a manually entered location**")
    st.caption("Use this if browser location is unavailable. Enter a town, campus, landmark, or coordinates; these searches use the text you enter and are not described as live location.")
    loc = st.text_input("Town, campus, landmark or coordinates", value=st.session_state.get("manual_location",""), key="nearby_manual_search")
    if st.button("Use manual search location"):
        if loc.strip():
            st.session_state.manual_location = loc.strip()
            st.success(f"Manual search location set to: {loc.strip()}")
        else:
            st.error("Enter a location first.")
    if loc.strip():
        encoded = quote_plus(loc.strip())
        cols=st.columns(3)
        for col, label, query in zip(cols, ["Hospitals","Police stations","Fire services"], ["hospitals","police stations","fire stations"]):
            url = "https://www.google.com/maps/search/" + quote_plus(query) + "/@" + encoded
            # Google Maps search query works more reliably than treating a text place as coordinates.
            url = "https://www.google.com/maps/search/" + quote_plus(query + " near " + loc.strip())
            col.link_button(f"Find {label}", url, use_container_width=True)

elif page == "Safety instructions":
    st.title("Safety instructions")
    guides = {
        "Medical emergencies": "Call emergency responders for serious symptoms. Follow dispatcher instructions. Do not give food or drink to an unconscious person. Only provide first aid you are trained to give.",
        "Fire incidents": "Raise the alarm, evacuate using safe exits, avoid lifts, and move to the assembly point. Do not re-enter the building.",
        "Harassment and personal safety": "Move to a safer public area if possible. Contact campus security or a trusted support person. Keep records only if it is safe to do so.",
        "Lost persons": "Notify campus security promptly. Share a factual description and last-known location with appropriate responders. Avoid spreading unverified details.",
        "Unsafe campus locations": "Avoid the immediate hazard, inform campus security or facilities staff, and describe the location clearly.",
        "General preparedness": "Save emergency numbers, learn exit routes and assembly points, keep essential medication accessible where applicable, and know how to contact campus support."
    }
    q = st.text_input("Search safety guidance")
    for title, body in guides.items():
        if q.lower() in (title+" "+body).lower():
            with st.expander(title, expanded=bool(q)):
                st.write(body)
    st.info("This is general guidance, not professional medical, legal, or emergency advice. Contact qualified responders when needed.")

elif page == "Admin dashboard":
    st.title("Admin dashboard")
    st.warning("DEMO ADMIN VIEW — no real authentication is configured. Do not use this as production security.")
    with st.expander("Demo access confirmation"):
        code = st.text_input("Enter demo access code", type="password", help="Default demo code: CAMPUS-DEMO")
        if st.button("Unlock admin tools"):
            st.session_state.admin_unlocked = (code == "CAMPUS-DEMO")
            if not st.session_state.admin_unlocked:
                st.error("Incorrect demo code.")
    unlocked = st.session_state.get("admin_unlocked", False)
    if not unlocked:
        st.info("Enter the demo code above to manage incident statuses and contacts. The incident summary remains visible.")
    incidents = list_incidents()
    total = len(incidents)
    new_count = sum(i["status"]=="New" for i in incidents)
    review_count = sum(i["status"]=="Reviewing" for i in incidents)
    resolved_count = sum(i["status"]=="Resolved" for i in incidents)
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Total incidents", total); m2.metric("New",new_count); m3.metric("Reviewing",review_count); m4.metric("Resolved",resolved_count)
    cat_filter=st.selectbox("Filter incidents by category", ["All","Medical","Fire","Harassment","Lost Person","Unsafe Situation","Other"])
    status_filter=st.selectbox("Filter by status", ["All","New","Reviewing","Resolved"])
    search=st.text_input("Search incident ID, description or location")
    filtered=[i for i in incidents if (cat_filter=="All" or i["category"]==cat_filter) and (status_filter=="All" or i["status"]==status_filter) and search.lower() in (i["incident_id"]+" "+i["description"]+" "+i["location"]).lower()]
    if filtered:
        df=pd.DataFrame(filtered)
        st.dataframe(df[["incident_id","category","description","created_at","location","status","is_demo"]].rename(columns={"incident_id":"Reference","created_at":"Recorded at","is_demo":"Demo data"}), hide_index=True, use_container_width=True)
        if unlocked:
            st.subheader("Update incident status")
            selected=st.selectbox("Incident", [i["incident_id"] for i in filtered])
            status=st.selectbox("New status", ["New","Reviewing","Resolved"])
            if st.button("Save status change", type="primary"):
                update_incident_status(selected,status)
                st.success("Status updated in SQLite.")
                st.rerun()
    else:
        st.info("No incidents match those filters.")
    if unlocked:
        st.subheader("Manage contacts")
        contacts=list_contacts()
        if contacts:
            selected_contact=st.selectbox("Choose contact to remove", [f"{c['id']} · {c['name']} ({c['phone']})" for c in contacts])
            if st.button("Remove selected contact"):
                delete_contact(int(selected_contact.split(" · ")[0]))
                st.success("Contact removed.")
                st.rerun()
        with st.expander("Add contact"):
            with st.form("admin_add_contact"):
                n=st.text_input("Name")
                cat=st.selectbox("Category", ["National Emergency","Ambulance","Fire","Police","Campus Security","Student Support","Trusted Contact"])
                p=st.text_input("Phone")
                demo=st.checkbox("Fictional demo contact", value=True)
                if st.form_submit_button("Save contact"):
                    if n.strip() and p.strip():
                        add_contact(n.strip(),cat,p.strip(),int(demo)); st.success("Saved."); st.rerun()
                    else: st.error("Enter both name and phone.")
        st.subheader("Reset demonstration data")
        st.error("This deletes incident/contact records and recreates the original fictional demo set.")
        if "confirm_reset" not in st.session_state: st.session_state.confirm_reset=False
        st.session_state.confirm_reset=st.checkbox("I confirm reset of local demo data", value=st.session_state.confirm_reset)
        if st.button("Reset demo data", disabled=not st.session_state.confirm_reset):
            reset_demo_data()
            st.session_state.confirm_reset=False
            st.success("Demo data reset.")
            st.rerun()
