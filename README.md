# HR Dashboard Sharing System using AWS, Python & SendGrid

## 📌 Project Summary

A scalable backend system that enables HR Practitioners to **create**, **view**, and **share dashboards** with managers. Dashboards track:

* Headcount
* Payroll Cost
* Total Overtime Hours

When shared, email notifications are automatically sent to selected managers.

![Architecture Diagram](architecture_diagram.png)

---

## 👤 Personas

* **HR Practitioners**: Create, View, and Share dashboards
* **Managers**: Receive email notifications upon sharing

---

## 🧰 Technologies Used

* **AWS Lambda** – Stateless compute logic
* **API Gateway** – Expose HTTP endpoints (Postman-compatible)
* **DynamoDB** – NoSQL store for dashboard metadata
* **SNS** – Publishes messages to trigger email dispatcher
* **SendGrid** – Sends actual notification emails
* **CloudWatch** – Logging & monitoring

---

## 🗃️ Folder Structure

```text
adp_dashboard_project/
├── architecture.txt
├── db_schema.txt
├── api_spec.txt
├── README.md
├── postman_collection.json
├── lambda/
│   ├── create_dashboard.py
│   ├── view_dashboard.py
│   ├── share_dashboard.py
│   └── email_dispatcher.py
```

---

## 🔐 IAM Permissions

Each Lambda function is attached to an IAM role with:

* `AmazonDynamoDBFullAccess`
* `AmazonSNSFullAccess`
* `AWSLambdaBasicExecutionRole`

---

## 🌐 API Endpoints

| Method | Endpoint                         | Description                   |
| ------ | -------------------------------- | ----------------------------- |
| POST   | /dashboard/create                | Create a new dashboard        |
| GET    | /dashboard/{dashboard\_id}       | View dashboard details        |
| POST   | /dashboard/share/{dashboard\_id} | Share dashboard with managers |

---

## 📩 Email Notification Format

* **Subject**: `Dashboard Shared Notification`
* **Body**: `You’ve been granted access to dashboard <dashboard_id>`

---

## ✅ Completed Features

* [x] Create Dashboard (Lambda + DynamoDB)
* [x] View Dashboard (Lambda + API Gateway)
* [x] Share Dashboard (Lambda + SNS)
* [x] Email Dispatcher (Lambda + SendGrid)
* [x] Fully Testable with Postman

---

## ⚠️ Note on Scalability

For large manager lists (e.g., 15,000+), storing all emails in the `shared_with` array may exceed DynamoDB’s 400KB item size limit.  
👉 **In production**, move `shared_with` into a separate table (e.g., `SharedAccess`) with `dashboard_id` as the partition key.

---


## 🧪 Postman Testing Guide

1. **Create Dashboard**

```http
POST /dashboard/create
```

```json
{
  "created_by": "hr1@adp.com",
  "name": "Payroll Snapshot - May 2025",
  "headcount": 120,
  "payroll_cost": 95000,
  "overtime_hours": 320
}
```

2. **View Dashboard**

```http
GET /dashboard/{dashboard_id}
```

3. **Share Dashboard**

```http
POST /dashboard/share/{dashboard_id}
```

```json
{
  "shared_with": ["manager1@example.com", "manager2@example.com"]
}
```

---

## 🚀 Future Improvements

* Add authentication (Cognito or JWT)
* Add input validation
* Rate limiting & monitoring
* Create frontend or UI wrapper

---

📁 Fully tested
🧉 Built for real-world use
📩 Email scaled for 15,000 recipients
