import tkinter as tk
import time


def convert_to_minutes_seconds(big_time, small_time):
    total_seconds = (big_time - small_time) / 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{int(minutes) if minutes.is_integer() else minutes}m:{round(seconds, 2)}s"


def current_milli_time():
    return round(time.time() * 1000)


racetimer_string = ""
lap1_time_string = ""
lap2_time_string = ""
lap3_time_string = ""
start_webhook = -1
lap1_webhook = -1
lap2_webhook = -1
lap3_webhook = -1


def update_labels(self):
    convert_string(start_webhook, lap1_webhook, lap2_webhook, lap3_webhook)
    self.label_texts[0].set(racetimer_string)
    self.label_texts[1].set(lap1_time_string)
    self.label_texts[2].set(lap2_time_string)
    self.label_texts[3].set(lap3_time_string)


class MyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Webhook Update Example")

        self.label_texts = [tk.StringVar() for _ in range(4)]
        for i in range(4):
            self.label_texts[i].set(f"nothing received {i + 1}")

        root.title('Overlay')
        self.root.geometry("220x150+{}+{}".format(root.winfo_screenwidth() - 220, 0))
        root.wm_attributes('-alpha', 0.8, '-topmost', 1)
        root.configure(background='black')
        root.overrideredirect(True)
        self.update_labels_periodically()
        self.labels = []
        for i in range(4):
            label = tk.Label(root, textvariable=self.label_texts[i], font=('Helvetica', 12), background='black',
                             foreground='white', highlightthickness=0, anchor='nw')
            label.pack(pady=0, padx=2, anchor='nw')
            self.labels.append(label)

        self.start_webhook_server()

    def update_labels_periodically(self):
        update_labels(self)
        self.root.after(10, self.update_labels_periodically)  # Update every 1000 milliseconds (1 second)

    def start_webhook_server(self):
        from flask import Flask, request, jsonify
        import threading

        app = Flask(__name__)

        @app.route('/webhook', methods=['POST'])
        def webhook():
            global start_webhook, lap1_webhook, lap2_webhook, lap3_webhook
            data = request.get_json()

            # Update the label text with the received data
            start_webhook = data.get("start", "-1")
            lap1_webhook = data.get("lap1", "-1")
            lap2_webhook = data.get("lap2", "-1")
            lap3_webhook = data.get("lap3", "-1")
            convert_string(start_webhook, lap1_webhook, lap2_webhook, lap3_webhook)
            self.label_texts[0].set(racetimer_string)
            self.label_texts[1].set(lap1_time_string)
            self.label_texts[2].set(lap2_time_string)
            self.label_texts[3].set(lap3_time_string)

            return jsonify({"status": "success"})

        def run_flask_app():
            app.run(port=6942)

        # Start Flask app in a separate thread
        webhook_thread = threading.Thread(target=run_flask_app)
        webhook_thread.start()


def convert_string(start_time, lap1, lap2, lap3):
    global racetimer_string, lap1_time_string, lap2_time_string, lap3_time_string
    if int(lap3) == -1 and int(start_time) != -1:
        racetimer_string = f"Total: {convert_to_minutes_seconds(current_milli_time(), int(start_time))}"
    elif int(start_time) != -1:
        racetimer_string = f"Total: {convert_to_minutes_seconds(int(lap3), int(start_time))}"
    else:
        racetimer_string = "Total: 0m:0.0s"

    if lap1 != -1:
        lap1_time_string = f"Lap 1: {convert_to_minutes_seconds(int(lap1), int(start_time))}"
    elif start_time != -1:
        lap1_time_string = f"Lap 1: {convert_to_minutes_seconds(current_milli_time(), int(start_time))}"
    else:
        lap1_time_string = f"Lap 1: 0m:0.0s"

   #print(f"s{start_time} l1 {lap1} l2 {lap2} l3 {lap3}")
    if lap2 != -1:
        lap2_time_string = f"Lap 2: {convert_to_minutes_seconds(int(lap2), int(lap1))}"
    elif lap1 != -1:
        lap2_time_string = f"Lap 2: {convert_to_minutes_seconds(current_milli_time(), int(lap1))}"
    else:
        lap2_time_string = f"Lap 2: 0m:0.0s"
    if lap3 != -1:
        lap3_time_string = f"Lap 3: {convert_to_minutes_seconds(int(lap3), int(lap2))}"
    elif lap2 != -1:
        lap3_time_string = f"Lap 3: {convert_to_minutes_seconds(current_milli_time(), int(lap2))}"
    else:
        lap3_time_string = f"Lap 3: 0m:0.0s"


def main_running():
    root = tk.Tk()
    gui = MyGUI(root)
    root.mainloop()
