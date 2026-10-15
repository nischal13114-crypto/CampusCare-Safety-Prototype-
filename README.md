# CampusCare — Student Safety & Emergency Response Prototype

A local, presentation-ready Streamlit prototype. Incident reports, statuses, and contacts are stored in SQLite on the computer running the app.

## Requirements
- Python 3.10 or newer
- Internet is needed once to install dependencies. Core app features run locally afterward.
- No API key or account is required.

## Install and run

Open a terminal in this folder and run:

### Windows
```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. Open it in a browser.

## Demo administrator access
Navigate to **Admin dashboard**, expand **Demo access confirmation**, and enter:

`CAMPUS-DEMO`

This is deliberately a simple demo gate, not production authentication. Anyone with access to the app source can see the code.

## Suggested 4-minute jury demo
1. **Home (30 sec):** Introduce the goal, safety notice, category shortcuts, 112 call link, and pre-seeded demo incidents.
2. **Emergency flow (60 sec):** Choose Medical or Fire, read the immediate guidance, submit a short incident with location `Main block, room 12`, and tick the consent checkbox. Show the generated `CC-...` reference.
3. **Contacts/location (45 sec):** Search contacts; show the `tel:` call links. In Location & nearby services, request browser location only if you are comfortable granting permission, or use a manual location. Open the OpenStreetMap search link.
4. **Admin dashboard (60 sec):** Unlock with `CAMPUS-DEMO`, filter incidents, change the new report to Reviewing, and show the updated status persists.
5. **Reset (30 sec):** Use the reset checkbox and reset button to restore fictional demo records.

## Implemented
- Navigation between all eight sections.
- Emergency categories and category-specific general safety guidance.
- SOS confirmation before opening a guided workflow.
- Incident validation, consent checkbox, unique reference ID, timestamp, and SQLite persistence.
- Incident listing, category/status/search filters, and status changes.
- Fictional demo incidents and campus contacts.
- Searchable contacts, category filtering, phone links, and add/remove contact controls.
- Browser geolocation request with permission; manual location fallback; OpenStreetMap links.
- Searchable safety instructions and clear demo-mode warnings.

## Limitations and responsible use
- **No automatic dispatch:** reports are saved only in the local SQLite database. They are not sent to police, ambulance, campus security, or any other recipient.
- **Geolocation:** browser permission and secure-context rules apply. The embedded browser component displays coordinates and map/copy links within that component; it does not silently transmit them to Streamlit or attach them to an incident. Use manual entry to include a location in a report.
- **Calls:** `tel:` links ask the device/browser to open a calling application; actual calling depends on the device.
- **Copying:** copy-number controls show the number for manual copying; clipboard access differs by browser.
- **Admin security:** the demo gate is not production-grade. A real deployment needs authentication, role-based access, encrypted transport, audit logs, retention policies, secure hosting, and privacy/legal review.
- **Emergency numbers:** 112 is the India national emergency number. Replace fictional campus contacts before any real-world pilot.
- **No offline installation:** dependencies must first be installed. Once installed, the local app/database do not need cloud services, but external maps need internet.
- **Not a replacement for emergency services or professional advice.**

## Files
- `app.py` — Streamlit UI and workflows
- `database.py` — SQLite operations and demo seed data
- `requirements.txt` — Python dependencies
- `tests/test_database.py` — database behavior tests

## Tests
From this folder after Python is installed:
```bash
python -m unittest discover -s tests -v
```
Tests use a temporary database file so your demo database is not affected.


## Navigation fix
This build synchronizes dashboard category buttons with the sidebar navigation state. Replace your old extracted folder with this updated project ZIP to apply the fix.

## Update: persistent submission receipt and location-based nearby searches
- Successful report confirmations are no longer immediately cleared by an explicit rerun. The most recent receipt stays visible on the relevant report page, with its reference ID and timestamp.
- Browser geolocation now builds nearby hospital/police/fire Google Maps links using the actual coordinates returned by the browser, and offers an OpenStreetMap link centered on those coordinates.
- If geolocation is denied/unavailable, manual place-based Google Maps searches are available. A manual place is not presented as live GPS.
- Browser geolocation works best on localhost or HTTPS. The location component does not silently transmit coordinates into the incident form.
