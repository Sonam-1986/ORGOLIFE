import os
import re

html_path = 'frontend/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Navigation and Landing Buttons
content = content.replace(
    '''<button class="nav-pill" onclick="navigate('donor-auth')">Donor</button>
    <button class="nav-pill" onclick="navigate('receiver-auth')">Receiver</button>''',
    '''<button class="nav-pill" onclick="navigate('user-auth')">Sign In / Register</button>'''
)

content = content.replace(
    '''<button class="btn-primary" onclick="navigate('donor-auth')">Register as Donor</button>
        <button class="btn-outline" onclick="navigate('receiver-auth')">I Need an Organ</button>''',
    '''<button class="btn-primary" onclick="authRedirect()">Get Started</button>'''
)

content = content.replace('''onclick="navigate('donor-auth')"''', '''onclick="authRedirect()"''')
content = content.replace('''onclick="navigate('receiver-auth')"''', '''onclick="authRedirect()"''')

# 2. Inject user-auth and user-dashboard pages
user_pages = """
<!-- ════════════════════════════════════════════════════════
     PAGE: USER AUTH
════════════════════════════════════════════════════════ -->
<div class="page" id="page-user-auth">
  <div class="form-page">
    <button class="form-back" onclick="navigate('landing')">← Back to Home</button>
    <div class="form-header">
      <h2>Welcome to OrgoLife</h2>
      <p>Login to your account or register as a new user.</p>
    </div>
    <div class="tab-bar">
      <button class="tab-btn active" id="userLoginTab" onclick="switchTab('user','login')">Sign In</button>
      <button class="tab-btn" id="userRegTab" onclick="switchTab('user','register')">Register</button>
    </div>

    <!-- USER LOGIN -->
    <div id="userLoginForm" class="form-card">
      <div class="form-group">
        <label>Email Address <span>*</span></label>
        <input type="email" class="form-control" id="uLoginEmail" placeholder="your@email.com">
      </div>
      <div class="form-group">
        <label>Password <span>*</span></label>
        <input type="password" class="form-control" id="uLoginPass" placeholder="••••••••">
      </div>
      <button class="btn-submit" onclick="userLogin()">Sign In</button>
    </div>

    <!-- USER REGISTER -->
    <div id="userRegForm" class="form-card" style="display:none">
      <div class="form-section-label">Personal Information</div>
      <div class="form-row">
        <div class="form-group"><label>Full Name <span>*</span></label><input class="form-control" id="uName" placeholder="Rahul Kumar"></div>
        <div class="form-group"><label>Phone <span>*</span></label><input class="form-control" id="uPhone" type="tel" placeholder="9876543210" maxlength="10" minlength="10" pattern="[0-9]{10}" inputmode="numeric"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Email <span>*</span></label><input type="email" class="form-control" id="uEmail" placeholder="rahul@email.com"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Password <span>*</span></label><input type="password" class="form-control" id="uPass" placeholder="Min 8 chars, A-Z, 0-9"></div>
        <div class="form-group"><label>Confirm Password <span>*</span></label><input type="password" class="form-control" id="uPassConfirm" placeholder="Repeat password"></div>
      </div>
      <button class="btn-submit" onclick="userRegister()">Create Account</button>
    </div>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════
     PAGE: USER DASHBOARD (BASE)
════════════════════════════════════════════════════════ -->
<div class="page" id="page-user-dashboard">
  <div class="dashboard">
    <div class="dashboard-header">
      <div class="dashboard-greeting">
        <h2>Welcome, <span id="baseUserName">User</span> 👋</h2>
        <p>Complete your profile to become a Donor or Receiver.</p>
      </div>
    </div>
    
    <div class="role-cards" id="upgradeCards">
      <div class="role-card donor" onclick="showUpgradeForm('donor')">
        <div class="role-icon">🫀</div>
        <h3>Become a Donor</h3>
        <p>Complete your profile with medical and identity documents to start saving lives.</p>
        <div class="role-card-action">Start Now →</div>
      </div>
      <div class="role-card receiver" onclick="showUpgradeForm('receiver')">
        <div class="role-icon">🔍</div>
        <h3>I Need an Organ</h3>
        <p>Register your health requirements to search for verified donors on our platform.</p>
        <div class="role-card-action">Register Need →</div>
      </div>
    </div>

    <!-- UPGRADE TO DONOR FORM -->
    <div id="upgradeDonorForm" class="form-card" style="display:none; max-width:800px; margin: 40px auto;">
        <button class="form-back" onclick="hideUpgradeForms()">← Back</button>
        <div class="form-header"><h2>Become a Donor (Step 1)</h2></div>
        <div class="form-row">
          <div class="form-group"><label>Age <span>*</span></label><input type="number" class="form-control" id="udAge" placeholder="18-70" min="18" max="70"></div>
          <div class="form-group"><label>Father's Name <span>*</span></label><input class="form-control" id="udFather"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>State <span>*</span></label><input class="form-control" id="udState"></div>
          <div class="form-group"><label>City <span>*</span></label><input class="form-control" id="udCity"></div>
        </div>
        <div class="form-group"><label>Full Address <span>*</span></label><input class="form-control" id="udAddress"></div>
        <div class="form-row">
          <div class="form-group"><label>Aadhaar Number</label><input class="form-control" id="udAadhaar"></div>
          <div class="form-group"><label>PAN Number</label><input class="form-control" id="udPan"></div>
        </div>
        <div class="form-section-label">Document Uploads</div>
        <div class="form-row">
          <div class="form-group"><label>Aadhaar Card <span>*</span></label><input type="file" id="udAadhaarFile" accept=".pdf,.jpg,.jpeg,.png"></div>
          <div class="form-group"><label>PAN Card <span>*</span></label><input type="file" id="udPanFile" accept=".pdf,.jpg,.jpeg,.png"></div>
        </div>
        <div class="form-group"><label>Medical Report <span>*</span></label><input type="file" id="udMedFile" accept=".pdf,.jpg,.jpeg,.png"></div>
        <button class="btn-submit" onclick="upgradeDonor()">Submit Profile</button>
    </div>

    <!-- UPGRADE TO RECEIVER FORM -->
    <div id="upgradeReceiverForm" class="form-card" style="display:none; max-width:800px; margin: 40px auto;">
        <button class="form-back" onclick="hideUpgradeForms()">← Back</button>
        <div class="form-header"><h2>Register as Receiver</h2></div>
        <div class="form-row">
          <div class="form-group"><label>Age <span>*</span></label><input type="number" class="form-control" id="urAge" placeholder="28"></div>
          <div class="form-group"><label>Father's Name <span>*</span></label><input class="form-control" id="urFather"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>State <span>*</span></label><input class="form-control" id="urState"></div>
          <div class="form-group"><label>City <span>*</span></label><input class="form-control" id="urCity"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Aadhaar Number</label><input class="form-control" id="urAadhaar"></div>
          <div class="form-group"><label>PAN Number</label><input class="form-control" id="urPan"></div>
        </div>
        <div class="form-section-label">Document Uploads</div>
        <div class="form-row">
          <div class="form-group"><label>Aadhaar Card <span>*</span></label><input type="file" id="urAadhaarFile" accept=".pdf,.jpg,.jpeg,.png"></div>
          <div class="form-group"><label>PAN Card <span>*</span></label><input type="file" id="urPanFile" accept=".pdf,.jpg,.jpeg,.png"></div>
        </div>
        <div class="form-group"><label>Medical Report <span>*</span></label><input type="file" id="urMedFile" accept=".pdf,.jpg,.jpeg,.png"></div>
        <button class="btn-sage" onclick="upgradeReceiver()">Submit Profile</button>
    </div>

  </div>
</div>
"""

# Extract everything between <body> and admin-auth to replace donor-auth and receiver-auth
auth_pattern = re.compile(r'<!-- ════════════════════════════════════════════════════════\s*PAGE: DONOR AUTH.*?<!-- ════════════════════════════════════════════════════════\s*PAGE: ADMIN AUTH', re.DOTALL)
content = auth_pattern.sub(user_pages + '\n<!-- ════════════════════════════════════════════════════════\n     PAGE: ADMIN AUTH', content)


# 3. Add Javascript Logic
js_additions = """
/* ════════════════════════════════════════════════════════
   USER BASE LOGIC
════════════════════════════════════════════════════════ */
function authRedirect() {
  if (!state.token) {
    navigate('user-auth');
  } else if (state.role === 'donor') {
    navigate('donor-dashboard');
  } else if (state.role === 'receiver') {
    navigate('receiver-dashboard');
  } else if (state.role === 'user') {
    navigate('user-dashboard');
  } else if (state.role === 'hospital_admin') {
    navigate('admin-dashboard');
  }
}

async function userLogin() {
  const email = document.getElementById('uLoginEmail').value.trim();
  const password = document.getElementById('uLoginPass').value;
  if (!email || !password) { toast('Please fill all fields.', 'error'); return; }
  const btn = event.currentTarget || document.activeElement;
  btn.disabled = true; btn.textContent = 'Signing in...';
  try {
    const data = await apiCall('/auth/login', 'POST', { email, password });
    saveAuth(data);
    authRedirect();
    toast(`Welcome back, ${data.name}!`, 'success');
  } catch(e) { toast(e.message, 'error'); }
  finally { btn.disabled = false; btn.textContent = 'Sign In'; }
}

async function userRegister() {
  const name = document.getElementById('uName').value.trim();
  const email = document.getElementById('uEmail').value.trim();
  const phone = document.getElementById('uPhone').value.trim();
  const password = document.getElementById('uPass').value;
  const confirm = document.getElementById('uPassConfirm').value;
  if (!name || !email || !phone || !password) { toast('Please fill all required fields.', 'error'); return; }
  if (password !== confirm) { toast('Passwords do not match.', 'error'); return; }
  
  const btn = event.currentTarget || document.activeElement;
  btn.disabled = true; btn.textContent = 'Registering...';
  try {
    await apiCall('/auth/register', 'POST', { name, email, password, contact_number: phone });
    // auto login
    const loginData = await apiCall('/auth/login', 'POST', { email, password });
    saveAuth(loginData);
    authRedirect();
    toast('Account created successfully!', 'success');
  } catch(e) { toast(e.message, 'error'); }
  finally { btn.disabled = false; btn.textContent = 'Create Account'; }
}

function showUpgradeForm(type) {
  document.getElementById('upgradeCards').style.display = 'none';
  if(type === 'donor') document.getElementById('upgradeDonorForm').style.display = 'block';
  if(type === 'receiver') document.getElementById('upgradeReceiverForm').style.display = 'block';
}

function hideUpgradeForms() {
  document.getElementById('upgradeCards').style.display = 'flex';
  document.getElementById('upgradeDonorForm').style.display = 'none';
  document.getElementById('upgradeReceiverForm').style.display = 'none';
}

async function upgradeDonor() {
  const age = document.getElementById('udAge').value;
  const father_name = document.getElementById('udFather').value.trim();
  const stateVal = document.getElementById('udState').value.trim();
  const city = document.getElementById('udCity').value.trim();
  const address = document.getElementById('udAddress').value.trim();
  const aadhaar = document.getElementById('udAadhaar').value.trim();
  const pan = document.getElementById('udPan').value.trim().toUpperCase();
  const aadhaarFile = document.getElementById('udAadhaarFile').files[0];
  const panFile = document.getElementById('udPanFile').files[0];
  const medFile = document.getElementById('udMedFile').files[0];

  if (!age||!father_name||!stateVal||!city||!address||!aadhaarFile||!panFile||!medFile) {
    toast('Please fill all required fields and upload all documents.', 'error'); return;
  }

  const fd = new FormData();
  fd.append('age', age); fd.append('father_name', father_name);
  fd.append('state', stateVal); fd.append('city', city); fd.append('full_address', address);
  if (aadhaar) fd.append('aadhaar_number', aadhaar);
  if (pan) fd.append('pan_number', pan);
  fd.append('aadhaar_file', aadhaarFile);
  fd.append('pan_file', panFile);
  fd.append('medical_file', medFile);

  try {
    const regData = await apiCall('/donors/register', 'POST', fd, true);
    state.role = 'donor';
    localStorage.setItem('ol_role', 'donor');
    toast('Profile updated to Donor!', 'success');
    navigate('donor-dashboard');
  } catch(e) { toast(e.message, 'error'); }
}

async function upgradeReceiver() {
  const age = document.getElementById('urAge').value;
  const father_name = document.getElementById('urFather').value.trim();
  const stateVal = document.getElementById('urState').value.trim();
  const city = document.getElementById('urCity').value.trim();
  const aadhaar = document.getElementById('urAadhaar').value.trim();
  const pan = document.getElementById('urPan').value.trim().toUpperCase();
  const aadhaarFile = document.getElementById('urAadhaarFile').files[0];
  const panFile = document.getElementById('urPanFile').files[0];
  const medFile = document.getElementById('urMedFile').files[0];

  if (!age||!father_name||!stateVal||!city||!aadhaarFile||!panFile||!medFile) {
    toast('Please fill all required fields and upload all documents.', 'error'); return;
  }

  const fd = new FormData();
  fd.append('age', age); fd.append('father_name', father_name);
  fd.append('state', stateVal); fd.append('city', city);
  if (aadhaar) fd.append('aadhaar_number', aadhaar);
  if (pan) fd.append('pan_number', pan);
  fd.append('aadhaar_file', aadhaarFile);
  fd.append('pan_file', panFile);
  fd.append('medical_file', medFile);

  try {
    const regData = await apiCall('/receivers/register', 'POST', fd, true);
    state.role = 'receiver';
    localStorage.setItem('ol_role', 'receiver');
    toast('Profile updated to Receiver!', 'success');
    navigate('receiver-dashboard');
  } catch(e) { toast(e.message, 'error'); }
}

function saveAuth(data) {
  state.token = data.access_token;
  state.role = data.role;
  state.userName = data.name;
  localStorage.setItem('ol_token', data.access_token);
  localStorage.setItem('ol_role', data.role);
  localStorage.setItem('ol_name', data.name);
  updateNav();
}
"""

js_pattern = re.compile(r'function switchTab\(portal, tab\) \{.*?\n\}', re.DOTALL)
def switchTab_replace(match):
    original = match.group(0)
    new_fn = """function switchTab(portal, tab) {
  const prefixes = { user: 'user', donor: 'donor', receiver: 'rec', admin: 'admin' };
  const p = prefixes[portal];
  document.getElementById(p+'LoginTab').classList.toggle('active', tab==='login');
  document.getElementById(p+'RegTab').classList.toggle('active', tab==='register');
  document.getElementById(p+'LoginForm').style.display = tab==='login' ? 'block' : 'none';
  document.getElementById(p+'RegForm').style.display = tab==='register' ? 'block' : 'none';
}"""
    return new_fn

content = js_pattern.sub(switchTab_replace, content)

# Inject JS before the End
content = content.replace('/* ════════════════════════════════════════════════════════\n   ADMIN LOGIN & REGISTER', js_additions + '\n/* ════════════════════════════════════════════════════════\n   ADMIN LOGIN & REGISTER')

# Delete old donorLogin, donorRegisterStep1, receiverLogin, receiverRegister functions from original JS to avoid confusion (optional, but cleaner)
del_pattern_1 = re.compile(r'/\* ════════════════════════════════════════════════════════\s*DONOR LOGIN.*?/\* ════════════════════════════════════════════════════════\s*DONOR DASHBOARD', re.DOTALL)
content = del_pattern_1.sub('/* ════════════════════════════════════════════════════════\n   DONOR DASHBOARD', content)

del_pattern_2 = re.compile(r'/\* ════════════════════════════════════════════════════════\s*RECEIVER LOGIN & REGISTER.*?/\* ════════════════════════════════════════════════════════\s*RECEIVER DASHBOARD / SEARCH', re.DOTALL)
content = del_pattern_2.sub('/* ════════════════════════════════════════════════════════\n   RECEIVER DASHBOARD / SEARCH', content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Frontend refactored.')
