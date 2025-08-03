import customtkinter as ctk
import json
import random
from CTkMessagebox import CTkMessagebox
import keyboard
import threading
import time

ctk.set_default_color_theme("dark-blue")

with open('words_dictionary.json', 'r') as file:
    data = json.load(file)

def group_by_length(input_set):
        grouped = {}
        for value in input_set:
            length = len(value)
            if length not in grouped:
                grouped[length] = 1
            else:
                 grouped[length] += 1

        pop = []
        for key, value in grouped.items():
            if value < 10:
                 pop.append(key)
                

        for key in pop:
            grouped.pop(key)
        return grouped

word_len_list = group_by_length(data)
word_len_possible , word_len_size = zip(*sorted(list(word_len_list.items())))
word_len_possible  = [str(x) for x in word_len_possible ]




def check_if_closed(method):
        def wrapper(self, *args, **kwargs):
            if self.is_closed:
                return  
            return method(self, *args, **kwargs)
        try:
            return wrapper
        except:
            return

class Guesser(ctk.CTk):
    def __init__(self, word_len=5, no_tries=6, data=None):
        try:
            super().__init__()
            X_size = str(max(40*word_len,400))
            Y_size = str(max(40*no_tries+270,0))
            size = f"{X_size}x{Y_size}"
            self.geometry(size)
            self.title("Wordle - player")
            if data is None:
                data = []
            self.no_tries = no_tries
            self.word_len = word_len
            self.user_x = 0
            self.user_y = 0
            self.is_closed = False
            self.warning_active = False
            self.keyboards_row = []
            self.key_press_in_progress = {}
            self.cooldown = False


            self.filtered_set = {item for item in data if len(item) == self.word_len}
            print("Number of filtered words:", len(self.filtered_set))
        
        
            if self.filtered_set:
                self.word_to_guess = str(random.choice(list(self.filtered_set)))
                self.answer = list(self.word_to_guess)
                print("Answer :",self.word_to_guess)
            else:
                self.word_to_guess = None
                CTkMessagebox(message=f"No valid words to guess. Please input a shorter word length.",icon="warning", option_1="Close",title="Can not start game")
                self.destroy()


            


            char_keys = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P','A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L','Z', 'X', 'C', 'V', 'B', 'N', 'M','enter','backspace']
            for key in char_keys:
                keyboard.on_press_key(key, self.handle_key_press)
            #keyboard.wait("esc")


            self.title_f = ctk.CTkFrame(self)
            self.title_f.pack(padx=10, pady=(3, 3), fill="x") 
            self.title = ctk.CTkLabel(self.title_f, text="WORDLE",height=20 ,text_color = ("#727EFF"),font=("Comic Sans MS", 30))
            self.title.pack(side=ctk.BOTTOM, padx=2)

            self.attempts = []
            self.table = ctk.CTkFrame(self)
            self.table.pack(padx=10, pady=(10, 10), fill="both", expand=True)

            label_size = 30  

            for i in range(no_tries):
                row_frame = ctk.CTkFrame(self.table)
                row_frame.pack(pady=5)
                self.attempts.append([])  

                for _ in range(word_len):
                    label = ctk.CTkLabel(row_frame, width=label_size, height=label_size, text=" ")
                    label.pack(side=ctk.LEFT, padx=2)
                    self.attempts[i].append(label)  

            self.message_f = ctk.CTkFrame(self)
            self.message_f.pack(padx=10, pady=(3, 3), fill="x") 
            self.row_message = ctk.CTkFrame(self.message_f)
            self.row_message.pack(pady=5)
            self.message = ctk.CTkLabel(self.row_message, text="",height=4 )
            self.message.pack(side=ctk.BOTTOM, padx=2)


            self.frame = ctk.CTkFrame(self)
            self.frame.pack(padx=10, pady=(10, 10), fill="x")  
            
            self.create_keyboard(self.frame)
        except:
            pass
        
    
    
    
    
    @check_if_closed
    def update_label(self, attempt_index, letter_index, letter):
        try:
            if (0 <= attempt_index < len(self.attempts) and 
                    0 <= letter_index < len(self.attempts[attempt_index])):
                self.attempts[attempt_index][letter_index].configure(text=letter)
            else:
                pass
        except:
            pass

    def end_game(self,win, answer):
            self.message.configure(text = f"Answer : {str(answer).upper()}")
            if win:
                CTkMessagebox(message=f'You Win the game , the answer is "{answer.upper()}" !',icon="check", option_1="Close",title="YOU WIN")
                
            else:
                CTkMessagebox(message=f'You Fail the game , the answer is "{answer.upper()}" !',icon="warning", option_1="Close",title="SKILL ISSUE")

            
            self.destroy()

        
    @check_if_closed
    def clear_input(self,attempt_index):
        for i in range(len(self.attempts[attempt_index])):
            self.attempts[attempt_index][i].configure(text=" ")
            self.user_x = 0



    @check_if_closed
    def check_answer(self, attempt_index):
        self.cooldown = True
        input = ""
        color = ["#474747" for _ in range(len(self.attempts[attempt_index]))]
        for i in range(len(self.attempts[attempt_index])):
            input += str(self.attempts[attempt_index][i].cget("text"))

        output = self.answer.copy()
        input = input.lower()
        print("player input:",input)
        
        def reset_warning():
            if self.warning_active:
                self.message.configure(text_color="#FFFFFF", text="")
                self.warning_active = False  

        def Start_warning():
            self.message.configure(text_color="#FFA4A4", text="Word not in list") 
            threading.Timer(0.5, show_warning).start()

        def show_warning():
            self.warning_active = True 
            threading.Timer(2, reset_warning).start()

        

        if input not in self.filtered_set:
            self.message.configure(text = f"Word not in list")
            self.message.configure(text_color = "#FF0000")
            self.warning_active = False
            get = threading.Timer(0.1, Start_warning)
            get.start()
            
        
            
        else:
            for i in range(len(self.attempts[attempt_index])):
                Char = input[i]
                if Char == self.answer[i]:
                    #self.attempts[attempt_index][i].configure(fg_color="#00793C")
                    color[i] = "#00793C"
                    self.update_keyboard(Char,"#00793C")
                    try:
                        output.remove(Char)
                    except:
                        pass

            for i in range(len(self.attempts[attempt_index])):
                Char = input[i]    
                if (Char != self.answer[i] and Char in output):
                    #self.attempts[attempt_index][i].configure(fg_color="#697223")
                    color[i] = "#697223"
                    self.update_keyboard(Char,"#697223")
                    try:
                        output.remove(Char)
                    except:
                        pass
                elif (Char != self.answer[i] and Char not in output):
                    self.update_keyboard(Char,"#474747")
                    try:
                        output.remove(Char)
                    except:
                        pass

            label_size = 30 
            for i in range(len(self.attempts[attempt_index])):
                self.attempts[attempt_index][i].configure(fg_color="#C4C4C4")
                time.sleep(0.1)
                self.attempts[attempt_index][i].configure(fg_color=color[i])


            
                
            self.user_x = 0
            self.user_y += 1

            
            if input == self.word_to_guess:
                self.end_game(True,self.word_to_guess)
            elif self.user_y >= self.no_tries :
                self.end_game(False,self.word_to_guess)
        self.cooldown = False



            



    
    @check_if_closed
    def update_keyboard(self,key = "", color = ""):
        for row in self.keyboards_row[:-1]:
            for i in row:
                if i.cget("fg_color")[0] != "#00793C" and i.cget("text") == key.upper():
                    i.configure(fg_color=color)
                
    @check_if_closed
    def create_keyboard(self, frame):
        keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['Enter', 'Clear','<-']
        ]

        self.keyboards_row = []
        for i,row in enumerate(keys):
            row_frame = ctk.CTkFrame(frame)
            row_frame.pack(pady=5)
            self.keyboards_row.append([])  
            for key in row:
                button = ctk.CTkButton(row_frame, text=key, command=lambda k=key: self.key_press(k), width=5, height=5)
                button.pack(side=ctk.LEFT, padx=2)
                self.keyboards_row[i].append(button)

    @check_if_closed
    def key_press(self, key):
        if self.cooldown == False:
            if key == "Enter":
                if self.user_x >= self.word_len:
                    #print("Checking guess...")
                    threading.Timer(0, self.check_answer,[self.user_y]).start()
            elif key == "Clear":
                #print("Clearing input...")
                self.clear_input(self.user_y)
            elif key == "<-":
                if 0 < self.user_x <= self.word_len:
                    self.update_label(self.user_y,self.user_x," ")
                    self.user_x -= 1
            else:
                self.update_label(self.user_y,self.user_x,key)
                if self.user_x < self.word_len:
                    self.user_x += 1
            
            self.update_label(self.user_y,self.user_x,"_")
                
    
    @check_if_closed
    def handle_key_press(self,event):
        try:
            if self.focus_get() == self and self.cooldown == False:
                if str(event.name) == "enter":
                    Char = Char = str(event.name).title()
                elif str(event.name) == "backspace":
                    Char = "<-" 
                else:
                    Char = str(event.name).upper()
                    
                self.key_press(Char)
                for row in self.keyboards_row:
                    for i in row:
                        if i.cget("text") == Char:
                            color = i.cget("fg_color")
                            t_color = i.cget("text_color")

                            if not self.key_press_in_progress.get(Char, False):
                                self.key_press_in_progress[Char] = True
                                i.configure(fg_color="#FFFFFF", text_color="#000000")
                                threading.Timer(0.05, self.update_click_color, [i, color, t_color, Char]).start()

        except:
            pass

    @check_if_closed
    def update_click_color(self, key, color, t_color, Char):
        key.configure(fg_color=color, text_color=t_color)
        self.key_press_in_progress[Char] = False


        



class Word_Generate(ctk.CTk):
    try:
        def __init__(self):
            super().__init__()
            self.title("Wordle")
            self.geometry("400x300")


            self.frame = ctk.CTkFrame(self)
            self.frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

            self.label1 = ctk.CTkLabel(self.frame, text="Please Enter The Length of the word:")
            self.label1.grid(row=0, column=0, padx=(10,2), pady=(10, 0), sticky="w")

            combobox_var = ctk.StringVar(value="5")
            self.entry1 = ctk.CTkComboBox(self.frame, values=word_len_possible,variable=combobox_var, command=self.update_possible_answer)
            self.entry1.grid(row=0, column=1, padx=(2,10), pady=(10, 0), sticky="ew")


            self.label2 = ctk.CTkLabel(self.frame, text="Please Enter The Number of Tries:")
            self.label2.grid(row=1, column=0, padx=(10,2), pady=(20, 0), sticky="w")


            self.entry2 = ctk.CTkEntry(self.frame, placeholder_text="Enter Number of Tries",textvariable =	ctk.StringVar(value="6"))
            
            self.entry2.grid(row=1, column=1, padx=(2,2), pady=(20, 0), sticky="ew")

            self.tips2 = ctk.CTkLabel(self.frame, text=f"Number of Possible Answer: {str(word_len_list[int(self.entry1.get())])}")
            self.tips2.grid(row=2, column=0, padx=10, pady=(20, 20), sticky="w")
            self.tips = ctk.CTkLabel(self.frame, text=f"")
            self.tips.grid(row=3, column=0, padx=10, pady=(20, 5), sticky="ew")

            self.submit_button = ctk.CTkButton(self.frame, text="Submit", command=self.store_integers)
            self.submit_button.grid(row=4, column=0, padx=10, pady=(5, 50), sticky="ew")


            self.frame.grid_rowconfigure(1, weight=1)
            self.frame.grid_rowconfigure(3, weight=1)
            self.frame.grid_columnconfigure(0, weight=1)



            self.integers = []
    except:
        pass

    def update_possible_answer(self,choice):
        self.tips2.configure(text=f"Number of Possible Answer: {str(word_len_list[int(self.entry1.get())])}")
        

    def store_integers(self):
        try:
            word_length = int(self.entry1.get())
            no_of_try = int(self.entry2.get())
            print("Length of the word:", word_length, "| Number of Tries:", no_of_try)
            
            if word_length <= 1 or no_of_try <= 1:
                self.tips.configure(text="Please enter values greater than 1.")
                return
            if no_of_try > 15:
                self.tips.configure(text="Number of tries cannot exceed 15.")
                return
            
            guesser = Guesser(word_length, no_of_try, data)
            guesser.mainloop()
        except ValueError:
            self.tips.configure(text="Please enter valid integers.")


app = Word_Generate()
app.mainloop()




