import customtkinter as ct
import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import pytesseract
import numpy as np
import time
from googletrans import Translator
from tkinter import filedialog as fd
import easyocr
from CTkScrollableDropdown import *
import os
import glob
import warnings

warnings.filterwarnings("ignore")

lang_dict = {}
lang_list = []

lang_dict2 = {}
lang_list2 = [] 
translate_check = False

lang_file = open("lang.txt", "r")
langs = lang_file.readlines()

for lang in langs:
    temp = lang.rstrip("\n")
    store = temp.split()
    lang_dict[store[0].rstrip(":")] = store[1]

lang_list = list(lang_dict.keys())

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

width, height = 1200, 1200

# url = "https://192.168.1.5:8080/video"
url = "http://10.24.92.98:8080/video"

vid = cv2.VideoCapture(0)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

vid2 = cv2.VideoCapture(url)
vid2.set(cv2.CAP_PROP_FRAME_WIDTH, width)
vid2.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


def window_clear():
    win_inf = main_window.winfo_children()
    for i in range(0,len(win_inf)):
        win_inf[i].destroy()
    return


def home():
    window_clear()
    main()


def translate_text(text, target_language):
    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        translated_text = translation.text
        return translated_text
    except Exception as e:
        return 0


def translate(text):
    global lang_list
    global originalDisplayBox
    global translate_check
    global translatedDisplayBox
    global output2Label
    
    translate_pop = ct.CTkToplevel()
    translate_pop.title("Translate")
    translate_pop.geometry("300x250")
    
    transto = ct.CTkLabel(translate_pop, text="Translate To", font = ("Century Gothic", 25, "bold"))
    transto.place(x=20, y=10)

    entry_lang = ct.CTkComboBox(translate_pop, values=lang_list, font = ("Century Gothic", 20, "bold"), width=255)
    entry_lang.place(x=20, y=55)

    entry_lang.set(lang_list[0])
    dropdown = CTkScrollableDropdown(entry_lang, values=lang_list, justify="left", button_color="transparent", autocomplete=True, font = ("Century Gothic", 20), width=255, height=160)


    def lang_get():
        global translate_check
        global translatedDisplayBox
        global output2Label

        selected_value = str(dropdown.get_selected_value())
        lang_code = str(lang_dict[selected_value])
        translated_text = translate_text(text, lang_code)

        if translated_text == 0:
            messagebox.showerror("Translation not available", "The text cannot be translated into language you selected")
        else:
            originalDisplayBox.configure(width=360)
            output2Label.place(x=500, y=516)

            translatedDisplayBox.place(x=505, y=550)
            translate_check = True

            translatedDisplayBox.configure(state="normal")
            translatedDisplayBox.delete("1.0", tk.END)
            translatedDisplayBox.insert(tk.END,translated_text)
            translatedDisplayBox.configure(state="disabled")
            translate_pop.destroy()

    translateButton = ct.CTkButton(master=translate_pop, text="Translate",command=lang_get ,width=150,  font=("Century Gothic", 20, "bold"))
    translateButton.place(x=70,y=180)

    translate_pop.mainloop()


def export():
    global translate
    global originalDisplayBox
    global translatedDisplayBox
    
    export_pop = ct.CTkToplevel()
    export_pop.title("Export")
    export_pop.geometry("300x280")

    filename = ct.CTkLabel(export_pop, text="File Name", font = ("Century Gothic", 23, "bold"))
    filename.place(x=20, y=10)
    filenameEntry = ct.CTkEntry(export_pop, font = ("Century Gothic", 20), width=255)
    filenameEntry.place(x=20,y=50)

    def export_file(*args):
        global originalDisplayBox
        text_storeOriginal = originalDisplayBox.get(1.0,tk.END)

        trans_store = checkbox.get()
        print(trans_store)
        file_name = filenameEntry.get()

        file = open(f"{file_name}.txt", "w")

        if trans_store == "off":
            file.write(text_storeOriginal)
        else:
            text_storeTranslated = translatedDisplayBox.get(1.0,tk.END)
            final = f"Original Text:\n{text_storeOriginal}\n\nTranslated Text:\n{text_storeTranslated}"

            file.write(final)

        file.close()
        export_pop.destroy()

    if translate_check:
        checkbox = ct.CTkCheckBox(master=export_pop, text="Export Translated Text", onvalue="on", offvalue="off", font=("Century Gothic", 18))
        checkbox.place(x=20, y=110)
    else:
        pass
    
    exportButton = ct.CTkButton(master=export_pop, text="Export" ,width=150,  font=("Century Gothic", 20, "bold"), command=export_file)
    exportButton.place(x=70,y=230)

    export_pop.mainloop()
    

def remove_empty_lines(text):
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)


def easyocr2(image_path, language='en'):
    try:
        reader = easyocr.Reader([language])

        result = reader.readtext(image_path)

        # Extract and return the text from the result
        text = '\n'.join([entry[1] for entry in result])
        text = remove_empty_lines(text)
        return text

    except Exception as e:
        return "Extract Error TT02"


def tesserectocr(image,language="jpn"):
    try:
        text = pytesseract.image_to_string(image, lang=language)
        text = remove_empty_lines(text)
        return text
    except:
        return "Extract Error TT02"
    

def getText(image_name, mode, ocrmode,language="en"):
    global originalDisplayBox
    global translatedDisplayBox
    global output2Label

    getTextButton.destroy()
    goBackButton.destroy()

    if mode == 0:
        path = f"Snaps\{image_name}"
    else:
        path = image_name

    files = glob.glob('M:/FIP/Snaps/Processed/*')
    for f in files:
        os.remove(f)

    img = cv2.imread(path, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (370, 223))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

    gray = cv2.bitwise_not(img)

    cv2.imwrite(f"M:\FIP\Snaps\Processed\gray2.png", gray)

    _, img2 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    cv2.imwrite(f"M:\\FIP\\Snaps\\Processed\\threshed.png", img2)

    kernel = np.ones((1, 1), np.uint8)

    dilated = cv2.dilate(img2, kernel, iterations=1)
    dilated = cv2.cvtColor(dilated, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f"M:\FIP\Snaps\Processed\dilated.png", dilated)

    gray_disp = tk.PhotoImage(file=f"M:\FIP\Snaps\Processed\gray2.png")
    thresh_disp = tk.PhotoImage(file=f"M:\\FIP\\Snaps\\Processed\\threshed.png")
    dilated_disp = tk.PhotoImage(file=f"M:\\FIP\\Snaps\\Processed\\dilated.png")

    grayShow = ct.CTkLabel(main_window,text="" ,image=gray_disp)
    grayShow.place(x=530,y=60)

    threhShow = ct.CTkLabel(main_window,text="" ,image=thresh_disp)
    threhShow.place(x=530,y=300)

    dilatedShow = ct.CTkLabel(main_window,text="" ,image=dilated_disp)
    dilatedShow.place(x=70,y=300)

    if int(ocrmode) == 0:
        text = tesserectocr(dilated)

    elif int(ocrmode) == 1:
        text = easyocr2(dilated)


    if text == "Extract Error TT02":
        text=""
        messagebox.showerror("Extraction Failed", "Extraction failed from image")


    outputLabel = ct.CTkLabel(main_window, text="Output Text",font=("Century Gothic", 20, "bold"))
    outputLabel.place(x=73, y=516)

    output2Label = ct.CTkLabel(main_window, text="Translated Text",font=("Century Gothic", 20, "bold"))

    originalDisplayBox = ct.CTkTextbox(main_window, height = 80, width = 752, font=("Century Gothic",14))
    originalDisplayBox.place(x=70,y=550)

    originalDisplayBox.insert(tk.END, text)
    originalDisplayBox.configure(state="disabled")

    translatedDisplayBox = ct.CTkTextbox(main_window, height = 80, width = 360, font=("Century Gothic",14))

    translateButton = ct.CTkButton(master=main_window, text="Translate", command=lambda text_pass=text :translate(text_pass), width=150,  font=("Century Gothic", 20, "bold"))
    translateButton.place(x=75,y=650)

    exportButton = ct.CTkButton(master=main_window, text="Export", command=export, width=150,  font=("Century Gothic", 20, "bold"))
    exportButton.place(x=370,y=650)

    homeButton = ct.CTkButton(master=main_window, text="Home", command=home, width=150,  font=("Century Gothic", 20, "bold"))
    homeButton.place(x=660,y=650)


def image_confirmation(image_name, mode, ocrmode,lang="eng"):
    global translate_check
    translate_check = False
    window_clear()
    global getTextButton
    global goBackButton

    if mode == 0:
        image_confirm = (Image.open(f"Snaps\{image_name}"))
    else:
        image_confirm = (Image.open(image_name))
    
    image_confirm = ImageTk.PhotoImage(image_confirm.resize((370, 223)))

    originalLabel = ct.CTkLabel(main_window, text="Original Image",font=("Century Gothic", 20, "bold"))
    originalLabel.place(x=140, y=25)

    imageShow = ct.CTkLabel(main_window, image=image_confirm, text="")
    imageShow.place(x=70,y=60)

    grayLabel = ct.CTkLabel(main_window, text="Gray Image",font=("Century Gothic", 20, "bold"))
    grayLabel.place(x=620, y=25)

    dilateLabel = ct.CTkLabel(main_window, text="Dilated Image",font=("Century Gothic", 20, "bold"))
    dilateLabel.place(x=140, y=265)

    threshLabel = ct.CTkLabel(main_window, text="Threshed Image",font=("Century Gothic", 20, "bold"))
    threshLabel.place(x=620, y=265)

    getTextButton = ct.CTkButton(master=main_window, text="Get Text", width=350,  font=("Century Gothic", 25, "bold"), command=lambda x=image_name:getText(x, mode, ocrmode,lang))
    getTextButton.place(x=275,y=580)

    goBackButton = ct.CTkButton(master=main_window, text="Go Back", command=photo, width=350,  font=("Century Gothic", 25, "bold"))
    goBackButton.place(x=275,y=640)


def photo():
    window_clear()

    def snap_pc():
        result,image = vid.read()
        cur_time = int(time.time())
        save_name = f"img_{cur_time}.png"
        image = cv2.resize(image, (800,600))
        cv2.imwrite(f"./Snaps/{save_name}", image)

        # save_name = "Test2.png"
        image_confirmation(save_name,0, ocrmode)

    def snap_mob():
        result,image = vid2.read()
        cur_time = int(time.time())
        save_name = f"img_{cur_time}.png"
        image = cv2.resize(image, (800,600))
        cv2.imwrite(f"./Snaps/{save_name}", image)
        image_confirmation(save_name,0,ocrmode)


    def pc_camera():
        _, frame = vid.read()

        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        opencv_image = cv2.resize(opencv_image, (800, 600))
        captured_image = Image.fromarray(opencv_image)
        
        photo_image = ImageTk.PhotoImage(image=captured_image)
        
        label_widget.photo_image = photo_image
        label_widget.configure(image=photo_image)
        label_widget.after(1, pc_camera)


    def mobile_camera():
        _, frame = vid2.read()

        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        opencv_image = cv2.resize(opencv_image, (800, 600))
        captured_image = Image.fromarray(opencv_image)
        
        photo_image = ImageTk.PhotoImage(image=captured_image)
        
        label_widget.photo_image = photo_image
        label_widget.configure(image=photo_image)
        label_widget.after(1, mobile_camera)
    

    ocrmode = 0

    def start_camera():
        start_mode = int(mode.get())
        ocr_get = int(ocr.get())
        ocrmode = ocr_get

        white_canvas.configure(height=620, width=820)
        white_canvas.place(x=162,y=30)

        snapButton.place(x=275,y=580)
        cancelButton.place(x=275,y=640)
        
        srcLabel.destroy()
        startButton.destroy()
        PC.destroy()
        Mobile.destroy()
        ocrLabel.destroy()
        tes.destroy()
        easy.destroy()

        if start_mode == 1:
            snapButton.configure(command=snap_mob)
            mobile_camera()
        else:
            pc_camera()


    white_canvas = ct.CTkCanvas(main_window, bg="white", height=0, width=0)
    
    label_widget = ct.CTkLabel(main_window, text="")
    label_widget.place(x=138, y=35)

    srcLabel = ct.CTkLabel(master=main_window, text="Camera Source", font=("Century Gothic", 30, "bold"))
    srcLabel.place(x=150, y=50)

    mode= tk.IntVar()
    PC = ct.CTkRadioButton(master=main_window, text="PC", variable=mode, value=0,  font=("Century Gothic", 25))
    PC.place(x=150,y=125)

    Mobile = ct.CTkRadioButton(master=main_window, text="Mobile", variable=mode, value=1,  font=("Century Gothic", 25) )
    Mobile.place(x=150,y=175)

    ocrLabel = ct.CTkLabel(master=main_window, text="OCR Choice", font=("Century Gothic", 30, "bold"))
    ocrLabel.place(x=500, y=50)

    ocr= tk.IntVar()
    tes = ct.CTkRadioButton(master=main_window, text="EasyOCR", variable=ocr, value=0,  font=("Century Gothic", 25))
    tes.place(x=500,y=125)

    easy = ct.CTkRadioButton(master=main_window, text="TesseractOCR", variable=ocr, value=1,  font=("Century Gothic", 25) )
    easy.place(x=500,y=175)

    startButton = ct.CTkButton(main_window, text="Start", command=start_camera, width=350,  font=("Century Gothic", 25, "bold"))
    startButton.place(x=275,y=325)

    snapButton = ct.CTkButton(main_window, text="Snap", command=snap_pc, width=350,  font=("Century Gothic", 25, "bold"))
    cancelButton = ct.CTkButton(main_window, text="Back", command=home, width=350,  font=("Century Gothic", 25, "bold"))
    cancelButton.place(x=275,y=400)


def browse():
    window_clear()

    def proceed():
        image = pathEntry.get()
        ocr_mode = int(ocr.get())
        image_confirmation(image,1,ocr_mode)

    def browse():
        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=[("Image",[".jpg", ".png"])])
        
        pathEntry.delete(0,tk.END)
        pathEntry.insert(tk.END, filename)


    pathLabel = ct.CTkLabel(master=main_window, text="File Path: ", font=("Century Gothic", 30, "bold"))
    pathLabel.place(x=70, y=50)
    pathEntry = ct.CTkEntry(main_window, width=500, font=("Century Gothic", 22))
    pathEntry.place(x=210, y=53)

    browseButton = ct.CTkButton(main_window, text="Browse",command=browse,font=("Century Gothic", 22, "bold"))
    browseButton.place(x=730,y=53)

    ocrLabel = ct.CTkLabel(master=main_window, text="OCR Choice:", font=("Century Gothic", 30, "bold"))
    ocrLabel.place(x=70, y=135)

    ocr= tk.IntVar()
    tes = ct.CTkRadioButton(master=main_window, text="EasyOCR", variable=ocr, value=1,  font=("Century Gothic", 25))
    tes.place(x=285,y=140)

    easy = ct.CTkRadioButton(master=main_window, text="TesseractOCR", variable=ocr, value=0,  font=("Century Gothic", 25) )
    easy.place(x=450,y=140)

    sourceLabel = ct.CTkLabel(master=main_window, text="Source Language:", font=("Century Gothic", 30, "bold"))
    sourceLabel.place(x=70, y=195)

    proceedButton = ct.CTkButton(main_window, text="Proceed",command=proceed,width=350,font=("Century Gothic", 25, "bold"))
    proceedButton.place(x=275,y=330)

    cancelButton = ct.CTkButton(main_window, text="Back", command=home, width=350,  font=("Century Gothic", 25, "bold"))
    cancelButton.place(x=275,y=400)
    

ct.set_appearance_mode("dark")
ct.set_default_color_theme("pink.json")

main_window = ct.CTk()
main_window.geometry("900x700")
main_window.title("Text Recognition")

def main():
    TitleLabel = ct.CTkLabel(master=main_window, text="Text Recognition and Translation", font=("Century Gothic", 52, "bold"))
    TitleLabel.place(x=40, y=20)

    snapButton = ct.CTkButton(master=main_window, width=350, text="Take a Picture", font=("Century Gothic", 25, "bold"), command=photo)
    snapButton.place(x=275,y=190)

    browseButton = ct.CTkButton(master=main_window,text="Browse Image", width=350,  font=("Century Gothic", 25, "bold"), command=browse)
    browseButton.place(x=275,y=280)
    
    main_window.mainloop()  

main()
