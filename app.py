from flask import Flask, render_template_string, request, redirect, url_for
import json
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Replace with a secure key in production

# Load hobbies from CSV file
hobbies_file = os.path.join(os.path.dirname(__file__), 'hobbies.csv')
hobbies_df = pd.read_csv(hobbies_file)
hobbies_list = hobbies_df['hobby'].tolist()

# Data storage (you might want to use a database in production)
data = []
if os.path.exists('data.json'):
    with open('data.json', 'r') as f:
        data = json.load(f)

# HTML template as a string
template = '''
<!DOCTYPE html>
<html>
<head>
    <title>User Management</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: #f0f2f5;
        }
        .rounded-10 {
            border-radius: 10px;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        .modal-content {
            background-color: white;
            margin: 10% auto;
            padding: 20px;
            width: 60%;
            border-radius: 10px;
        }
        .app-container {
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            background-color: white;
            border: 1px solid #e5e7eb;
            max-height: 90vh;
            overflow-y: auto;
        }
        .app-header {
            background-color: #f8fafc;
            border-bottom: 1px solid #e5e7eb;
            padding: 1.5rem;
        }
        #addButton {
            width: 150px;
            background-color: #1a5e3b;
            transition: background-color 0.3s ease;
        }
        #addButton:disabled {
            background-color: #a3c9b5;
            opacity: 0.6;
            cursor: not-allowed;
        }
        #addButton:not(:disabled):hover {
            background-color: #2e7d55;
        }
        .field-label {
            font-weight: bold;
        }
        .table-container {
            max-height: 300px;
            overflow-y: auto;
            position: relative;
        }
        .table-container::-webkit-scrollbar {
            width: 8px;
        }
        .table-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        .table-container::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        .table-container::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        table {
            width: 100%;
            table-layout: fixed;
            border-collapse: collapse;
        }
        thead {
            position: sticky;
            top: 0;
            background-color: #f8fafc;
            z-index: 1;
        }
        th, td {
            border: 1px solid #e5e7eb;
            padding: 12px; /* Increased padding for better readability */
            text-align: left;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        /* Fixed column widths */
        th:nth-child(1), td:nth-child(1) { /* Checkbox column */
            width: 5%;
        }
        th:nth-child(2), td:nth-child(2) { /* Name column */
            width: 20%;
        }
        th:nth-child(3), td:nth-child(3) { /* Age column */
            width: 10%;
        }
        th:nth-child(4), td:nth-child(4) { /* Sex column */
            width: 10%;
        }
        th:nth-child(5), td:nth-child(5) { /* Hobbies column */
            width: 40%;
        }
        th:nth-child(6), td:nth-child(6) { /* Actions column */
            width: 15%;
        }
        /* Hobbies column with dynamic scrollbar */
        td:nth-child(5) {
            white-space: nowrap;
            overflow-x: auto;
            text-overflow: clip;
        }
        td:nth-child(5)::-webkit-scrollbar {
            height: 6px;
        }
        td:nth-child(5)::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        td:nth-child(5)::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        td:nth-child(5)::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        /* Alternate row colors */
        tbody tr:nth-child(odd) {
            background-color: #ffffff; /* White for odd rows */
        }
        tbody tr:nth-child(even) {
            background-color: #f9fafb; /* Light gray for even rows, matches theme */
        }
        /* Style for the hobbies dropdown */
        select[multiple] {
            height: 150px;
        }
    </style>
</head>
<body class="bg-gray-50 p-4 md:p-8">
    <div class="max-w-4xl mx-auto app-container">
        <div class="app-header">
            <h1 class="text-3xl font-bold text-gray-800">User Management</h1>
        </div>
        
        <div class="p-4 md:p-6">
            <!-- Add Form -->
            <div class="bg-white rounded-10 p-6 shadow-sm border border-gray-100 mb-8">
                <form method="POST" action="/" enctype="multipart/form-data" id="addForm">
                    <input type="hidden" name="action" value="add">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <div>
                            <label class="block text-gray-700 mb-2 field-label">Name</label>
                            <input type="text" name="name" class="w-full p-2 border rounded-10 focus:outline-none focus:ring-2 focus:ring-blue-500" value="">
                        </div>
                        <div>
                            <label class="block text-gray-700 mb-2 field-label">Age</label>
                            <input type="number" name="age" class="w-full p-2 border rounded-10" value="">
                        </div>
                        <div>
                            <label class="block text-gray-700 mb-2 field-label">Sex</label>
                            <select name="sex" class="w-full p-2 border rounded-10">
                                <option value="">Select</option>
                                <option value="Male">Male</option>
                                <option value="Female">Female</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-gray-700 mb-2 field-label">Hobbies</label>
                            <select name="hobbies" multiple class="w-full p-2 border rounded-10">
                                {% for hobby in hobbies_list %}
                                <option value="{{ hobby }}">{{ hobby }}</option>
                                {% endfor %}
                            </select>
                            <p class="text-gray-500 text-sm mt-1">Hold Ctrl (or Cmd on Mac) to select multiple hobbies.</p>
                        </div>
                    </div>
                    <button type="submit" id="addButton" class="text-white px-4 py-2 rounded-10 transition-colors" disabled>
                        Add User
                    </button>
                </form>
            </div>

            <!-- Data Table -->
            <div class="bg-white rounded-10 p-6 shadow-sm border border-gray-100 mb-6">
                <form method="POST" action="/" id="dataForm">
                    <input type="hidden" name="action" id="form-action" value="">
                    <div class="table-container">
                        <table class="w-full border rounded-10">
                            <thead class="bg-gray-100">
                                <tr>
                                    <th></th>
                                    <th>Name</th>
                                    <th>Age</th>
                                    <th>Sex</th>
                                    <th>Hobbies</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for entry in data %}
                                <tr>
                                    <td>
                                        <input type="checkbox" name="selected" value="{{ entry['id'] }}">
                                    </td>
                                    <td>{{ entry['name'] }}</td>
                                    <td>{{ entry['age'] }}</td>
                                    <td>{{ entry['sex'] }}</td>
                                    <td>{{ ', '.join(entry['hobbies']) }}</td>
                                    <td>
                                        <button type="button" 
                                            onclick='openEditModal("{{ entry['id'] }}", "{{ entry['name']|escape }}", "{{ entry['age'] }}", "{{ entry['sex'] }}", {{ entry['hobbies']|tojson|safe }})'
                                            class="bg-yellow-500 text-white px-2 py-1 rounded hover:bg-yellow-600 transition-colors">
                                            Edit
                                        </button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="mt-4 flex space-x-4">
                        <button type="button" onclick="submitForm('delete')" class="bg-red-500 text-white px-4 py-2 rounded-10 hover:bg-red-600 transition-colors">
                            Delete Selected
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Edit Modal -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <h2 class="text-2xl font-bold mb-4">Edit User</h2>
            <form method="POST" action="/" id="editForm">
                <input type="hidden" name="action" value="update">
                <input type="hidden" name="selected_id" id="edit-id">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div>
                        <label class="block text-gray-700 mb-2 field-label">Name</label>
                        <input type="text" name="name" id="edit-name" class="w-full p-2 border rounded-10 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-gray-700 mb-2 field-label">Age</label>
                        <input type="number" name="age" id="edit-age" class="w-full p-2 border rounded-10">
                    </div>
                    <div>
                        <label class="block text-gray-700 mb-2 field-label">Sex</label>
                        <select name="sex" id="edit-sex" class="w-full p-2 border rounded-10">
                            <option value="">Select</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 mb-2 field-label">Hobbies</label>
                        <select name="hobbies" multiple class="w-full p-2 border rounded-10 edit-hobbies">
                            {% for hobby in hobbies_list %}
                            <option value="{{ hobby }}">{{ hobby }}</option>
                            {% endfor %}
                        </select>
                        <p class="text-gray-500 text-sm mt-1">Hold Ctrl (or Cmd on Mac) to select multiple hobbies.</p>
                    </div>
                </div>
                <div class="flex justify-end space-x-4">
                    <button type="button" onclick="closeEditModal()" class="bg-gray-500 text-white px-4 py-2 rounded-10 hover:bg-gray-600 transition-colors">
                        Cancel
                    </button>
                    <button type="submit" class="bg-green-500 text-white px-4 py-2 rounded-10 hover:bg-green-600 transition-colors">
                        Save Changes
                    </button>
                </div>
            </form>
        </div>
    </div>

    <script>
        function submitForm(action) {
            document.getElementById('form-action').value = action;
            document.getElementById('dataForm').submit();
        }

        function openEditModal(id, name, age, sex, hobbies) {
            document.getElementById('edit-id').value = id;
            document.getElementById('edit-name').value = name;
            document.getElementById('edit-age').value = age;
            document.getElementById('edit-sex').value = sex;
            
            var hobbySelect = document.querySelector('.edit-hobbies');
            for (var i = 0; i < hobbySelect.options.length; i++) {
                hobbySelect.options[i].selected = false;
            }
            
            if (hobbies && hobbies.length > 0) {
                for (var i = 0; i < hobbySelect.options.length; i++) {
                    if (hobbies.includes(hobbySelect.options[i].value)) {
                        hobbySelect.options[i].selected = true;
                    }
                }
            }
            
            document.getElementById('editModal').style.display = 'block';
        }

        function closeEditModal() {
            document.getElementById('editModal').style.display = 'none';
        }

        window.onclick = function(event) {
            var modal = document.getElementById('editModal');
            if (event.target == modal) {
                closeEditModal();
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('addForm');
            const addButton = document.getElementById('addButton');
            const nameInput = form.querySelector('input[name="name"]');
            const ageInput = form.querySelector('input[name="age"]');
            const sexSelect = form.querySelector('select[name="sex"]');
            const hobbiesSelect = form.querySelector('select[name="hobbies"]');

            function checkFormValidity() {
                const nameFilled = nameInput.value.trim() !== '';
                const ageFilled = ageInput.value.trim() !== '';
                const sexFilled = sexSelect.value !== '';
                const hobbiesFilled = Array.from(hobbiesSelect.selectedOptions).length > 0;

                addButton.disabled = !(nameFilled || ageFilled || sexFilled || hobbiesFilled);
            }

            nameInput.addEventListener('input', checkFormValidity);
            ageInput.addEventListener('input', checkFormValidity);
            sexSelect.addEventListener('change', checkFormValidity);
            hobbiesSelect.addEventListener('change', checkFormValidity);

            checkFormValidity();
        });
    </script>
</body>
</html>
'''

def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            new_entry = {
                'id': len(data) + 1,
                'name': request.form.get('name', ''),
                'age': request.form.get('age', ''),
                'sex': request.form.get('sex', ''),
                'hobbies': request.form.getlist('hobbies')
            }
            data.append(new_entry)
            save_data()
            return redirect(url_for('home'))
        
        elif action == 'delete':
            selected_ids = request.form.getlist('selected')
            if selected_ids:
                data[:] = [entry for entry in data if str(entry['id']) not in selected_ids]
                save_data()
            return redirect(url_for('home'))
        
        elif action == 'update':
            selected_id = request.form.get('selected_id')
            if selected_id:
                for entry in data:
                    if str(entry['id']) == selected_id:
                        entry['name'] = request.form.get('name')
                        entry['age'] = request.form.get('age')
                        entry['sex'] = request.form.get('sex')
                        entry['hobbies'] = request.form.getlist('hobbies')
                        break
                save_data()
            return redirect(url_for('home'))
    
    return render_template_string(template, data=data, hobbies_list=hobbies_list)

# Run the app locally for development; this won't be used in production
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)