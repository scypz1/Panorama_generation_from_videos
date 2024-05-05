import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import cv2
import video_processor


def update_status(message):
    status_label.config(text=message)
    root.update_idletasks()  # Update the UI


def save_image(image):
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
    if file_path:
        cv2.imwrite(file_path, image)
        messagebox.showinfo("Save Successful", "Panorama saved successfully!")


def resize_image(image, max_width, max_height):
    width_ratio = max_width / image.width
    height_ratio = max_height / image.height
    scaling_factor = min(width_ratio, height_ratio)
    new_width = int(image.width * scaling_factor)
    new_height = int(image.height * scaling_factor)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    return resized_image


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def display_panorama(image):
    clear_frame(display_frame)
    display_frame.pack(fill=tk.BOTH, expand=True)
    display_frame.update()
    max_width = display_frame.winfo_width()
    max_height = display_frame.winfo_height() - 50
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    resized_pil_image = resize_image(pil_image, max_width, max_height)
    tk_image = ImageTk.PhotoImage(resized_pil_image)
    image_label = tk.Label(display_frame, image=tk_image)
    image_label.image = tk_image
    image_label.pack()
    save_button = tk.Button(display_frame, text="Save Panorama", command=lambda: save_image(image))
    save_button.pack()


def create_panorama_from_video(video_path, update_status):
    frames = video_processor.dynamic_key_frames_extraction(video_path, update_status)
    panorama = video_processor.stitch_frames(frames, update_status)
    image = video_processor.drop_black_edges(panorama)
    if image is not None:
        update_status("Panorama created successfully. Ready to save.")
        return image
    else:
        update_status("Failed to create panorama.")
        return None


def thread_create_panorama(video_path):
    image = create_panorama_from_video(video_path, update_status)
    if image is not None:
        root.after(10, lambda: display_panorama(image))


def start_panorama_creation():
    video_path = entry.get()
    if video_path:
        threading.Thread(target=thread_create_panorama, args=(video_path,)).start()
    else:
        messagebox.showerror("Error", "Please select a video file first!")


def browse_video():
    filename = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Panorama Creator")
    root.geometry('800x600')
    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20)
    entry = tk.Entry(frame, width=50)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    browse_button = tk.Button(frame, text="Browse", command=browse_video)
    browse_button.pack(side=tk.LEFT, padx=10)
    start_button = tk.Button(frame, text="Create Panorama", command=start_panorama_creation)
    start_button.pack(side=tk.LEFT)
    status_label = tk.Label(root, text="", relief=tk.SUNKEN, anchor="w")
    status_label.pack(fill=tk.X, padx=20, pady=10)
    display_frame = tk.Frame(root)
    root.mainloop()



