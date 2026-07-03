# BloodBridge: Optimizing Lifesaving Resources

> **A Cloud-Native Blood Donation Management System**
> 
> Built with Python Flask, MySQL, and AWS Architecture Concepts

---

## Project Overview

**BloodBridge** is a full-stack healthcare web application designed to optimize blood donation and emergency blood request management. The system connects four key stakeholders - **Administrators**, **Donors**, **Hospitals**, and **Blood Bank Managers** - through a unified cloud-powered platform.

This project demonstrates:
- Modern web application development with Flask
- MySQL database design and management
- Professional healthcare UI/UX design
- AWS Cloud Architecture concepts (EC2 + RDS)
- Multi-role authentication and session management
- Real-time inventory tracking and analytics

---

## AWS Cloud Architecture

```
Users (Web/Mobile)
    |
    v
Route 53 (DNS + Health Checks)
    |
    v
CloudFront (CDN + SSL/TLS)
    |
    v
AWS WAF + Shield (DDoS Protection)
    |
    v
Application Load Balancer (ALB)
    |
    v
EC2 Auto-Scaling Group (Flask App)
    |
    v
RDS MySQL (Multi-AZ + Backups)
```

**Architecture Highlights:**
- **EC2**: Auto-scaling compute instances running the Flask application
- **RDS**: Managed MySQL database with Multi-AZ deployment for high availability
- **ALB**: Application Load Balancer for traffic distribution
- **CloudFront**: Content delivery network with edge caching
- **WAF + Shield**: Web application firewall and DDoS protection
- **VPC**: Virtual private cloud with security groups and NACLs
- **CloudWatch**: Monitoring and logging

---

## Features

### 1. Authentication System
- Multi-role login (Admin, Donor, Hospital, Blood Bank Manager)
- Secure password hashing with Werkzeug
- Session-based authentication
- Flash messaging system

### 2. Admin Dashboard
- System overview with analytics charts
- User management (view all users and donors)
- Blood request management (approve/reject/fulfill)
- Real-time inventory monitoring
- Dashboard statistics and trends

### 3. Donor Dashboard
- Personal profile management
- Donation eligibility checker (56-day rule)
- Upcoming blood drives listing
- Matching blood requests notification
- Donation history tracking
- Blood drive scheduling

### 4. Hospital Dashboard
- Emergency blood request creation
- Request status tracking
- Available donors listing
- Blood inventory overview
- Priority-based request system (Low/Medium/High/Critical)

### 5. Blood Bank Dashboard
- Real-time inventory management
- Stock update (add/remove units)
- Low stock alerts and warnings
- All requests overview
- Blood group-wise stock tracking

### 6. Public Pages
- Home page with live statistics
- Emergency requests listing
- Public blood inventory view
- AWS Architecture documentation
- Contact page

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript |
| **Backend** | Python 3.8+, Flask |
| **Database** | MySQL 8.0 |
| **ORM/DB** | Flask-MySQLdb |
| **Security** | Werkzeug (password hashing) |
| **Charts** | Chart.js |
| **Icons** | Font Awesome 6 |
| **Fonts** | Google Fonts (Inter, Poppins) |
| **Cloud** | AWS EC2, RDS (architecture demo) |

---


