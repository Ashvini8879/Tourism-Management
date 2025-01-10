from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,IntegerField, TextAreaField, FieldList, FormField
from wtforms.validators import DataRequired, URL, NumberRange, Length, EqualTo, Email,  Regexp
from flask_ckeditor import CKEditorField



# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
   
    title = StringField("Tour Name", validators=[DataRequired()])
    destination = StringField("Tour Destination", validators=[DataRequired()])
    
    img_url = StringField("Tour Background Image URL", validators=[DataRequired(), URL()])
    days = IntegerField("Days", validators=[DataRequired(), NumberRange(min=1)])

    tour_operator = StringField("Tour Operator", validators=[DataRequired()])
    max_group_size = IntegerField("Max Group Size", validators=[DataRequired(), NumberRange(min=1)])
    age_range = StringField("Age Range", validators=[DataRequired()])
    operated_in = StringField("Operated In", validators=[DataRequired()])
    tour_id = StringField("Tour ID", validators=[DataRequired()])
    
    places_youll_see = CKEditorField("Places You’ll See (with images)", validators=[DataRequired()])
    highlights = TextAreaField("Highlights", validators=[DataRequired()])

    
    submit = SubmitField("Create Tour")


# Create a form to register new users
class RegisterForm(FlaskForm):
    email = StringField(
        "Email", 
        validators=[
            DataRequired(), 
            Email(message="Please enter a valid email address.")
        ]
    )
    password = PasswordField(
        "Password", 
        validators=[
            DataRequired(), 
            Length(min=8, message="Password must be at least 8 characters long.")
        ]
    )
    confirm_password = PasswordField(
        "Confirm Password", 
        validators=[
            DataRequired(), 
            EqualTo("password", message="Passwords must match.")
        ]
    )
    name = StringField(
        "Name", 
        validators=[
            DataRequired(), 
            Length(min=2, max=50, message="Name must be between 2 and 50 characters."),
            Regexp(
                "^[A-Za-z ]+$", 
                message="Name must contain only letters and spaces."
            )
        ]
    )
    submit = SubmitField("Sign Me Up!")


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


# Create a form to add comments
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")
