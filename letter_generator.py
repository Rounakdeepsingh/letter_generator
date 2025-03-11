from flask import Flask, render_template, request, send_file, session, flash, redirect, url_for
import google.generativeai as genai
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from datetime import datetime

# Load API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API key not found.  Please set GEMINI_API_KEY in your environment variables.")

genai.configure(api_key=API_KEY)

app = Flask(__name__)  # Corrected:  Double underscores for __name__
app.secret_key = "your_secret_key"  # Replace with a strong, randomly generated secret key!

# Model selection
MODEL_NAME = "gemini-1.5-pro"  # Or any other valid model name

def generate_letter(letter_type, **kwargs):
    date_today = datetime.today().strftime("%d %B %Y")
    prompt = ""

    if letter_type == "bonafide":
        prompt = f"""
        Generate a professional formal Bonafide Certificate request letter, strictly adhering to the following format and details:

        - Date: {date_today}
        - Place: Chennai
        - From:
            - Name (IN CAPITAL, AS PER 10TH MARKSHEET): {kwargs.get('name')}
            - Vh No: {kwargs.get('vh_no')}
        - To: The Principal, Vel Tech High Tech Dr.Rangarajan Dr.Sakunthala Engineering College.
        - Subject: Requisition for Bonafide Certificate for {kwargs.get('bonafide_for')} Reg.

        - Body:
            - I/We are in need of bonafide certificate for {kwargs.get('bonafide_reason')}.
            - Purpose: Kindly issue me/us the same with/without tuition/hostel/transport fee structure.
            - Kindly do the needful at the earliest.

        - Closing:
            - Thanking You,
            - Your Obediently,
        """

    elif letter_type == "fee_receipt":
        prompt = f"""
        Generate a professional formal Fee Receipt request letter, strictly adhering to the following format and details:

        - Date: {date_today}
        - Place: Chennai
        - From:
            - Name (IN CAPITAL, AS PER 10TH MARKSHEET): {kwargs.get('name')}
            - Vh No: {kwargs.get('vh_no')}
        - To: The Principal, Vel Tech High Tech Dr.Rangarajan Dr.Sakunthala Engineering College.
        - Subject: Requisition for Fee Receipt(s) Reg.
        
        - Body:
            - As I am in need of the Fee Receipt(s) for {kwargs.get('fee_receipt_reason')}.
            - Kindly issue me the same at the earliest.
        
        - Purpose: {kwargs.get('purpose')}

        - Closing:
            - Thanking You,
            - Your Obediently,
        """

    elif letter_type == "on_duty":
        prompt = f"""
        Generate a professional formal On Duty request letter, strictly adhering to the following format and details:

        - Date: {date_today}
        - Place: Chennai
        - From:
            - Name (IN CAPITAL, AS PER 10TH MARKSHEET): {kwargs.get('name')}
            - Vh No: {kwargs.get('vh_no')}
        - To: The Principal, Vel Tech High Tech Dr.Rangarajan Dr.Sakunthala Engineering College.
        - Subject: Requisition for On Duty Reg.
        
        - Body:
            - As Iam/We are interested/Registered for the program on {kwargs.get('program_name')} at {kwargs.get('program_location')}.
            - From {kwargs.get('from_date')} to {kwargs.get('to_date')}.
            - In this regard I/we request you to Kindly issue me/us the On Duty. Kindly do the needful at the earliest.
        
        - Closing:
            - Thanking You,
            - Your Obediently,
        """

    elif letter_type == "leave":
        prompt = f"""
        Generate a professional formal Leave application letter, strictly adhering to the following format and details:

        - Date: {date_today}
        - Place: Chennai
        - From:
            - Name (IN CAPITAL, as per the 10TH MARK SHEET): {kwargs.get('name')}
            - Vh.No./Reg. No.: {kwargs.get('vh_no')}
            - Year/ Sem/ Batch/ Class: {kwargs.get('year_sem_batch_class')}
        - To: The Principal, Vel Tech High Tech Dr.Rangarajan Dr.Sakunthala Engineering College.
        - Subject: Requisition for Leave Reg.

        - Body:
            - As I am going to {kwargs.get('leave_going_to')} from {kwargs.get('leave_from')} to {kwargs.get('leave_to')} for {kwargs.get('leave_reason')}.
            - I request you to Kindly issue me the leave. Kindly do the needful.

        - Additional Details:
            - % ATTENDANCE: {kwargs.get('attendance')} (PERIOD: {kwargs.get('period')})

        - Closing:
            - Thanking You,
            - Your Obediently,

        - Parent Details:
            - Parent Name: {kwargs.get('parent_name')}
            - Relation: Father/Mother
            - Parent Mobile No.: {kwargs.get('parent_mobile')}
        """

    elif letter_type == "apology":
        prompt = f"""
        Generate a professional formal Apology letter application, strictly adhering to the following format and details:

        - Date: {date_today}
        - Place: Chennai
        - From:
            - Name (IN CAPITAL, AS PER THE 10TH MARK SHEET): {kwargs.get('name')}
            - Vh.No./Reg. No.: {kwargs.get('vh_no')}
            - Year/ Sem/ Batch/ Class: {kwargs.get('year_sem_batch_class')}
        - To: The Principal, Vel Tech High Tech Dr.Rangarajan Dr.Sakunthala Engineering College.
        - Subject: Apology letter Reg.

        - Body:
            - As I have done {kwargs.get('apology_done')}, I sincerely apologize for the mistake happened and I abide to the action taken against me for the same.
            - and I assure you that I will not repeat my mistake again. Please accept my request and excuse me one last time.

        - Additional Details:
            - % ATTENDANCE: {kwargs.get('attendance')} (PERIOD: {kwargs.get('period')})

        - Closing:
            - Thanking You,
            - Your Obediently,

        - Parent Details:
            - Parent Name: {kwargs.get('parent_name')}
            - Relation: Father/Mother
            - Parent Mobile No.: {kwargs.get('parent_mobile')}
        """

    elif letter_type == "hostel_out_in":
        prompt = f"""
        Generate a professional formal Hostel Out/In Pass application, strictly adhering to the following format and details:

        - Date: {date_today}
        - Place: Chennai
        - From:
            - Name (in CAPITAL, as per the 10TH MARK SHEET): {kwargs.get('name')}
            - Vh.No./Reg. No.: {kwargs.get('vh_no')}
            - Year/ Sem/Batch/ Class: {kwargs.get('year_sem_batch_class')}
        - To: The Principal, Vel Tech High Tech Dr.Rangarajan Dr.Sakunthala Engineering College.
        - Subject: Requisition for Hostel Out Pass Reg.

        - Body:
            - I would like to go home / relatives house / outing due to {kwargs.get('reason')}.
            - In this regard, I request you to give permission for the same. Kindly do the needful at the earliest.

        - Additional Details:
            - Parent's Name: {kwargs.get('parent_name')}
            - Contact No: {kwargs.get('parent_contact')}
            - Place of Visit: {kwargs.get('place_of_visit')}
            - Out Time: Date: {kwargs.get('out_date')} Time: {kwargs.get('out_time')}
            - In Time: Date: {kwargs.get('in_date')} Time: {kwargs.get('in_time')}
            - Confirmed with Parent: Yes

        - Closing:
            - Thanking You,
            - Your Obediently,

        """

    elif letter_type == "id_card":
        prompt = f"""
        Generate a professional formal ID Card application, strictly adhering to the following format and details:

        - Date: {date_today}
        - Place: Chennai
        - From:
            - Name (in CAPITAL, as per the 10TH MARK SHEET): {kwargs.get('name')}
            - Vh.No./Reg. No.: {kwargs.get('vh_no')}
            - Year/ Sem/Batch/ Class: {kwargs.get('year_sem_batch_class')}
        - To: The Principal, Vel Tech High Tech Dr.Rangarajan Dr.Sakunthala Engineering College.
        - Subject: Requisition for New Id card Reg.

        - Body:
            - As I have lost my id card in {kwargs.get('id_card_lost_place')}, I would like to apply for a new id card.
            - In this regard, I request you to give approval for the same. I assure you that I will safeguard the id card hereafter. Kindly do the needful at the earliest.

        - Closing:
            - Thanking You,
            - Your Obediently,

        """

    elif letter_type == "attendance_shortage":
        prompt = f"""
        Generate a professional formal Attendance Shortage Undertaking application, strictly adhering to the following format and details:

        - Date: {date_today}
        - Place: Chennai
        - From:
            - Name (in CAPITAL, as per the 10TH MARK SHEET): {kwargs.get('name')}
            - Vh.No./Reg. No.: {kwargs.get('vh_no')}
            - Year/ Sem/ Batch/ Class: {kwargs.get('year_sem_batch_class')}
        - To: The Principal, Vel Tech High Tech Dr.Rangarajan Dr.Sakunthala Engineering College.
        - Subject: Undertaking for having less than 75% attendance Reg.

        - Body:
            - I am aware that a minimum of 75% attendance is required to write end sem examinations.
            - My cumulative attendance for the Period from {kwargs.get('period_start')} to {kwargs.get('period_end')} is {kwargs.get('attendance')}%.
            - In this regard, I assure you that, hereafter I would come to college regularly and I also undertake that, in case of failing which and, get Sem drop as a consequence of shortage of attendance, I will take the whole responsibility. Hence I request you to accept my request and allow me to attend the classes. Kindly do the needful at the earliest.

        - Closing:
            - Thanking You,
            - Your Obediently,

        - Parent Details:
            - Parent Name: {kwargs.get('parent_name')}
            - Relation: Father/Mother
            - Parent Mobile No.: {kwargs.get('parent_mobile')}
        """

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        error_message = f"Error generating letter: {e}"
        print(error_message)  # Log the error for debugging
        return error_message

@app.route("/", methods=["GET", "POST"])
def index():
    letter = None
    current_year = datetime.now().year
    letter_type = session.get("letter_type", None)

    if request.method == "POST":
        # Get letter_type, either from form (initial selection) or session (subsequent requests)
        if 'letter_type' in request.form:
            letter_type = request.form.get("letter_type")
            session["letter_type"] = letter_type  # Store in session
        else:
            letter_type = session.get("letter_type")  # Retrieve from session

        if letter_type:  # Check if a letter type is selected
            if 'generate' in request.form:
                # Collect form data (using .get() to handle missing fields)
                #  Crucially, *all* fields are collected here, even if they are
                #  only used by some letter types.  This avoids KeyErrors.
                form_data = {
                    "name": request.form.get("name"),
                    "vh_no": request.form.get("vh_no"),
                    "year_sem_batch_class": request.form.get("year_sem_batch_class"),
                    "bonafide_for": request.form.get("bonafide_for"),
                    "bonafide_reason": request.form.get("bonafide_reason"),
                    "fee_receipt_reason": request.form.get("fee_receipt_reason"),
                    "purpose": request.form.get("purpose"),
                    "program_name": request.form.get("program_name"),
                    "program_location": request.form.get("program_location"),
                    "from_date": request.form.get("from_date"),
                    "to_date": request.form.get("to_date"),
                    "leave_going_to": request.form.get("leave_going_to"),
                    "leave_from": request.form.get("leave_from"),
                    "leave_to": request.form.get("leave_to"),
                    "leave_reason": request.form.get("leave_reason"),  # Corrected: Added leave_reason
                    "attendance": request.form.get("attendance"),
                    "period": request.form.get("period"),
                    "parent_name": request.form.get("parent_name"),
                    "parent_mobile": request.form.get("parent_mobile"),
                    "apology_done": request.form.get("apology_done"),
                    "reason": request.form.get("reason"),
                    "parent_contact": request.form.get("parent_contact"),
                    "place_of_visit": request.form.get("place_of_visit"),
                    "out_date": request.form.get("out_date"),
                    "out_time": request.form.get("out_time"),
                    "in_date": request.form.get("in_date"),
                    "in_time": request.form.get("in_time"),
                    "id_card_lost_place": request.form.get("id_card_lost_place"),
                    "period_start": request.form.get("period_start"),
                    "period_end": request.form.get("period_end")
                }
                letter = generate_letter(letter_type, **form_data)
                if "Error" in letter:
                   flash(f"Error generating the letter: {letter}", "error")
                session["letter"] = letter  # Store the generated letter

            else:  # The "Proceed" button was pressed, but no 'generate'
                flash("Please select a letter type.", "error") # Added

        # No else needed:  If letter_type is None, we just fall through
        # and re-render the template, showing the initial form.

    return render_template("index.html", letter=session.get("letter", None), current_year=current_year, letter_type=letter_type)



@app.route("/form_fields")
def form_fields():
    letter_type = request.args.get("letter_type")
    if not letter_type:
        return "Please select a letter type.", 400
    form_html = render_template("form_fields.html", letter_type=letter_type) #form_fields.html
    return form_html

@app.route("/download", methods=["POST"])
def download_pdf():
    letter_text = request.form.get("edited_letter", "No letter generated.")
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)  # Corrected: Use imported 'letter'
    styles = getSampleStyleSheet()
    style = ParagraphStyle(name='LetterStyle', fontName='Helvetica', fontSize=12, leading=14, spaceAfter=12)

    letter_paragraphs = letter_text.strip().split("\n\n")  # Split by double newlines
    flowables = []
    for para in letter_paragraphs:
        # Replace single newlines with <br /> for HTML-style line breaks within paragraphs
        paragraph = Paragraph(para.replace("\n", "<br />"), style)
        flowables.append(paragraph)

    doc.build(flowables)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="generated_letter.pdf")#Corrected:download_name


@app.route("/home")
def home():
    session.pop("letter_type", None)  # Clear letter_type from session
    session.pop("letter", None)
    return redirect(url_for("index"))

if __name__ == "__main__":  # Corrected: Double underscores for __main__
    app.run(debug=True)