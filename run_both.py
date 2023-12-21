from threading import Thread
import overlay

class This(Thread):
    def run(self):
        import main

class That(Thread):
    def run(self):
        overlay.main_running()


if __name__ == "__main__":
    e = This().start()
    i = That().start()
