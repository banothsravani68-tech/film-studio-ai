
import gradio as gr

studio_tasks = []
studio_bookings = []
approval_requests = []

studio_services = [
    "Wedding Photography",
    "Wedding Videography",
    "Pre-Wedding Photography",
    "Pre-Wedding Videography",
    "Birthday Photography",
    "Birthday Videography",
    "Album Design",
    "Video Editing",
    "Photo Editing",
    "Reel Editing"
]

task_statuses = [
    "Pending",
    "In Progress",
    "Revision",
    "Completed",
    "Delivered"
]


def understand_studio_request(message):
    text = message.lower()

    if any(x in text for x in ["song change", "change song", "song"]):
        return "Video Editing Request", "Video Editor"

    elif any(x in text for x in ["add clip", "add clips", "remove clip", "remove clips"]):
        return "Video Editing Request", "Video Editor"

    elif any(x in text for x in ["album photo", "album photos", "change album", "add album"]):
        return "Album Request", "Album Designer"

    elif any(x in text for x in ["retouch", "photo edit", "photo editing"]):
        return "Photo Editing Request", "Photo Editor"

    elif any(x in text for x in ["reel", "instagram reel"]):
        return "Reel Request", "Reel Editor"

    elif any(x in text for x in [
        "not received", "not come", "delivery",
        "photos not", "video not", "missing"
    ]):
        return "Delivery Complaint", "Support/Admin"

    elif any(x in text for x in [
        "complaint", "complain", "problem", "issue"
    ]):
        return "Complaint", "Support/Admin"

    elif any(x in text for x in ["booking", "book", "reserve"]):
        return "Booking Request", "Studio Manager"

    else:
        return "General Request", "Studio Manager"


def create_customer_task(
    customer_name,
    phone,
    event_type,
    event_date,
    request_details,
    priority="Normal"
):
    request_type, assigned_staff = understand_studio_request(request_details)

    task = {
        "task_id": len(studio_tasks) + 1,
        "customer_name": customer_name,
        "phone": phone,
        "event_type": event_type,
        "event_date": event_date,
        "request": request_details,
        "request_type": request_type,
        "assigned_to": assigned_staff,
        "priority": priority,
        "status": "Pending"
    }

    studio_tasks.append(task)
    return task


def create_booking(
    customer_name,
    phone,
    event_type,
    event_date,
    service
):
    if not customer_name or not phone or not event_date:
        return {
            "status": "Error",
            "message": "Customer name, phone number and event date are required."
        }

    booking = {
        "booking_id": len(studio_bookings) + 1,
        "customer_name": customer_name,
        "phone": phone,
        "event_type": event_type,
        "event_date": event_date,
        "service": service,
        "status": "Waiting for Studio Manager Approval"
    }

    studio_bookings.append(booking)
    return booking


def approve_or_reject_booking(booking_id, decision):
    for booking in studio_bookings:
        if booking["booking_id"] == int(booking_id):

            if decision == "Approve":
                booking["status"] = "Booking Confirmed"

            elif decision == "Reject":
                booking["status"] = "Booking Rejected"

            else:
                return {
                    "status": "Error",
                    "message": "Please choose Approve or Reject."
                }

            return booking

    return {
        "status": "Error",
        "message": "Booking not found."
    }


def update_studio_task(task_id, new_status):

    if new_status not in task_statuses:
        return {
            "status": "Error",
            "message": "Invalid task status."
        }

    for task in studio_tasks:

        if task["task_id"] == int(task_id):

            task["status"] = new_status

            return {
                "status": "Updated",
                "task_id": task_id,
                "customer": task["customer_name"],
                "assigned_to": task["assigned_to"],
                "new_status": new_status
            }

    return {
        "status": "Error",
        "message": "Task not found."
    }


def get_customer_task_status(phone):

    if not phone:
        return "Please enter your phone number."

    customer_tasks = [
        task for task in studio_tasks
        if task.get("phone") == phone
    ]

    if not customer_tasks:
        return "No task found for this phone number."

    output = "### Your Studio Requests\n\n"

    for task in customer_tasks:

        output += (
            f"**Task ID:** {task.get('task_id', 'N/A')}\n\n"
            f"**Request:** {task.get('request', 'N/A')}\n\n"
            f"**Assigned To:** {task.get('assigned_to', 'N/A')}\n\n"
            f"**Status:** {task.get('status', 'Pending')}\n\n"
            "---\n\n"
        )

    return output


def request_human_approval(action, customer_name, details):

    approval = {
        "approval_id": len(approval_requests) + 1,
        "action": action,
        "customer_name": customer_name,
        "details": details,
        "status": "Waiting for Human Approval"
    }

    approval_requests.append(approval)

    return approval


def process_human_approval(approval_id, decision):

    for approval in approval_requests:

        if approval["approval_id"] == int(approval_id):

            if decision == "Approve":
                approval["status"] = "Approved"

            elif decision == "Reject":
                approval["status"] = "Rejected"

            else:
                return {
                    "status": "Error",
                    "message": "Please choose Approve or Reject."
                }

            return approval

    return {
        "status": "Error",
        "message": "Approval request not found."
    }


def agent_decide_action(message):

    request_type, assigned_staff = understand_studio_request(message)

    if request_type == "Booking Request":
        action = "Start Booking Workflow"

    elif request_type == "Complaint":
        action = "Create Complaint Task"

    elif request_type == "Delivery Complaint":
        action = "Check Delivery / Create Support Task"

    elif request_type == "Video Editing Request":
        action = "Create Video Editing Task"

    elif request_type == "Album Request":
        action = "Create Album Task"

    elif request_type == "Photo Editing Request":
        action = "Create Photo Editing Task"

    elif request_type == "Reel Request":
        action = "Create Reel Editing Task"

    else:
        action = "Send to Studio Manager"

    return {
        "request": message,
        "request_type": request_type,
        "assigned_to": assigned_staff,
        "action": action
    }


def process_agent_request(customer_name, phone, message):

    decision = agent_decide_action(message)

    action = decision["action"]
    assigned_staff = decision["assigned_to"]

    if action in [
        "Start Booking Workflow",
        "Create Complaint Task",
        "Check Delivery / Create Support Task"
    ]:

        approval = request_human_approval(
            action,
            customer_name,
            message
        )

        return {
            "approval_required": True,
            "approval_id": approval["approval_id"],
            "action": action,
            "assigned_to": assigned_staff,
            "status": "Waiting for Human Approval"
        }

    task = create_customer_task(
        customer_name,
        phone,
        "Customer Request",
        "",
        message,
        "Normal"
    )

    return {
        "approval_required": False,
        "task_created": True,
        "task_id": task["task_id"],
        "action": action,
        "assigned_to": assigned_staff,
        "status": task["status"]
    }


def improved_customer_chat(customer_name, phone, message):

    if not customer_name or not phone:
        return "Please enter your name and phone number first."

    if not message or not message.strip():
        return "Please enter your request."

    result = process_agent_request(
        customer_name,
        phone,
        message
    )

    action = result.get("action")
    assigned = result.get("assigned_to")

    if result.get("approval_required"):

        return f"""
### 📸 Film Studio AI Assistant

Hi **{customer_name}**! 👋

I understood your request:

**{message}**

**AI Action:** {action}

**Handled By:** {assigned}

**Approval:** Studio team approval is required.

**Reference ID:** {result.get('approval_id')}

Your request has been forwarded to the studio team.
"""

    return f"""
### 📸 Film Studio AI Assistant

Hi **{customer_name}**! 👋

I understood your request:

**{message}**

**AI Action:** {action}

**Handled By:** {assigned}

**Task ID:** {result.get('task_id')}

**Status:** {result.get('status')}

Your request has been sent to the studio team.
"""


def final_booking_request(
    customer_name,
    phone,
    event_type,
    event_date,
    service
):

    result = create_booking(
        customer_name,
        phone,
        event_type,
        event_date,
        service
    )

    return str(result)


def final_manager_decision(
    booking_id,
    decision
):

    return str(
        approve_or_reject_booking(
            booking_id,
            decision
        )
    )


def final_customer_status(phone):

    return get_customer_task_status(phone)


def final_staff_dashboard():

    if not studio_tasks:
        return "No customer tasks available."

    output = "========== FILM STUDIO STAFF DASHBOARD ==========\n\n"

    for task in studio_tasks:

        output += (
            f"Task ID: {task.get('task_id', 'N/A')}\n"
            f"Customer: {task.get('customer_name', 'N/A')}\n"
            f"Phone: {task.get('phone', 'N/A')}\n"
            f"Request: {task.get('request', 'N/A')}\n"
            f"Assigned To: {task.get('assigned_to', 'N/A')}\n"
            f"Priority: {task.get('priority', 'Normal')}\n"
            f"Status: {task.get('status', 'Pending')}\n"
            "----------------------------------------\n"
        )

    return output


def final_update_task(task_id, new_status):

    if not task_id or not new_status:
        return "Please enter Task ID and select a status."

    return str(
        update_studio_task(
            task_id,
            new_status
        )
    )


with gr.Blocks(
    title="Film Studio AI Assistant"
) as app:

    gr.Markdown(
        """
# 📸 Film Studio AI Assistant

### AI-powered customer support and studio workflow automation

Customer requests → AI understanding → Agent decision → Staff assignment → Human approval → Task tracking
"""
    )

    with gr.Tab("🤖 AI Assistant"):

        customer_name = gr.Textbox(
            label="Customer Name"
        )

        customer_phone = gr.Textbox(
            label="Phone Number"
        )

        customer_message = gr.Textbox(
            label="Customer Request",
            placeholder="Example: Naa wedding video lo song change cheyyali"
        )

        send_request = gr.Button(
            "Send Request"
        )

        ai_response = gr.Markdown()

        send_request.click(
            improved_customer_chat,
            inputs=[
                customer_name,
                customer_phone,
                customer_message
            ],
            outputs=ai_response
        )

    with gr.Tab("📅 Booking"):

        booking_name = gr.Textbox(
            label="Customer Name"
        )

        booking_phone = gr.Textbox(
            label="Phone Number"
        )

        booking_event = gr.Textbox(
            label="Event Type"
        )

        booking_date = gr.Textbox(
            label="Event Date"
        )

        booking_service = gr.Dropdown(
            studio_services,
            label="Service"
        )

        booking_button = gr.Button(
            "Request Booking"
        )

        booking_result = gr.Textbox(
            label="Booking Result"
        )

        booking_button.click(
            final_booking_request,
            inputs=[
                booking_name,
                booking_phone,
                booking_event,
                booking_date,
                booking_service
            ],
            outputs=booking_result
        )

        gr.Markdown("### Studio Manager Approval")

        approval_booking_id = gr.Textbox(
            label="Booking ID"
        )

        approval_decision = gr.Dropdown(
            ["Approve", "Reject"],
            label="Decision"
        )

        approval_button = gr.Button(
            "Update Booking"
        )

        approval_result = gr.Textbox(
            label="Approval Result"
        )

        approval_button.click(
            final_manager_decision,
            inputs=[
                approval_booking_id,
                approval_decision
            ],
            outputs=approval_result
        )

    with gr.Tab("📦 Track Request"):

        tracking_phone = gr.Textbox(
            label="Customer Phone Number"
        )

        tracking_button = gr.Button(
            "Track My Request"
        )

        tracking_result = gr.Markdown()

        tracking_button.click(
            final_customer_status,
            inputs=tracking_phone,
            outputs=tracking_result
        )

    with gr.Tab("📋 Staff Dashboard"):

        refresh_button = gr.Button(
            "Refresh Dashboard"
        )

        dashboard_output = gr.Textbox(
            label="Customer Tasks",
            lines=15
        )

        refresh_button.click(
            final_staff_dashboard,
            outputs=dashboard_output
        )

        gr.Markdown("### Update Task Status")

        task_id_input = gr.Textbox(
            label="Task ID"
        )

        task_status_input = gr.Dropdown(
            task_statuses,
            label="New Status"
        )

        update_button = gr.Button(
            "Update Task"
        )

        update_result = gr.Textbox(
            label="Update Result"
        )

        update_button.click(
            final_update_task,
            inputs=[
                task_id_input,
                task_status_input
            ],
            outputs=update_result
        )


if __name__ == "__main__":
    app.launch()
