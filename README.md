# BlueTide Property Management

A comprehensive Python-based property management application built with Flask.

## Features

✅ **User Authentication**
- Admin/Owner login system
- Role-based access control
- Session management

✅ **Service Management**
- Browse available services
- Submit service requests
- Track request status (pending/in progress/completed)
- Priority levels (low/medium/high)

✅ **Property Inventory**
- Manage properties and spaces
- Track inventory items with photos
- Organized by property → spaces → items

✅ **Notifications**
- Real-time administrator notifications
- Service request status updates
- Unread notification tracking

✅ **Dashboard**
- Overview of recent requests
- Quick action buttons
- Status summaries

## Screenshots

### Home Page
![Home Page](https://github.com/user-attachments/assets/67b61c0d-82bc-4eb5-8823-e949cfbd1c7c)

### Admin Dashboard
![Admin Dashboard](https://github.com/user-attachments/assets/77951995-6d9e-498b-be29-fa57084664f3)

### Notifications
![Notifications](https://github.com/user-attachments/assets/bccd913b-bf7c-49c8-a009-3772cf49f983)

## Tech Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Frontend**: Bootstrap 5 + Font Awesome
- **File Handling**: Werkzeug (for photo uploads)

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bluetide-pm
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser to `http://localhost:5000`

## Demo Credentials

The application comes with pre-configured demo accounts:

**Administrator Account:**
- Username: `admin`
- Password: `admin123`
- Permissions: Full access, can manage all service requests

**Property Owner Account:**
- Username: `owner1`
- Password: `owner123`
- Permissions: Can request services and view own properties

## Usage

### For Property Owners:
1. Login with owner credentials
2. Browse available services
3. Submit service requests with priority and description
4. Track request status in "My Requests"
5. View property inventory organized by spaces
6. Check notifications for updates

### For Administrators:
1. Login with admin credentials
2. View all service requests from all users
3. Update service request status (pending → in progress → completed)
4. Manage all properties and inventory
5. Receive notifications for new service requests

## Database Schema

The application uses the following main models:
- **User**: Admin and owner accounts
- **Property**: Properties managed in the system
- **Space**: Rooms/areas within properties
- **InventoryItem**: Items within spaces (with optional photos)
- **Service**: Available services for request
- **ServiceRequest**: Service requests with status tracking
- **Notification**: System notifications

## File Structure

```
bluetide-pm/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── .gitignore           # Git ignore rules
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── services.html
│   ├── request_service.html
│   ├── my_requests.html
│   ├── inventory.html
│   ├── spaces.html
│   ├── items.html
│   └── notifications.html
└── static/             # Static files
    ├── css/
    ├── js/
    └── uploads/        # Photo uploads
```

## Features Implemented

- [x] Owner/admin login system
- [x] List of available services
- [x] Service request functionality
- [x] Administrator notifications
- [x] Service status tracking (pending/in progress/completed)
- [x] Property inventory management
- [x] Photo attachment support for inventory items
- [x] Modular design with Users, Inventory, Services, and Notifications modules
- [x] Responsive web interface
- [x] Role-based access control

## Future Enhancements

- File upload functionality for inventory photos
- Email notifications
- Reporting and analytics
- Mobile app support
- Multi-tenant support for multiple property management companies
