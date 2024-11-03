photo = PhotoImage(file="C:/Users/hp/Pictures/Screenshots/azurepic.png")
resized_photo = photo.subsample(2)
pic_label = Label(left_frame, image=resized_photo)
pic_label.config(width=100, height=100)
pic_label.pack()

heading = Label(left_frame, text="Cloud Resource Cleanup in Azure:\nEfficient Management and Optimization of Azure Resources",
                bg="blue", fg="white", font=("Consolas", 12))
heading.pack(pady=10)

l1 = Label(left_frame, text="CLOUD NAME")
l1.pack(anchor="w", pady=10)
options1 = ["azure", "aws", "gcp"]
cloud_var = StringVar()
dropdown1 = OptionMenu(left_frame, cloud_var, *options1)
dropdown1.pack()

l2 = Label(left_frame, text="RESOURCE")
l2.pack(anchor="w", pady=10)
options2 = ["vm", "ip", "disk"]
resource_var = StringVar()
dropdown2 = OptionMenu(left_frame, resource_var, *options2)
dropdown2.pack()
'''
l3 = Label(left_frame, text="FILTER TAGS")
l3.pack(anchor="w", pady=10)
text1 = "{ 'test_task': ['stress-test'] }"
l10 = Label(left_frame, text=text1)
l10.pack()
text_area1 = Text(left_frame, height=3, width=40)
text_area1.pack()

l4 = Label(left_frame, text="AGE")
l4.pack(anchor="w", pady=10)
text2 = "{ 'days': 2, 'hours': 12 }"
l11 = Label(left_frame, text=text2)
l11.pack()
text_area2 = Text(left_frame, height=3, width=40)
text_area2.pack()

l5 = Label(left_frame, text="OPERATION TYPE")
l5.pack(anchor="w", pady=10)
options3 = ["stop", "delete"]
operation_type_var = StringVar()
dropdown3 = OptionMenu(left_frame, operation_type_var, *options3)
dropdown3.pack()
'''
l6 = Label(left_frame, text="DRY RUN")
l6.pack(anchor="w", pady=10)
options4 = ["--dry_run"]
dry_run_var = StringVar()
dropdown4 = OptionMenu(left_frame, dry_run_var, *options4)
dropdown4.pack()

#submit button
submit_button = Button(left_frame, text="SEARCH", width=15, height=2, command=submit_form)
submit_button.pack(side=LEFT, pady=10, padx=80)

#reset button
#reset_button = Button(left_frame, text="Reset",width=15, height=2, command=lambda: [text_area1.delete(1.0, END), text_area2.delete(1.0, END)])
#reset_button.pack(side=RIGHT, pady=10, padx=80)

# Right side
right_frame = Frame(root)
right_frame.pack(side=RIGHT, padx=50, pady=50)
'''
label7 = Label(right_frame, text="RESULT", anchor="w", padx=20)
label7.pack()
text_box1 = Text(right_frame, height=40, width=100)
text_box1.pack()'''