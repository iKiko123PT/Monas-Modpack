import os
import requests
import shutil
import json
import subprocess
from tkinter import (
    Tk, Button, Label, Scrollbar, Listbox, messagebox,
    VERTICAL, RIGHT, Y, BOTH, END, filedialog
)

# --- CONFIG ---
GITHUB_USER = "iKiko123PT"
GITHUB_REPO = "Mods-das-Monas"
MODS_FOLDER = "mods"
MODS_JSON_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/mods.json"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{MODS_FOLDER}"

# --- Load optional mods.json for metadata ---
def load_mod_metadata():
    try:
        res = requests.get(MODS_JSON_URL)
        return {mod["name"]: mod for mod in res.json()}
    except:
        return {}

# --- Get mod list from GitHub API ---
def fetch_mod_files():
    res = requests.get(GITHUB_API_URL)
    files = res.json()
    return [
        {
            "name": f["name"],
            "url": f["download_url"]
        }
        for f in files if f["name"].endswith((".jar", ".zip"))
    ]

# --- Download file ---
def download_file(url, dest):
    r = requests.get(url, stream=True)
    with open(dest, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

# --- GUI ---
class ModInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Instalador dos Mods das Monas")
        self.root.geometry("600x550")

        Label(root, text="Seleciona os mods que queres instalar. Os já instalados são marcados:", font=("Arial", 11)).pack(pady=10)

        self.scrollbar = Scrollbar(root, orient=VERTICAL)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.list_frame = Listbox(root, selectmode="multiple", yscrollcommand=self.scrollbar.set, width=80, height=20)
        self.list_frame.pack(padx=10, fill=BOTH, expand=True)

        self.scrollbar.config(command=self.list_frame.yview)

        self.mods = []
        self.load_mods()

        Button(root, text="Instalar selecionados", command=self.install_mods).pack(pady=5)
        Button(root, text="Reinstalar todos", command=self.reinstall_all).pack(pady=5)
        Button(root, text="Ver mods instalados", command=self.show_installed_mods).pack(pady=5)
        Button(root, text="Desinstalar selecionados", command=self.uninstall_selected).pack(pady=5)
        Button(root, text="Abrir pasta dos mods", command=self.open_mods_folder).pack(pady=5)

    def load_mods(self):
        mod_metadata = load_mod_metadata()
        mod_files = fetch_mod_files()

        self.mc_mods_dir = os.path.join(os.getenv("APPDATA"), ".minecraft", "mods")
        os.makedirs(self.mc_mods_dir, exist_ok=True)
        existing_mods = set(os.listdir(self.mc_mods_dir))

        self.mods = []
        self.list_frame.delete(0, END)

        for mod in mod_files:
            name = mod["name"]
            url = mod["url"]

            is_installed = name in existing_mods

            label = mod_metadata.get(name, {}).get("name", name)
            desc = mod_metadata.get(name, {}).get("description", "")
            display = f"{label} - {desc}" if desc else label
            if is_installed:
                display += " [INSTALADO]"

            self.mods.append((name, url))
            self.list_frame.insert(END, display)

            if not is_installed:
                self.list_frame.select_set(END)

    def install_mods(self):
        selected_indices = self.list_frame.curselection()
        if not selected_indices:
            messagebox.showinfo("Atenção", "Tens de selecionar algum Mod")
            return

        for i in selected_indices:
            name, url = self.mods[i]
            dest_path = os.path.join(self.mc_mods_dir, name)
            try:
                download_file(url, dest_path)
            except Exception as e:
                messagebox.showerror("Erro", f"Não consegui obter {name}:\n{str(e)}")

        messagebox.showinfo("Sucesso", "Mods instalados com sucesso.")
        self.load_mods()

    def reinstall_all(self):
        for name, url in self.mods:
            dest_path = os.path.join(self.mc_mods_dir, name)
            try:
                download_file(url, dest_path)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro a reinstalar {name}:\n{str(e)}")

        messagebox.showinfo("Reinstalação completa", "Todos os mods foram reinstalados.")
        self.load_mods()

    def uninstall_selected(self):
        selected_indices = self.list_frame.curselection()
        if not selected_indices:
            messagebox.showinfo("Atenção", "Seleciona mods para desinstalar.")
            return

        for i in selected_indices:
            name, _ = self.mods[i]
            path = os.path.join(self.mc_mods_dir, name)
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    messagebox.showerror("Erro", f"Não consegui apagar {name}:\n{str(e)}")

        messagebox.showinfo("Mods apagados", "Mods selecionados foram desinstalados.")
        self.load_mods()

    def show_installed_mods(self):
        mods = os.listdir(self.mc_mods_dir)
        if not mods:
            messagebox.showinfo("Mods instalados", "Não há mods instalados.")
        else:
            installed = "\n".join(mods)
            messagebox.showinfo("Mods instalados", f"Estes mods estão instalados:\n\n{installed}")

    def open_mods_folder(self):
        subprocess.Popen(f'explorer "{self.mc_mods_dir}"')

# --- Main ---
if __name__ == "__main__":
    root = Tk()
    app = ModInstaller(root)
    root.mainloop()
