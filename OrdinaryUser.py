from Guest import *
import tkinter as tk

class OrdinaryUser(Guest):

    def __init__(self, parent, controller):

        super(OrdinaryUser, self).__init__(parent, controller)

        get_own_docs_button = tk.Button(self, text="My Documents", fg="green",command=self.fetch_own_docs)
        get_shared_docs_button = tk.Button(self, text="Shared With Me", fg="green", command=self.fetch_shared_docs)
        get_all_docs_button = tk.Button(self, text="All Documents", fg="green", command=self.fetch_all_docs)
        delete_button = tk.Button(self, text="Delete", command=self.delete_doc)
        create_doc_button = tk.Button(self, text="Create A \n New Document ",
                                      fg="red", command=lambda: self.create_new_doc())
        # create_doc_button.config(height=10, width=10);
        process_complaints_button = tk.Button(self, text="Process Complaints", command=lambda: self.ProcessComplaintsBox(self.userid))
        manage_invite_button = tk.Button(self, text="Manage Invitations", command=self.manage_invitations)
        logout_button = tk.Button(self, text="Log Out", fg="blue", command=lambda: controller.log_out())

        search_field = tk.Entry(self)

        user_search_button = tk.Button(self, text="Search User", command=lambda: self.search_user(search_field.get().lower()))
        document_search_button = tk.Button(self, text="Search Document", command=lambda: self.search_doc(search_field.get().lower()))

        # PLACING THE LABELS
        n = 150
        m = 50

        delete_button.place(x=n + 20, y=m * 8 + 10)
        create_doc_button.place(x=n, y=m * 9.5)
        process_complaints_button.place(x=n + 300, y=m * 9.5)
        manage_invite_button.place(x=n + 300, y=m * 10)
        logout_button.place(x=n + 380, y=m - 20)
        get_all_docs_button.place(x=n-125, y=m*5-35)
        get_own_docs_button.place(x=n-125, y=m*5-15)
        get_shared_docs_button.place(x=n-125, y=m*5+5)


        search_field.place(x=n+50, y=m*4.75)
        user_search_button.place(x=n+240, y=m*4.5)
        document_search_button.place(x=n+240, y=m*5)

    def fetch_own_docs(self):
        docs = DocumentsManager.get_own_docs(self.userid)
        self.refresh_doc_section(docs)

    def fetch_shared_docs(self):
        docs = DocumentsManager.get_shared_docs_for_ou(self.userid)
        self.refresh_doc_section(docs)

    def fetch_all_docs(self):
        docs = DocumentsManager.get_all_docs()
        self.refresh_doc_section(docs)

    def create_new_doc(self):
        box = self.DialogBox()  # create the dialog box to ask for title and scope for creating doc
        self.wait_window(box)  # wait until dialog is closed (info is submitted)
        title = box.init_info['title']
        scope = box.init_info['scope']
        if title and scope:
            new_doc_id = DocumentsManager.create_new_doc(self.userid, scope, str(title)) # get new_doc_id
            self.controller.opened_docid = new_doc_id  # set currently opened doc_id
            self.controller.create_doc_owner_page()    # create new doc_owner_page
            self.controller.show_frame("DocumentOwnerPage")  # display page

    def delete_doc(self):
        if self.selected_docid:
            if DocumentsManager.is_owner(self.userid, self.selected_docid) or self.controller.is_su(): # SU can delete any doc
                msg_box = tk.messagebox.askquestion("Delete a document",
                                                    "Are you sure you want to delete this document?",
                                                    icon="warning")
                if msg_box == 'yes':
                    DocumentsManager.delete_doc(self.selected_docid)
                    self.docs_section.delete(self.selected_docid)
            else:
                tk.messagebox.showerror("", "You cannot delete a document that is not owned by you!")
        else:
            tk.messagebox.showerror("", "Please select a document!")

    def search_doc(self, document_result):
        # this function returns a list of doc id that contains key words from search field
        list_with_docid = []

        docs = DocumentsManager.get_own_docs(self.userid)

        title_list = list(docs['title'])
        content_list = list(docs['content'])
        docid_list = list(docs.index)

        counter = 0
        for iz in range(0, len(title_list)):
            # check the document that match keywords entered in the search bar
            if str(document_result).upper() in str(title_list[iz]).upper():
                list_with_docid.append(docid_list[iz])
                counter += 1
            elif str(document_result).upper() in str(content_list[iz]).upper():
                list_with_docid.append(docid_list[iz])
                counter += 1

        if counter == 0:
            tk.messagebox.showerror("Error", "No Such Document found")

        self.display_search_doc_results(list_with_docid)
        return list_with_docid

    def display_search_doc_results(self, docid_list):
        docs_df = pd.DataFrame()
        for docid in docid_list:
            docs_df = docs_df.append(DocumentsManager.get_doc_info(docid).to_frame().transpose())
        self.refresh_doc_section(docs_df)

    def search_user(self, result):
        self.SearchResultBox(result)

    def manage_invitations(self):
        self.ManageInvitationsBox(self.userid)

    class ProcessComplaintsBox(tk.Toplevel):
        # This class is a pop up box taht let user to see complaints they received
        def __init__(self, userid):
            tk.Toplevel.__init__(self)

            self.title("Process Complaints")

            self.userid = userid

            self.selected_complaint = ''

            self.complaints_section = ttk.Treeview(self, height=6, show=['headings'],
                                                   columns=['id', 'complainer', 'complainee', 'doc_title', 'version', 'processed'])
            self.complaints_section.heading('id', text='id', anchor=tk.CENTER)
            self.complaints_section.heading('complainer', text='Complainer', anchor=tk.CENTER)
            self.complaints_section.heading('complainee', text='Complainee', anchor=tk.CENTER)
            self.complaints_section.heading('doc_title', text='Document Title', anchor=tk.CENTER)
            self.complaints_section.heading('version', text='Version Number', anchor=tk.CENTER)
            self.complaints_section.heading('processed', text='Processed', anchor=tk.CENTER)
            self.complaints_section.column('id', minwidth=20, width=40)
            self.complaints_section.column('complainer', minwidth=20, width=100)
            self.complaints_section.column('complainee', minwidth=20, width=100)
            self.complaints_section.column('doc_title', minwidth=20, width=150)
            self.complaints_section.column('version', minwidth=20, width=40)
            self.complaints_section.column('processed', minwidth=20, width=70)

            vsb = ttk.Scrollbar(self, orient="vertical", command=self.complaints_section.yview)
            self.complaints_section.configure(yscrollcommand=vsb.set)
            self.complaints_section.bind('<Button-1>', self.on_select_complaint)

            self.complaint_content_section = tk.Text(self, height=3, width=60,
                                                     highlightbackground="black", highlightcolor="black",
                                                     highlightthickness=1)
            self.doc_content_section = tk.Text(self, height=20, width=60, highlightbackground="black", highlightcolor="black",
                                               highlightthickness=1)

            all_complaints_button = tk.Button(self, text="All Complaints", command=self.show_all_complaints)
            unprocessed_button = tk.Button(self, text="Unprocessed Complaints", command=self.show_unprocessed)
            process_button = tk.Button(self, text="Mark as Processed", command=self.mark_as_processed)
            delete_button = tk.Button(self, text="Delete", command=self.delete_complaint)
            back_button = tk.Button(self, text="Back", command=self.destroy)

            complaint_label = tk.Label(self, text="Complaint: ")
            doc_content_label = tk.Label(self, text="Document Content: ")

            complaint_label.grid(row=5, column=0)
            doc_content_label.grid(row=6, column=0)
            all_complaints_button.grid(row=0, column=1)
            unprocessed_button.grid(row=1, column=1)
            self.complaints_section.grid(row=2, column=1)
            self.complaint_content_section.grid(row=5, column=1)
            self.doc_content_section.grid(row=6, column=1)
            process_button.grid(row=3, column=1)
            delete_button.grid(row=4, column=1)
            back_button.grid(row=4, column=2)

            # populate complaints and content section
            self.complaints_received = ComplaintsManager.get_complaints_received(userid)
            self.unprocessed = ComplaintsManager.get_unprocessed_complaints(userid)
            self.show_complaints(self.complaints_received)

        def on_select_complaint(self, event):
            selected_complaint = int(self.complaints_section.identify_row(event.y))
            if selected_complaint is not None:
                self.selected_complaint = selected_complaint
                selected_complaint_seq_id = self.complaints_received.loc[self.selected_complaint]['seq_id']
                if DocumentsManager.is_current_version(selected_complaint_seq_id):
                    doc_content = DocumentsManager.get_doc_info(int(selected_complaint_seq_id.split('-')[0]))['content']
                else:
                    doc_content = DocumentsManager.retrieve_old_version(selected_complaint_seq_id)
                self.refresh_doc_content_section(doc_content)
                self.refresh_complaint_content_section(self.complaints_received.loc[selected_complaint]['content'])

        def refresh_complaint_content_section(self, content):
            self.complaint_content_section.delete(1.0, tk.END)
            self.complaint_content_section.insert(tk.INSERT, content)

        def refresh_doc_content_section(self, content):
            self.doc_content_section.delete(1.0, tk.END)
            self.doc_content_section.insert(tk.INSERT, content)

        def show_complaints(self, complaints_df):
            for complaint in self.complaints_section.get_children():
                self.complaints_section.delete(complaint)
            if not complaints_df.empty:
                for complaint_id, row in complaints_df.iterrows():
                    if row['complainer_id'] == 0:
                        complainer_name = 'Guest'
                    else:
                        complainer_name = AccountsManager.get_username(row['complainer_id']),

                    info_tuple = (
                        complaint_id,
                        complainer_name,
                        AccountsManager.get_username(row['complainee_id']),
                        DocumentsManager.get_doc_info(int(row['seq_id'].split('-')[0]))['title'],
                        int(row['seq_id'].split('-')[1]),
                        row['processed']
                    )
                    self.complaints_section.insert('', tk.END, iid=complaint_id, values=info_tuple)


        def show_all_complaints(self):
            self.complaints_received = ComplaintsManager.get_complaints_received(self.userid)
            self.show_complaints(self.complaints_received)

        def show_unprocessed(self):
            self.unprocessed = ComplaintsManager.get_unprocessed_complaints(self.userid)
            self.show_complaints(self.unprocessed)

        def delete_complaint(self):
            self.complaints_section.delete(self.selected_complaint)
            ComplaintsManager.remove_complaint(self.selected_complaint)

        def mark_as_processed(self):
            ComplaintsManager.mark_as_processed(self.selected_complaint)

    class ManageInvitationsBox(tk.Toplevel):
        # This class is a popup box that allows user to accept/reject invitations

        def __init__(self, userid):
            tk.Toplevel.__init__(self)

            self.userid = userid
            self.title("Manage Invitations")
            self.invitations_received = InvitationsManager.get_invitations(userid)

            self.invitations_section = ttk.Treeview(self, height=6, show=['headings'],
                                                    columns=['inviter', 'title', 'time'])
            self.invitations_section.heading('inviter', text='Inviter')
            self.invitations_section.heading('title', text='Document Title')
            self.invitations_section.heading('time', text='Received at')
            self.invitations_section.column('inviter', minwidth=0, width=100)
            self.invitations_section.column('title', minwidth=0, width=150)
            self.invitations_section.column('time', minwidth=0, width=160)

            vsb = ttk.Scrollbar(self, orient="vertical", command=self.invitations_section.yview)
            self.invitations_section.configure(yscrollcommand=vsb.set)

            accept_button = tk.Button(self, text="Accept", command=self.accept_invite)
            reject_button = tk.Button(self, text="Reject", command=self.reject_invite)
            back_button = tk.Button(self, text="Back", command=self.destroy)

            self.invitations_section.grid(row=0)
            vsb.grid(row=0, column=1, sticky='nse')
            accept_button.grid(row=1)
            reject_button.grid(row=2)
            back_button.grid(row=3)

            # filter our the invites that have been rejected
            self.invitations_received = self.invitations_received.loc[self.invitations_received['rejected'] == False]
            # populate invitations section
            if not self.invitations_received.empty:
                for index, row in self.invitations_received.iterrows():
                    info_tuple = (
                        AccountsManager.get_username(row['inviter_id']),
                        DocumentsManager.get_doc_info(row['doc_id'])['title'],
                        row['time']
                    )
                    self.invitations_section.insert('', tk.END, iid=row['doc_id'], values=info_tuple)

        def accept_invite(self):
            selected_invite_docid = int(self.invitations_section.selection()[0])
            InvitationsManager.accept_invitation(self.userid, selected_invite_docid)
            tk.messagebox.showinfo("", "Accepted invitation successfully. You can now contribute to the document!")
            self.invitations_section.delete(selected_invite_docid)

        def reject_invite(self):
            selected_invite_docid = int(self.invitations_section.selection()[0])
            InvitationsManager.reject_invitation(self.userid, selected_invite_docid)
            tk.messagebox.showinfo("", "You have rejected the invitation successfully.")
            self.invitations_section.delete(selected_invite_docid)

    class DialogBox(tk.Toplevel):
        # This class is a dialog box that asks user for title and scope of doc upon creating new doc

        def __init__(self):
            tk.Toplevel.__init__(self)

            self.init_info = {
                'title': '',
                'scope': ''
            }

            self.title("Creating a new document")
            title_label = tk.Label(self, text="Title: ")
            scope_label = tk.Label(self, text="Scope: ")
            title_entry = tk.Entry(self)
            OPTIONS = [
                "Private",
                "Shared",
                "Restricted",
                "Public"
            ]
            variable = tk.StringVar(self)
            variable.set("Private")
            scopes_drop_down = tk.OptionMenu(self, variable, *OPTIONS)
            submit_button = tk.Button(self, fg="red", text="Submit", command=lambda : self.on_submit(
                title_entry.get(), variable.get()))
            cancel_button = tk.Button(self, text="Cancel", command=self.destroy)

            title_label.grid(row=0)
            scope_label.grid(row=1)
            title_entry.grid(row=0, column=1)
            scopes_drop_down.grid(row=1, column=1)
            submit_button.grid(row=2, column=1)
            cancel_button.grid(row=2, column=0)

        def on_submit(self, title, scope):
            if not title:
                tk.messagebox.showerror("", "You must fill out the title field in order to create a document!")
            else:
                self.init_info['title'] = title
                self.init_info['scope'] = scope
                self.destroy()

    # this class helps is invoked to display search results of user in a document page
    class SearchResultBox(tk.Toplevel):

        def __init__(self, user_result):
            # this is passed as keyword in the text field of the search bar
            tk.Toplevel.__init__(self)
            self.user_result=user_result
            self.title("User Search Results")

            # read the user info database
            user_db = AccountsManager.get_all_users()
            user_db = user_db.loc[user_db['usertype'] != 'DeletedUser']

            # list that stores all the user names
            user_list = list(user_db['username'])
            # list that stores all the technical interest for all user in the respective index of the user
            technical_list = list(user_db['technical_interest'])
            # empty list to store the index of username matched
            index_list = []
            # check if any username matches the searched input

            # make a list box
            username_list = tk.Listbox(self, height=10)#,width=10)
            # setting the title for the listbox
            username_list.insert(tk.END, "Users")
            # lopping through the names of usernames
            for names in range(0,len(user_list)):
                # check if text in search bar has anything from the name in the database
                # if user_list[names] != "DeletedUser":
                if self.user_result.upper() in user_list[names].upper():
                    username_list.insert(tk.END, user_list[names])
                    # keeping track of the indexes added to add the corresponding technical interests
                    index_list.append(names)
                elif self.user_result.upper() in technical_list[names].upper():
                    username_list.insert(tk.END, user_list[names])
                    # keeping track of the indexes added to add the corresponding technical interests
                    index_list.append(names)

            # make a list box for technical interest
            technical_interest_list=tk.Listbox(self, height=10)
            # setting the title for the listbox
            technical_interest_list.insert(tk.END, "Technical Interest")
            # looping through the indexes added in the username_list
            for index in index_list:
                # add that specific index of the technical_list
                technical_interest_list.insert(tk.END, technical_list[index])

            # cancel button to go back to the main page
            cancel_button=tk.Button(self, text="Cancel", command=self.destroy)

            # setting up the layout of the dialog box
            username_list.grid(row=0, column=0)
            technical_interest_list.grid(row=0, column=1)
            cancel_button.grid(row=1, column=0)

            # this is the case when there is no match which simply destroys the box
            # then prints an error message box in the screen
            # as index_list is updated when a match is found its length being 0 confirm no match
            if len(index_list) == 0:
                self.destroy()
                tk.messagebox.showerror("Error", "No Such User found")
