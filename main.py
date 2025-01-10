### main.py ###


from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from bs4 import BeautifulSoup
from sqlalchemy.orm import joinedload
from flask_login import login_required
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# For adding profile images to the comment section
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///tour.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
# Tour model with a foreign key to User
class Tour(db.Model):
    __tablename__ = "Tour_information"
    id = db.mapped_column(db.Integer, primary_key=True)
    title = db.mapped_column(db.String(250), unique=True, nullable=False)
    author_id = db.mapped_column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Other fields for Tour
    destination = db.mapped_column(db.String(250), nullable=False)
    img_url = db.mapped_column(db.String(250), nullable=False)
    days = db.mapped_column(db.Integer, nullable=False)
    tour_operator = db.mapped_column(db.String(50), nullable=False)
    max_group_size = db.mapped_column(db.Integer, nullable=False)
    age_range = db.mapped_column(db.String(50), nullable=False)
    operated_in = db.mapped_column(db.String(100), nullable=False)
    tour_id = db.mapped_column(db.String(50), unique=True, nullable=False)
    places_youll_see = db.mapped_column(db.Text, nullable=False)
    highlights = db.mapped_column(db.Text, nullable=False)
    date = db.mapped_column(db.String(250), nullable=False)

    # Foreign key relationship to User
    author = db.relationship("User", back_populates="posts")

    # Relationship to Itinerary using primaryjoin on tour_id
    itinerary = db.relationship(
        "Itinerary",
        back_populates="parent_post",
        primaryjoin="Tour.tour_id == foreign(Itinerary.tour_id)",
        cascade="all, delete-orphan"
    )

    # Relationship to Comment
    comments = db.relationship(
        "Comment",
        back_populates="parent_post",
        cascade="all, delete-orphan"
    )

    # Relationship to WishlistItem
    wishlist_items = db.relationship("WishlistItem", back_populates="post")

  

class Traveler(db.Model):
    __tablename__ = "Traveller_Details"
    id = db.Column(db.Integer, primary_key=True)
    tour_name = db.Column(db.String(100), nullable=False)
    tour_date = db.Column(db.String(100), nullable=False)
    tour_price = db.Column(db.Float, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    nationality = db.Column(db.String(50), nullable=False)


   

class Itinerary(db.Model):
    __tablename__ = "itineraries_data"
    id = mapped_column(Integer, primary_key=True)
    day = mapped_column(Integer, nullable=False)
    title = mapped_column(Text, nullable=False)
    description = mapped_column(Text, nullable=False)
    tour_id = mapped_column(String(50), db.ForeignKey("Tour_information.tour_id"), nullable=False)

    # Back-populated relationship to Tour
    parent_post = relationship("Tour", back_populates="itinerary")




# Create a User table for all your registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    # This will act like a list of Tour objects attached to each User.
    # The "author" refers to the author property in the Tour class.
    posts = relationship("Tour", back_populates="author")
    # Parent relationship: "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")
    # Relationship to Tour
    posts = relationship("Tour", back_populates="author", cascade="all, delete-orphan")

    wishlist_items = relationship("WishlistItem", back_populates="user")

# Create a table for the comments on the blog posts
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # Child relationship:"users.id" The users refers to the tablename of the User class.
    # "comments" refers to the comments property in the User class.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    # Child Relationship to the BlogPosts
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("Tour_information.id"))
    parent_post = relationship("Tour", back_populates="comments")

class WishlistItem(db.Model):
    __tablename__ = "wishlist_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("Tour_information.id"))

    # Relationships
    user = relationship("User", back_populates="wishlist_items")
    post = relationship("Tour", back_populates="wishlist_items")

with app.app_context():
    db.create_all()

# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function

# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form, current_user=current_user)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))

    return render_template("login.html", form=form, current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if query:
        # Search blog posts by title
        results = Tour.query.filter(Tour.destination.ilike(f"%{query}%")).all()
        return render_template('index.html', all_posts=results, query=query)
    else:
        # If no query, redirect to the main page
        return redirect(url_for('get_all_posts'))
    
@app.route('/')
def get_all_posts():
    # Use joinedload to eagerly load comments and itineraries
    result = db.session.execute(
        db.select(Tour).options(joinedload(Tour.comments), joinedload(Tour.itinerary))
    )
    
    # Use unique() to avoid duplicates
    posts = result.scalars().unique().all()
    
    return render_template("index.html", all_posts=posts, current_user=current_user,on_confirmation_page=False)

# Add a POST method to be able to post comments
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(Tour, post_id)
    # Add the CommentForm to the route
    comment_form = CommentForm()

   
    # Extract images from the 'places' field (assuming CKEditor content is stored here)
    places_html = requested_post.places_youll_see  # Assuming 'places' is a field in Tour
    soup = BeautifulSoup(places_html, 'html.parser')
    headline = soup.find_all('p')
    images = soup.find_all('img')

    headlines = [h.get_text() for h in headline] 
    image_urls = [img['src'] for img in images]  # List of image URLs

     # Align headlines and image_urls based on the shortest list
    min_length = min(len(headlines), len(image_urls))
    headlines = headlines[:min_length]
    image_urls = image_urls[:min_length]

    # Only allow logged-in users to comment on posts
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form,image_urls=image_urls,headlines=headlines)



# Use a decorator so only an admin user can create new posts
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if isinstance(form.highlights.data, list):
        highlights_text = "\n".join(form.highlights.data)
    else:
        # If not a list, assume it’s a string or convert it to string
        highlights_text = str(form.highlights.data)
    if form.validate_on_submit():
        new_post = Tour(
            title=form.title.data,
            days=form.days.data,
            destination=form.destination.data,
            tour_operator=form.tour_operator.data,
            img_url=form.img_url.data,

            max_group_size=form.max_group_size.data,
            age_range=form.age_range.data,
            operated_in=form.operated_in.data,

            tour_id=form.tour_id.data,
            places_youll_see=form.places_youll_see.data,
            highlights=highlights_text,
           

            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        
        db.session.commit()
        # return redirect(url_for("get_all_posts"))
        return render_template("itinerary.html",tour_id=new_post.tour_id)
    return render_template("make-post.html", form=form, current_user=current_user)

@app.route('/create-itinerary', methods=['GET', 'POST'])
def create_itinerary():
    if request.method == 'POST':
        tour_id = request.form.get("tour_id")  # Get tour_id from form

        # Get itinerary data
        day_titles = request.form.getlist("itinerary-day[]")
        day_descriptions = request.form.getlist("itinerary-description[]")
        
        for day_num, (title, description) in enumerate(zip(day_titles, day_descriptions), start=1):
            itinerary_day = Itinerary(
                day=day_num,
                title=title,
                description=description,
                tour_id=tour_id  # Save tour ID with each day entry
            )
            db.session.add(itinerary_day)

        db.session.commit()
        return redirect(url_for('get_all_posts'))  # Redirect to a page showing all itineraries

    return render_template('itinerary.html')

@app.route('/add-to-wishlist/<int:post_id>', methods=["POST"])
def add_to_wishlist(post_id):
    # Ensure the user is logged in
    if not current_user.is_authenticated:
        flash("You need to log in or register to add items to your wishlist.")
        return redirect(url_for("login"))

    # Check if the item already exists in the wishlist
    existing_item = WishlistItem.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if not existing_item:
        # Add the new item to the wishlist
        new_item = WishlistItem(user_id=current_user.id, post_id=post_id)
        db.session.add(new_item)
        db.session.commit()
        flash("Item added to your wishlist.")
    else:
        flash("Item is already in your wishlist.")

    return redirect(url_for('show_post', post_id=post_id))



@app.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', wishlist_items=wishlist_items)

@app.route('/booked_traveller')
@login_required
def booked_traveller():
    # Fetch all traveler records from the database
    travelers = Traveler.query.all()

    # Render a template and pass the traveler data to it
    return render_template('booked_traveller.html', travelers=travelers)


@app.route('/remove-from-wishlist/<int:item_id>', methods=['POST'])
@login_required
def remove_from_wishlist(item_id):
    item_to_remove = WishlistItem.query.get_or_404(item_id)
    if item_to_remove.user_id == current_user.id:
        db.session.delete(item_to_remove)
        db.session.commit()
        return redirect(url_for('wishlist', message="Item removed from your wishlist."))
    else:
        return redirect(url_for('wishlist', error="You do not have permission to remove this item."))




# Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(Tour, post_id)  # Get the post to edit or return 404 if not found
    edit_form = CreatePostForm(
        title=post.title,
        days=post.days,
        destination=post.destination,
        tour_operator=post.tour_operator,
        img_url=post.img_url,
        max_group_size=post.max_group_size,
        age_range=post.age_range,
        operated_in=post.operated_in,
        tour_id=post.tour_id,
        places_youll_see=post.places_youll_see,
        highlights=post.highlights  # Assuming highlights are stored as a newline-separated string
    )

    if edit_form.validate_on_submit():  # If form is valid on submission
        # Update the post with new values from the form
        post.title = edit_form.title.data
        post.days = edit_form.days.data
        post.destination = edit_form.destination.data
        post.tour_operator = edit_form.tour_operator.data
        post.img_url = edit_form.img_url.data
        post.max_group_size = edit_form.max_group_size.data
        post.age_range = edit_form.age_range.data
        post.operated_in = edit_form.operated_in.data
        post.tour_id = edit_form.tour_id.data
        post.places_youll_see = edit_form.places_youll_see.data

        # Handle highlights as a list or string
        if isinstance(edit_form.highlights.data, list):
            post.highlights = "\n".join(edit_form.highlights.data)
        else:
            post.highlights = str(edit_form.highlights.data)

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the post's detail page
        return redirect(url_for("show_post", post_id=post.id))

    # Render the form with pre-filled values for editing
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


# Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(Tour, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)

@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user)

# Sample data for months, dates, and prices
available_departures = {
    "November 2024": [
        {"date": "Nov 5, 2024", "price": 999},
        {"date": "Nov 12, 2024", "price": 1100},
    ],
    "December 2024": [
        {"date": "Dec 10, 2024", "price": 1220},
        {"date": "Dec 25, 2024", "price": 1310},
    ],
    "January 2025": [
        {"date": "Jan 15, 2025", "price": 1150},
        {"date": "Jan 20, 2025", "price": 1425},
    ]
}

@app.route('/get_dates/<month>')
def get_dates(month):
    dates = available_departures.get(month, [])
    return jsonify(dates)

@app.route('/confirmation/post/<int:post_id>')
def confirmation(post_id):
    post = db.get_or_404(Tour, post_id)
    date = request.args.get('date')
    price = request.args.get('price')
    return render_template('confirmation.html', post=post,date=date, price=price,on_confirmation_page=True)



@app.route('/submit_travelers', methods=['POST'])
def submit_travelers():
    # Extract form data
    tour_name = request.form.get('tourName')
    tour_date = request.form.get('tourDate')
    tour_price = request.form.get('tourPrice')
    lead_first_name = request.form.get('leadFirstName')
    lead_last_name = request.form.get('leadLastName')
    lead_email = request.form.get('leadEmail')
    lead_phone = request.form.get('leadPhone')
    lead_dob = request.form.get('leadDobDay')
    lead_gender = request.form.get('leadGender')
    lead_nationality = request.form.get('leadNationality')
    traveler_count = int(request.form.get('travelerCount'))
    total_price = float(tour_price) * traveler_count

    try:
        # Store lead traveler in the database
        lead_traveler = Traveler(
            tour_name=tour_name,
            tour_date=tour_date,
            tour_price=float(tour_price),
            first_name=lead_first_name,
            last_name=lead_last_name,
            email=lead_email,
            phone=lead_phone,
            dob=datetime.strptime(lead_dob, '%Y-%m-%d').date(),
            gender=lead_gender,
            nationality=lead_nationality
        )
        db.session.add(lead_traveler)

        # Process and store additional travelers
        for i in range(2, traveler_count + 1):
            traveler_first_name = request.form.get(f'traveler{i}FirstName')
            traveler_last_name = request.form.get(f'traveler{i}LastName')
            traveler_dob = request.form.get(f'traveler{i}DobDay')
            traveler_gender = request.form.get(f'traveler{i}Gender')

            traveler = Traveler(
                tour_name=tour_name,
                tour_date=tour_date,
                tour_price=float(tour_price),
                first_name=traveler_first_name,
                last_name=traveler_last_name,
                email=lead_email,  # Assuming all travelers share lead email
                phone=lead_phone,
                dob=datetime.strptime(traveler_dob, '%Y-%m-%d').date(),
                gender=traveler_gender,
                nationality=lead_nationality
            )
            db.session.add(traveler)

        # Commit all changes to the database
        db.session.commit()

        # SMTP server configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = ""  # Replace with your email
        sender_password = ""  # Replace with your password

        # Create the email
        subject = "Your Trip Details"
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = lead_email
        message['Subject'] = subject

        # Email body
        body = f"""
        Hello {lead_first_name} {lead_last_name},
        
        Thank you for booking your trip with us! Here are your details:
        - Tour Name: {tour_name}
        - Tour Date: {tour_date}
        - Travelers: {traveler_count}
        - Total Price: {total_price}
        
        We hope you have an amazing trip!

        Regards,
        Travel Team
        """
        message.attach(MIMEText(body, 'plain'))

        # Send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, lead_email, message.as_string())
        server.quit()

        return redirect(url_for('get_all_posts'))  
        # return jsonify({"message": "Traveler details saved and email sent successfully."}), 200

    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify({"error": str(e)}), 500
    

# To get the email

@app.route('/enquiry', methods=['GET', 'POST'])
def enquiry():
    msg_sent = False
    if request.method == 'POST':
        print("POST request received")  # Debugging line
        # Get form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        user_message = request.form['message']
        
        try:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = ""  # Replace with your email
            sender_password = ""   # Replace with your password
            receiver = "travel.team131@gmail.com"
            # Create the email
            subject = "Contact Form Submission"
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver  # You can change the recipient if needed
            msg['Subject'] = subject

            # Email body content
            body = f"""
            Hello,

            You have received a new message from {name}:

            Name: {name}
            Email: {email}
            Phone: {phone}

            Message:
            {user_message}

            Regards,
            {name}
            """
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver, msg.as_string())  # Send to sender's email
            msg_sent = True
          
        except Exception as e:
            return f"An error occurred while sending the email: {e}"  # Return error message if exception occurs
    return render_template('contact.html', msg_sent=msg_sent)
    

if __name__ == "__main__":
    app.run(debug=True, port=5001)


