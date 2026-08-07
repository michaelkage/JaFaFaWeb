# JaFaFaWeb

A modern **Telemetry Hub** web application for searching, analyzing, and monitoring vehicle telemetry data. Built as a responsive HTML-based portal with Google OAuth authentication.

## 🎯 Overview

JaFaFaWeb is a customer-facing telemetry dashboard that allows authorized users to:
- Search and manage customer accounts
- View registered vehicle fleets
- Access real-time telemetry data and analytics
- Analyze vehicle performance metrics (speed, temperature, fuel level, etc.)
- Filter telemetry logs based on custom criteria

## 🚀 Features

### Authentication
- **Google OAuth Integration**: Secure sign-in using Google accounts
- User profile display with avatar and email
- Session management and sign-out functionality

### Customer Management
- Dropdown search for customers by name, email, or company
- Display customer tier levels (Enterprise, Pro)
- View registered vehicle count per customer
- Company and contact information display

### Vehicle Registry
- Search vehicles within customer accounts
- Filter by make, model, year, or plate number
- Display vehicle status (Active, In Service)
- View current mileage information

### Telemetry Dashboard
- Real-time vehicle metrics display:
  - Current speed (mph)
  - Fuel/Battery level (%)
  - Engine temperature (°F)
  
- Advanced filtering options:
  - Minimum speed filters (All Speeds, Cruising ≥40mph, High Speed ≥75mph)
  - Metric-based filters (All Logs, Speed Alerts >75mph, Thermal Warnings >200°F)
  
- Comprehensive telemetry table with columns:
  - Timestamp
  - Speed
  - Engine RPM
  - Temperature
  - Fuel/Battery Level
  - Vehicle Location

## 🏗️ Technical Stack

- **Frontend**: Pure HTML5 with embedded CSS and JavaScript
- **Authentication**: Google Sign-In API (GSI)
- **Data Storage**: Client-side mock database (MOCK_DATABASE)
- **Styling**: Custom CSS with dark theme design
- **Browser**: Modern browsers with ES6 support

## 📋 Project Structure

```
JaFaFaWeb/
└── index.html          # Single-page application with all UI, styles, and scripts
```

## 🎨 Design Features

- **Dark Theme**: Professional dark mode interface with slate and cyan accents
- **Responsive Layout**: Mobile-friendly design with flexible grid layouts
- **Intuitive Navigation**: Breadcrumb navigation and "Back" buttons for easy traversal
- **Accessible UI**: Status badges, color-coded alerts, and clear visual hierarchy

## 🔐 Security Notes

- Google OAuth for user authentication
- Input sanitization with `escapeHtml()` function to prevent XSS attacks
- Client-side mock data (for development/demo purposes)

## 📱 Three-Screen Flow

1. **Customer Lookup Screen**
   - Search and select customers
   - View customer summary card
   - Proceed to vehicle registry

2. **Vehicle Registry Screen**
   - Browse customer's fleet
   - View vehicle details
   - Launch telemetry dashboard

3. **Telemetry Dashboard Screen**
   - Monitor real-time vehicle metrics
   - Apply custom filters to telemetry data
   - Analyze historical vehicle performance

## 🧪 Mock Data

The application includes sample data for:
- **5 Customers**: Deji Ayeni, Morenike Ayeni, Michael Ayeni, Gabriel Blitzer, Elizabeth Ayeni
- **20+ Vehicles**: Luxury and standard vehicles with telemetry logs
- **Realistic Locations**: Lagos-based locations (Third Mainland Bridge, Lekki Expressway, etc.)
- **Sample Telemetry**: Speed, RPM, temperature, fuel levels, and timestamps

## 🚀 Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/michaelkage/JaFaFaWeb.git
   cd JaFaFaWeb
   ```

2. **Open in browser**:
   ```bash
   open index.html
   # or
   python -m http.server 8000  # if you need a local server
   ```

3. **Sign in** with a Google account to explore the dashboard

## 🔧 Future Enhancements

- Backend API integration to replace mock database
- Real-time WebSocket updates for telemetry data
- Database persistence for customer and vehicle data
- Advanced analytics and reporting features
- Export functionality for telemetry reports
- Multi-language support
- Dark/Light theme toggle

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests to improve the application.

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

Created by **michaelkage** as part of the JaFaFa telemetry platform.

---

**Note**: This is the web-based version of the JaFaFa telemetry suite. See [JaFaFaFQ](https://github.com/dhippo78/JaFaFaFQ) for the C# backend implementation.
