import tkinter as tk

def custom_prompt(parent):
    # Create a modal top-level window
    top = tk.Toplevel(parent)
    top.title("Elige una opción")
    top.grab_set()  # Makes the prompt modal (blocks main window)

    result = {"value": None}

    tk.Label(top, text="¿Qué querés hacer?").pack(padx=20, pady=10)

    def choose(option):
        result["value"] = option
        top.destroy()

    # Buttons with custom return values
    tk.Button(top, text="Opción A", command=lambda: choose("A")).pack(side="left", padx=10, pady=10)
    tk.Button(top, text="Opción B", command=lambda: choose("B")).pack(side="left", padx=10, pady=10)
    tk.Button(top, text="Cancelar", command=top.destroy).pack(side="left", padx=10, pady=10)

    top.wait_window()  # Waits until this window is closed
    return result["value"]

root = tk.Tk()
root.withdraw()  # Hide main window just for this demo

res = custom_prompt(root)
print("Elegiste:", res)

root.destroy()