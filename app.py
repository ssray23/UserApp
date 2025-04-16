import os
import json
import pandas as pd
from flask import Flask, render_template_string, request, redirect, url_for
from markupsafe import escape
import base64
import os.path

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# --- Font Embedding Code (Keep as before) ---
FONT_CONFIG = {
    'Helvetica Local': {
        'normal': { '400': 'Helvetica-Regular.woff', '700': 'Helvetica-Bold.woff' },
        'italic': { '400': 'Helvetica-Italic.woff', '700': 'Helvetica-BoldItalic.woff' }
    }
}
def encode_font_to_base64(font_path):
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, font_path)
    if not os.path.exists(full_path): print(f"Warning: Font file not found {full_path}. Skipping."); return None
    try:
        with open(full_path, "rb") as font_file: return base64.b64encode(font_file.read()).decode('utf-8')
    except Exception as e: print(f"Error encoding font {font_path}: {e}"); return None
def generate_font_face_css(config):
    css = ""
    for family_name, styles in config.items():
        for style, weights in styles.items():
            for weight, path in weights.items():
                encoded_font = encode_font_to_base64(path)
                if encoded_font:
                    if path.lower().endswith('.woff'): mime_type, format_type = 'font/woff', 'woff'
                    else: print(f"Warning: Unsupported format {path}. Skipping."); continue
                    css += f"""
@font-face {{ font-family: '{family_name}'; src: url(data:{mime_type};base64,{encoded_font}) format('{format_type}'); font-weight: {weight}; font-style: {style}; font-display: swap; }}"""
    return css
FONT_FACE_CSS = generate_font_face_css(FONT_CONFIG)
# --- End Font Embedding Code ---

# --- Load Hobbies (Keep as before) ---
hobbies_file = os.path.join(os.path.dirname(__file__), 'hobbies.csv')
try:
    hobbies_df = pd.read_csv(hobbies_file)
    hobbies_list = hobbies_df['hobby'].tolist()
except FileNotFoundError: hobbies_list = []
except Exception: hobbies_list = []

# --- Data Storage (Keep as before) ---
data_file = 'data.json'; data = []
if os.path.exists(data_file):
    try:
        with open(data_file, 'r') as f: data = json.load(f)
        if not isinstance(data, list): data = []
    except Exception: data = []

# --- HTML Template ---
template = f'''
<!DOCTYPE html>
<html>
<head>
    <title>User Management</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        {FONT_FACE_CSS}
        body {{ font-family: 'Helvetica Local', 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f0f2f5; font-size: 14px; }}
        button, h1, h2, .field-label {{ font-family: 'Helvetica Local', 'Helvetica Neue', Helvetica, Arial, sans-serif; }}
        h1, button {{ font-weight: 700; }}
        .field-label {{ font-weight: 700; }}
        .rounded-10 {{ border-radius: 10px; }}
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 1000; }}
        .modal-content {{ background-color: white; margin: 10% auto; padding: 20px; width: 60%; border-radius: 10px; }}
        .app-container {{ border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); overflow: hidden; background-color: white; border: 1px solid #e5e7eb; max-height: 90vh; overflow-y: auto; }}
        .app-header {{ background-color: #f8fafc; border-bottom: 1px solid #e5e7eb; padding: 1.5rem; }}
        #addButton {{ width: 150px; background-color: #1a5e3b; transition: background-color 0.3s ease; }}
        #addButton:disabled {{ background-color: #a3c9b5; opacity: 0.6; cursor: not-allowed; }}
        #addButton:not(:disabled):hover {{ background-color: #2e7d55; }}

        /* Table Container */
        .table-container {{ max-height: 300px; overflow-y: auto; overflow-x: hidden; position: relative; border-radius: 10px; border: 1px solid #e5e7eb; }}
        .table-container::-webkit-scrollbar {{ width: 8px; }}
        .table-container::-webkit-scrollbar-track {{ background: #f1f1f1; border-radius: 10px; }}
        .table-container::-webkit-scrollbar-thumb {{ background: #888; border-radius: 10px; }}
        .table-container::-webkit-scrollbar-thumb:hover {{ background: #555; }}

        /* Table */
        table {{ width: 100%; table-layout: fixed; border-collapse: separate; border-spacing: 0; }}
        thead {{ position: sticky; top: 0; background-color: #f1f5f9; z-index: 1; }}
        thead th:first-child {{ border-top-left-radius: 10px; border-left: 1px solid #e5e7eb; border-top: 1px solid #e5e7eb;}}
        thead th:last-child {{ border-top-right-radius: 10px; border-right: 1px solid #e5e7eb; border-top: 1px solid #e5e7eb; }}
        thead th {{ border-top: 1px solid #e5e7eb; font-weight: 700; }}

        /* General Cells */
        th, td {{
            border-bottom: 1px solid #e5e7eb;
            border-right: 1px solid #e5e7eb;
            padding: 10px 12px;
            text-align: left; /* Default alignment */
            overflow: hidden;
            white-space: nowrap;
            vertical-align: middle;
            font-size: 13px;
        }}
        th:first-child, td:first-child {{ border-left: none; }}
        th:last-child, td:last-child {{ border-right: none; }}
        tbody tr:last-child td {{ border-bottom: none; }}

        /* Columns needing ellipsis */
        th:nth-child(2), td:nth-child(2), th:nth-child(3), td:nth-child(3),
        th:nth-child(4), td:nth-child(4)
        {{ text-overflow: ellipsis; }}

        /* Hobbies column: allow horizontal scroll */
        td:nth-child(5) {{ overflow-x: auto; text-overflow: clip; }}

        /* Actions column header and cell */
        th:nth-child(6) {{
            text-align: center; /* <-- Center Actions header text */
        }}
        td:nth-child(6) {{
            text-align: center;
            vertical-align: middle;
        }}
        td:nth-child(6) button {{ display: inline-block; width: auto; }}

        /* Column widths */
        th:nth-child(1), td:nth-child(1) {{ width: 5%; text-align: center; /* Center checkbox */}}
        th:nth-child(2), td:nth-child(2) {{ width: 20%; }}
        th:nth-child(3), td:nth-child(3) {{ width: 10%; }}
        th:nth-child(4), td:nth-child(4) {{ width: 10%; }}
        th:nth-child(5), td:nth-child(5) {{ width: 40%; }}
        th:nth-child(6), td:nth-child(6) {{ width: 15%; }}

        tbody tr:nth-child(odd) {{ background-color: #ffffff; }}
        tbody tr:nth-child(even) {{ background-color: #f9fafb; }}
        select[multiple] {{ height: 150px; }}
        select[name="hobbies"] option:nth-child(even),
        select.edit-hobbies option:nth-child(even) {{ background-color: #e0f2fe; }}
        select[name="hobbies"] option,
        select.edit-hobbies option {{ padding: 4px 8px; }}
    </style>
</head>
<body class="bg-gray-50 p-4 md:p-8">
    <!-- HTML Body (Keep as before) -->
    <div class="max-w-4xl mx-auto app-container">
        <div class="app-header"><h1 class="text-3xl font-bold text-gray-800">User Management</h1></div>
        <div class="p-4 md:p-6">
            <!-- Add Form -->
            <div class="bg-white rounded-10 p-6 shadow-sm border border-gray-100 mb-8">
                <form method="POST" action="/" enctype="multipart/form-data" id="addForm">
                     <input type="hidden" name="action" value="add">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <div><label class="block text-gray-700 mb-2 field-label">Name</label><input type="text" name="name" class="w-full p-2 border rounded-10 focus:outline-none focus:ring-2 focus:ring-blue-500" value=""></div>
                        <div><label class="block text-gray-700 mb-2 field-label">Age</label><input type="number" name="age" class="w-full p-2 border rounded-10" value=""></div>
                        <div><label class="block text-gray-700 mb-2 field-label">Sex</label><select name="sex" class="w-full p-2 border rounded-10"><option value="">Select</option><option value="Male">Male</option><option value="Female">Female</option><option value="Other">Other</option></select></div>
                        <div><label class="block text-gray-700 mb-2 field-label">Hobbies</label><select name="hobbies" multiple class="w-full p-2 border rounded-10">{{% for hobby in hobbies_list %}}<option value="{{{{ hobby }}}}">{{{{ hobby }}}}</option>{{% endfor %}}</select><p class="text-gray-500 text-sm mt-1">Hold Ctrl (or Cmd on Mac) to select multiple hobbies.</p></div>
                    </div>
                    <button type="submit" id="addButton" class="text-white px-4 py-2 rounded-10 transition-colors" disabled>Add User</button>
                </form>
            </div>
            <!-- Data Table -->
            <div class="bg-white rounded-10 p-6 shadow-sm border border-gray-100 mb-6">
                <form method="POST" action="/" id="dataForm">
                    <input type="hidden" name="action" id="form-action" value="">
                    <div class="table-container">
                        <table>
                            <thead><tr><th></th><th>Name</th><th>Age</th><th>Sex</th><th>Hobbies</th><th>Actions</th></tr></thead>
                            <tbody>
                                {{% for entry in data %}}
                                <tr>
                                    <td><input type="checkbox" name="selected" value="{{{{ entry['id'] }}}}"></td><td>{{{{ entry['name'] }}}}</td><td>{{{{ entry['age'] }}}}</td><td>{{{{ entry['sex'] }}}}</td><td>{{{{ ', '.join(entry['hobbies']) }}}}</td>
                                    <td><button type="button" onclick='openEditModal("{{{{ entry['id'] }}}}", "{{{{ entry['name']|escape }}}}" , "{{{{ entry['age'] }}}}", "{{{{ entry['sex'] }}}}", {{{{ entry['hobbies']|tojson|safe }}}})' class="bg-yellow-500 text-white px-2 py-1 rounded hover:bg-yellow-600 transition-colors">Edit</button></td>
                                </tr>{{% endfor %}}
                            </tbody>
                        </table>
                    </div>
                    <div class="mt-4 flex space-x-4"><button type="button" onclick="submitForm('delete')" class="bg-red-500 text-white px-4 py-2 rounded-10 hover:bg-red-600 transition-colors">Delete Selected</button></div>
                </form>
            </div>
        </div>
    </div>
    <!-- Edit Modal (keep as before) -->
    <div id="editModal" class="modal"><div class="modal-content"><h2 class="text-2xl font-bold mb-4">Edit User</h2><form method="POST" action="/" id="editForm"><input type="hidden" name="action" value="update"><input type="hidden" name="selected_id" id="edit-id"><div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6"><div><label class="block text-gray-700 mb-2 field-label">Name</label><input type="text" name="name" id="edit-name" class="w-full p-2 border rounded-10 focus:outline-none focus:ring-2 focus:ring-blue-500"></div><div><label class="block text-gray-700 mb-2 field-label">Age</label><input type="number" name="age" id="edit-age" class="w-full p-2 border rounded-10"></div><div><label class="block text-gray-700 mb-2 field-label">Sex</label><select name="sex" id="edit-sex" class="w-full p-2 border rounded-10"><option value="">Select</option><option value="Male">Male</option><option value="Female">Female</option><option value="Other">Other</option></select></div><div><label class="block text-gray-700 mb-2 field-label">Hobbies</label><select name="hobbies" multiple class="w-full p-2 border rounded-10 edit-hobbies">{{% for hobby in hobbies_list %}}<option value="{{{{ hobby }}}}">{{{{ hobby }}}}</option>{{% endfor %}}</select><p class="text-gray-500 text-sm mt-1">Hold Ctrl (or Cmd on Mac) to select multiple hobbies.</p></div></div><div class="flex justify-end space-x-4"><button type="button" onclick="closeEditModal()" class="bg-gray-500 text-white px-4 py-2 rounded-10 hover:bg-gray-600 transition-colors">Cancel</button><button type="submit" class="bg-green-500 text-white px-4 py-2 rounded-10 hover:bg-green-600 transition-colors">Save Changes</button></div></form></div></div>
    <script>
        // JavaScript (Keep as before)
        function submitForm(action) {{ document.getElementById('form-action').value = action; document.getElementById('dataForm').submit(); }}
        function openEditModal(id, name, age, sex, hobbies) {{ document.getElementById('edit-id').value = id; document.getElementById('edit-name').value = name; document.getElementById('edit-age').value = age; document.getElementById('edit-sex').value = sex; var hobbySelect = document.querySelector('.edit-hobbies'); for (var i = 0; i < hobbySelect.options.length; i++) {{ hobbySelect.options[i].selected = false; }}; if (hobbies && hobbies.length > 0) {{ for (var i = 0; i < hobbySelect.options.length; i++) {{ if (hobbies.includes(hobbySelect.options[i].value)) {{ hobbySelect.options[i].selected = true; }} }} }}; document.getElementById('editModal').style.display = 'block'; }}
        function closeEditModal() {{ document.getElementById('editModal').style.display = 'none'; }}
        window.onclick = function(event) {{ var modal = document.getElementById('editModal'); if (event.target == modal) {{ closeEditModal(); }} }}
        document.addEventListener('DOMContentLoaded', function() {{ const form = document.getElementById('addForm'); const addButton = document.getElementById('addButton'); const nameInput = form.querySelector('input[name="name"]'); const ageInput = form.querySelector('input[name="age"]'); const sexSelect = form.querySelector('select[name="sex"]'); const hobbiesSelect = form.querySelector('select[name="hobbies"]'); function checkFormValidity() {{ const nameFilled = nameInput.value.trim() !== ''; const ageFilled = ageInput.value.trim() !== ''; const sexFilled = sexSelect.value !== ''; const hobbiesFilled = Array.from(hobbiesSelect.selectedOptions).length > 0; addButton.disabled = !(nameFilled || ageFilled || sexFilled || hobbiesFilled); }}; nameInput.addEventListener('input', checkFormValidity); ageInput.addEventListener('input', checkFormValidity); sexSelect.addEventListener('change', checkFormValidity); hobbiesSelect.addEventListener('change', checkFormValidity); checkFormValidity(); }});
    </script>
</body>
</html>
'''

# --- Functions and Routes (Keep as before) ---
def save_data():
    try:
        with open(data_file, 'w') as f: json.dump(data, f, indent=4)
    except Exception as e: print(f"Error saving data to {data_file}: {e}")

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        action = request.form.get('action'); form_data = request.form
        try:
            if action == 'add':
                if not any([form_data.get('name'), form_data.get('age'), form_data.get('sex'), request.form.getlist('hobbies')]): print("Add skipped"); return redirect(url_for('home'))
                next_id = max([entry.get('id', 0) for entry in data] + [0]) + 1
                new_entry = {'id': next_id, 'name': form_data.get('name', '').strip(), 'age': form_data.get('age', '').strip(), 'sex': form_data.get('sex', ''), 'hobbies': request.form.getlist('hobbies')}
                data.append(new_entry); save_data()
            elif action == 'delete':
                selected_ids = request.form.getlist('selected')
                if selected_ids:
                    try: selected_ids_int = {int(id_str) for id_str in selected_ids}; data[:] = [entry for entry in data if entry.get('id') not in selected_ids_int]; save_data()
                    except ValueError: print("Error: Invalid ID for deletion.")
                else: print("Delete skipped: None selected.")
            elif action == 'update':
                selected_id_str = form_data.get('selected_id')
                if selected_id_str:
                    try:
                        selected_id = int(selected_id_str); entry_updated = False
                        for entry in data:
                            if entry.get('id') == selected_id: entry['name'] = form_data.get('name', '').strip(); entry['age'] = form_data.get('age', '').strip(); entry['sex'] = form_data.get('sex', ''); entry['hobbies'] = request.form.getlist('hobbies'); entry_updated = True; break
                        if entry_updated: save_data()
                        else: print(f"Update failed: ID {selected_id} not found.")
                    except ValueError: print(f"Update failed: Invalid ID '{selected_id_str}'.")
                else: print("Update skipped: No ID.")
        except Exception as e: print(f"POST Error: {e}")
        return redirect(url_for('home'))
    sorted_data = sorted(data, key=lambda x: x.get('id', 0))
    return render_template_string(template, data=sorted_data, hobbies_list=hobbies_list)

# --- Main Execution (Keep as before) ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)