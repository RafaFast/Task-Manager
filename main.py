from tkinter import messagebox, simpledialog
import tkinter as tk
import json
import os
from datetime import datetime
from ttkbootstrap import Style

DATE_FORMAT = '%d/%m/%Y'
TASK_FILE = 'tasks.json'

# Function to save tasks in a JSON file
def save_tasks():
    with open(TASK_FILE, 'w') as file:
        json.dump(tasks, file)

def list_sort_priority(task):
    # Organizes the task file based on its priority and remaining days
    def priority(task):
        deadline_timestamp = datetime.strptime(task['Deadline Date'], DATE_FORMAT)
        if task['Priority'] == '(Priority)' and task['Conclused'] == '':
            return 0, deadline_timestamp
        else:
            return 1, deadline_timestamp
    # Organize 'tasks'
    tasks.sort(key=priority)

def days_to_deadline(task):
    deadline_date = datetime.strptime(task['Deadline Date'], DATE_FORMAT)
    return deadline_date, deadline_date - datetime.now()

def task_str_color(task):
    deadline = days_to_deadline(task)
    if deadline[1].days <= 0 and task['Conclused'] == "" and task['Priority'] == "":
        color = 'red'
    elif deadline[1].days <= 0 and task['Conclused'] == "" and task['Priority'] == "(Priority)":
        color = 'red'   
    elif deadline[1].days <= 0 and task['Conclused'] == "(Conclused)" and task['Priority'] == "":
        color = 'green'
    elif deadline[1].days <= 0 and task['Conclused'] == "(Conclused)" and task['Priority'] == "(Priority)":
        color = 'green'
    elif deadline[1].days > 0 and task['Conclused'] == "" and task['Priority'] == "(Priority)":
        color = 'purple'
    elif deadline[1].days > 0 and task['Conclused'] == "(Conclused)" and task['Priority'] == "":
        color = 'green'
    elif deadline[1].days > 0 and task['Conclused'] == "(Conclused)" and task['Priority'] == "(Priority)":
        color = 'green'
    else:
        color = 'white'
    task_list.itemconfig(tk.END, {'fg': color})

# Function to update the task list
def update_list():
    # Clears the tkinter ListBox
    task_list.delete(0, tk.END)
    
    for task in tasks:
        deadline = days_to_deadline(task)
        text = f"{task['Name']} {task['Conclused']} {task['Priority']} Deadline: {deadline[0].strftime(DATE_FORMAT)}"
        task_list.insert(tk.END, text)
        task_str_color(task)
        list_sort_priority(task)

def validate_date_format(date):
    try:
        datetime.strptime(date, DATE_FORMAT)
        return True
    except ValueError:
        return False
    
def validate_dates_consistency(start_date, deadline_date):
    start_date = datetime.strptime(start_date, DATE_FORMAT)
    deadline_date = datetime.strptime(deadline_date, DATE_FORMAT)
    if start_date <= deadline_date:
        return True
    else:
        return False

# Function to delete task
def delete_task():
    response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this task?")
    if response:
        selected = task_list.curselection()
        if selected:
            index = selected[0]
            del tasks[index]
            save_tasks()
            update_list()

# Function to edit a task
def edit_task_description():
    selected = task_list.curselection()
    if selected:
        index = selected[0]
        task = tasks[index]
        new_content = simpledialog.askstring(
            "Edit Task", f"Edit description of the task '{task['Name']}'", initialvalue=task['Description']
            )
        if new_content:
            task['Description'] = new_content
            save_tasks()
            update_list()

# Function to add task
def add_task():

    name = name_entry.get()
    description = description_entry.get()
    responsible = responsible_entry.get()
    start_date = start_date_entry.get()
    deadline = deadline_entry.get()

    if validate_date_format(start_date) == True and validate_date_format(deadline) == True:
        if validate_dates_consistency(start_date, deadline) == True:
            if name and description and responsible and start_date and deadline:
                
                task = {
                    'Name': name,
                    'Description': description,
                    'Responsible': responsible,
                    'Start Date': start_date,
                    'Deadline Date': deadline,
                    'Priority': "",
                    'Conclused': ""
                    }

                tasks.append(task)
                save_tasks()
                update_list()

                name_entry.delete(0, tk.END)
                description_entry.delete(0, tk.END)
                responsible_entry.delete(0, tk.END)
                start_date_entry.delete(0, tk.END)
                deadline_entry.delete(0, tk.END)
                
            else:                
                messagebox.showerror("Data Insufficiency Error", "Fill in all fields!!!")
        else:
            messagebox.showerror("Data Consistency Error", "The start date needs to be earlier than the deadline date")
    else:
        messagebox.showerror("Date Formatting Error", "Enter a valid date!!!")

# Function to mark task as conclused
def mark_conclused():
    selected = task_list.curselection()
    if selected:
        index = selected[0]
        task = tasks[index]
        task['Conclused'] = "(Conclused)"

        save_tasks()
        update_list()

# Function to set task priority
def set_priority():
    selected = task_list.curselection()
    if selected:
        index = selected[0]
        task = tasks[index]
        task['Priority'] = "(Priority)"

        save_tasks()
        update_list()

# Function to search tasks by name or responsible
def search_tasks():
    term = search_entry.get()
    if term:
        term = term.lower()

        found_tasks = [
            task for task in tasks if term in task['Name'].lower() or term in task['Responsible'].lower()
            ]
        
        task_list.delete(0, tk.END)
        for task in found_tasks:
            deadline = days_to_deadline(task)
            text = f"{task['Name']} {task['Conclused']} {task['Priority']} Deadline: {deadline[0].strftime(DATE_FORMAT)}"
            task_list.insert(tk.END, text)
            task_str_color(task)

# Function to open a new window for detailed task view
def open_details():
    selected = task_list.curselection()
    if selected:
        index = selected[0]
        task = tasks[index]

        details_window = tk.Toplevel(window)
        details_window.title(f"Task Details: {task['Name']}")

        frame = tk.Frame(details_window)
        frame.pack(padx=20, pady=10)
        
        name_label = tk.Label(frame, text=f"Task Name: {task['Name']}", font=("Arial", 12))
        name_label.pack(pady=5)

        description_label = tk.Label(frame, text=f"Description: {task['Description']}", font=("Arial", 12))
        description_label.pack(pady=5)

        responsible_label = tk.Label(frame, text=f"Responsible: {task['Responsible']}", font=("Arial", 12))
        responsible_label.pack(pady=5)

        start_date_label = tk.Label(frame, text=f"Start Date: {task['Start Date']}", font=("Arial", 12))
        start_date_label.pack(pady=5)

        deadline_date_label = tk.Label(frame, text=f"Deadline Date: {task['Deadline Date']}", font=("Arial", 12))
        deadline_date_label.pack(pady=5)

        priority_label = tk.Label(frame, text=f"Priority: {'Yes' if task['Priority'] else 'No'}", font=("Arial", 12))
        priority_label.pack(pady=5)

        conclused_label = tk.Label(frame, text=f"Conclused: {'Yes' if task['Conclused'] else 'No'}", font=("Arial", 12))
        conclused_label.pack(pady=5)

        # Centralizes details window
        details_window.geometry("+{}+{}".format(
            int(details_window.winfo_screenwidth() / 2 - details_window.winfo_reqwidth() / 2),
            int(details_window.winfo_screenheight() / 2 - details_window.winfo_reqheight() / 2)
        ))

# Load existing tasks from a json file or create a new empty list

if os.path.isfile(TASK_FILE):
    with open(TASK_FILE, 'r') as file:
        tasks = json.load(file)
else:
    tasks = []

style = Style(theme="darkly")
window = style.master

window.title("Task List")

general_frame = tk.Frame(window)
general_frame.pack(padx=10, pady=10)

data_frame = tk.LabelFrame(general_frame, text="Task Details")
data_frame.pack(padx=10, pady=10)

name_label = tk.Label(data_frame, text="Task Name:", font=(None, 12))
name_label.grid(row=0, column=0, padx=10, pady=10)
name_entry = tk.Entry(data_frame)
name_entry.grid(row=0, column=1, padx=10, pady=10)

description_label = tk.Label(data_frame, text="Description:", font=(None, 12))
description_label.grid(row=1, column=0, padx=10, pady=10)
description_entry = tk.Entry(data_frame)
description_entry.grid(row=1, column=1, padx=10, pady=10)

responsible_label = tk.Label(data_frame, text="Responsible:", font=(None, 12))
responsible_label.grid(row=2, column=0, padx=10, pady=10)
responsible_entry = tk.Entry(data_frame)
responsible_entry.grid(row=2, column=1, padx=10, pady=10)

start_date_label = tk.Label(data_frame, text="Start Date (DD/MM/YYYY):", font=(None, 12))
start_date_label.grid(row=3, column=0, padx=10, pady=10)
start_date_entry = tk.Entry(data_frame)
start_date_entry.grid(row=3, column=1, padx=10, pady=10)

deadline_label = tk.Label(data_frame, text="Deadline (DD/MM/YYYY):", font=(None, 12))
deadline_label.grid(row=4, column=0, padx=10, pady=10)
deadline_entry = tk.Entry(data_frame)
deadline_entry.grid(row=4, column=1, padx=10, pady=10)

button_frame = tk.Frame(general_frame)
button_frame.pack(padx=10, pady=10)

add_button = tk.Button(button_frame, text="Add Task", command=add_task)
add_button.pack(side="left", padx=5, pady=10)

edit_button = tk.Button(button_frame, text="Edit Task", command=edit_task_description)
edit_button.pack(side="left", pady=10)

conclused_button = tk.Button(button_frame, text="Mark as Done", command=mark_conclused)
conclused_button.pack(side="left", padx=5, pady=10)

priority_button = tk.Button(button_frame, text="Set Priority", command=set_priority)
priority_button.pack(side="left", padx=5, pady=10)

delete_button = tk.Button(button_frame, text="Delete Task", command=delete_task)
delete_button.pack(side="left", padx=5, pady=10)

search_frame = tk.LabelFrame(general_frame, text="Search")
search_frame.pack(padx=10, pady=10)

search_label = tk.Label(search_frame, text="Search by Name or Responsible:", font=(None, 12))
search_label.pack(padx=10, pady=10)
search_entry = tk.Entry(search_frame)
search_entry.pack(padx=10, pady=10)

search_button = tk.Button(search_frame, text="Search", command=search_tasks)
search_button.pack(padx=10, pady=10)

# Task list
task_list = tk.Listbox(window)
task_list.pack()
task_list.bind("<Double-Button-1>", lambda event: open_details())

update_list()

window.mainloop()