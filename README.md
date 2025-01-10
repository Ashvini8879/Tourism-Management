
# Tourism Management System

The **Tourism Management System** is a comprehensive web application designed to streamline the process of exploring, booking, and managing tours for users while simplifying administrative tasks for tour operators. This platform aims to provide an efficient, user-friendly, and secure solution tailored to the travel industry.

---

## Features

- Explore a wide range of tours with detailed information.
- Flexible login systems for users and administrators:
  - **Users**: Comment on tours, add tours to a Wishlist, and book tours.
  - **Administrators**: Add, edit, and delete tour details dynamically.
- Secure payment integration with **Razorpay**.
- Automated email confirmation with tour details after successful booking.
- User-friendly interface with robust design and seamless functionality.
- Scalable and impactful solution for the travel industry.

---

## Technology Stack

### Front-End:
- **HTML**: Structures web page content, including the home page, user forms, and tour details.
- **CSS**: Styles the application, ensuring it is responsive and visually appealing.
- **JavaScript**: Adds interactivity, such as form validation and handling user actions.
- **Bootstrap**: Provides a responsive and professional design framework.

### Back-End:
- **Flask**: Python-based web framework for server-side logic, routing, and database interactions.
- **Python**: Processes business logic and facilitates communication between components.
- **SQLite**: Stores user information, tours, bookings, and admin data in a relational database.
- **Razorpay**: Handles secure and seamless payment processing.

---

## Installation and Setup Instructions

Follow these steps to set up and run the Tourism Management System:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ashvini8879/tourism-management-system.git
   ```
2. **Navigate to the Project Directory**:
   ```bash
   cd tourism-management-system
   ```
3. **Set Up the Database**:
   - Create a database with the required structure and appropriate names (refer to the project files for schema details).
   - Use SQLite as the database backend.
   
4. **Fill Necessary Credentials**:
   - Add your **Razorpay API keys**, email credentials, and database configurations in the respective files.

5. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the Application**:
   ```bash
   python main.py
   ```
7. **Access the Website**:
   Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## Usage

- **For Users**:
  - Browse tours and view detailed information.
  - Register and log in to comment, add tours to a Wishlist, or book tours.
  - Fill out the traveler form and proceed with payment.
  - Receive a confirmation email with booking details.

- **For Administrators**:
  - Log in to manage tours (add, edit, delete).
  - Keep the website up-to-date with the latest tours.

---




