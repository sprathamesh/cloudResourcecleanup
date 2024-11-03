import subprocess
from tkinter import *

root = Tk()

def submit_form():
    cloud = cloud_var.get()
    resource = resource_var.get()
    #filter_tags = "{'tag': ['development']}"   # Default value for filter_tags  # Get and remove leading/trailing whitespace
    age = text_area2.get(1.0, END).strip()  # Get and remove leading/trailing whitespace
    operation_type = operation_type_var.get()
    dry_run = dry_run_var.get()

    command = ['python', 'C:\cloudResourcecleanup\cloud-resource-cleanup-main\crc.py']

    # Add arguments to the command list based on conditions
    if cloud:
        command.extend(['--cloud', cloud])
    if resource:
        command.extend(['--resource', resource])
    if filter_tags:
        command.extend(['--filter_tags', filter_tags])
    if age:
        command.extend(['--age', age])
    if operation_type:
        command.extend(['--operation_type', operation_type])
    if dry_run:
        command.append('--dry_run')

    # Execute the command
    if len(command) > 2:  # Assuming 'python' and the script path are always present
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output , error = process.communicate()

        # check for error
        if error:
            update_output_ui(f"Error: {error}")
        else:
            #update the UI with the output
            update_output_ui(output)

    else:
        # Display a message in the text box if no arguments were selected
        update_output_ui("No araaguments selected for the command.")

def reset_form():
    # Clear the text in the Text widgets
    # text_area1.delete(1.0, END)
    text_area2.delete(1.0, END)
    output_text.delete(1.0, END)

    # Reset the OptionMenu values
    cloud_var.set(options1[0])
    resource_var.set(options2[0])
    operation_type_var.set(options3[0])
    dry_run_var.set(options4[0])

def update_output_ui(output):
    # Clear the existing text in the Text widget
    output_text.delete(1.0, END)

    # Insert the captured output into the Text widget
    output_text.insert(END, output)

root.configure(bg="light blue")

root.title("CLOUD RESOURCE CLEANUP")

# Left side
left_frame = Frame(root)
left_frame.pack(side=LEFT, padx=50, pady=50)

heading = Label(left_frame, text="Cloud Resource Cleanup:\nEfficient Management and Optimization of Cloud Resources",
                bg="light blue", fg="black", font=("Consolas", 12))
heading.pack(pady=10)

l1 = Label(left_frame, text="CLOUD NAME")
l1.pack(anchor="w", pady=10)
options1 = ["azure", "aws"]
cloud_var = StringVar()
dropdown1 = OptionMenu(left_frame, cloud_var, *options1)
dropdown1.pack()

l2 = Label(left_frame, text="RESOURCE")
l2.pack(anchor="w", pady=10)
options2 = ["vm", "ip", "disk","keypair"]
resource_var = StringVar()
dropdown2 = OptionMenu(left_frame, resource_var, *options2)
dropdown2.pack()

# l3 = Label(left_frame, text="FILTER TAGS")
# l3.pack(anchor="w", pady=10)
# text_area1 = Text(left_frame, height=3, width=40)
# text_area1.pack()

l4 = Label(left_frame, text="AGE")
l4.pack(anchor="w", pady=10)
text_area2 = Text(left_frame, height=3, width=40)
text_area2.pack()

# Default message for text_area2
default_message_2 = "{ 'days': 2, 'hours': 12 }"
text_area2.insert("1.0", default_message_2)

l5 = Label(left_frame, text="OPERATION TYPE")
l5.pack(anchor="w", pady=10)
options3 = ["stop", "delete"]
operation_type_var = StringVar()
dropdown3 = OptionMenu(left_frame, operation_type_var, *options3)
dropdown3.pack()

l6 = Label(left_frame, text="DRY RUN")
l6.pack(anchor="w", pady=10)
options4 = ["--dry_run"]
dry_run_var = StringVar()
dropdown4 = OptionMenu(left_frame, dry_run_var, *options4)
dropdown4.pack()

# Submit button
submit_button = Button(left_frame, text="SEARCH", width=15, height=2, command=submit_form)
submit_button.pack(side=LEFT, pady=10, padx=80)

#reset button
reset_button = Button(left_frame, text="Reset", width=15, height=2, command=reset_form)
reset_button.pack(side=RIGHT, pady=10, padx=80)

# Right side
right_frame = Frame(root)
right_frame.pack(side=RIGHT, padx=50, pady=50)

# Create a Label for the heading
heading_label = Label(right_frame, text="RESULTS", font=("Helvetica", 16))
heading_label.pack(pady=10) 

# Create a Text widget to display the output
output_text = Text(right_frame, height=40, width=100)
output_text.pack()

root.mainloop()
