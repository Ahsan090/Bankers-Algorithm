import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from Process import process
from System import system


class BankersApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Banker's Algorithm Simulator")
        self.root.geometry("980x640")
        self.root.resizable(True, True)

        self.system = None
        self.current_frame = None
        self.n_proc = 0
        self.n_res = 0
        self.pid_list = []
        self._req_count = 0

        # Widget refs for Screen 2
        self.avail_entries = []
        self.max_entries = []
        self.alloc_entries = []

        # Widget refs for Screen 3
        self.tree = None
        self.status_label = None
        self.seq_label = None
        self.avail_label = None
        self.log_text = None
        self.pid_var = None
        self.req_entries = []

        self._setup_styles()
        self.show_setup_screen()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"), foreground="#2c3e50")
        style.configure("Header.TLabel", font=("Helvetica", 11, "bold"), foreground="#34495e")
        style.configure("Safe.TLabel", font=("Helvetica", 11, "bold"),
                        foreground="white", background="#27ae60", padding=(10, 4))
        style.configure("Unsafe.TLabel", font=("Helvetica", 11, "bold"),
                        foreground="white", background="#e74c3c", padding=(10, 4))
        style.configure("Info.TLabel", font=("Helvetica", 10), foreground="#555555")
        style.configure("Primary.TButton", font=("Helvetica", 10, "bold"), padding=(12, 6))
        style.configure("Secondary.TButton", font=("Helvetica", 10), padding=(8, 5))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Treeview", font=("Helvetica", 10), rowheight=26)

    # ── Utilities ────────────────────────────────────────────────────────────

    def _clear_screen(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def _fmt_vec(self, v):
        return "  ".join(map(str, v))

    def _log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ── Screen 1: Setup ──────────────────────────────────────────────────────

    def show_setup_screen(self):
        self._clear_screen()
        frame = ttk.Frame(self.root, padding=40)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Banker's Algorithm Simulator", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 30))

        ttk.Label(frame, text="Number of Processes:", style="Header.TLabel").grid(
            row=1, column=0, sticky="e", padx=(0, 12), pady=10)
        self.np_entry = ttk.Entry(frame, width=10, font=("Helvetica", 11))
        self.np_entry.grid(row=1, column=1, sticky="w", pady=10)
        self.np_entry.insert(0, "3")

        ttk.Label(frame, text="Number of Resource Types:", style="Header.TLabel").grid(
            row=2, column=0, sticky="e", padx=(0, 12), pady=10)
        self.nr_entry = ttk.Entry(frame, width=10, font=("Helvetica", 11))
        self.nr_entry.grid(row=2, column=1, sticky="w", pady=10)
        self.nr_entry.insert(0, "3")

        ttk.Button(frame, text="Configure System →", style="Primary.TButton",
                   command=self._on_setup_confirm).grid(
            row=3, column=0, columnspan=2, pady=30)

        self.np_entry.bind("<Return>", lambda _: self._on_setup_confirm())
        self.nr_entry.bind("<Return>", lambda _: self._on_setup_confirm())
        self.np_entry.focus_set()

    def _on_setup_confirm(self):
        try:
            n_proc = int(self.np_entry.get())
            n_res = int(self.nr_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter whole numbers for both fields.")
            return
        if n_proc < 1 or n_res < 1:
            messagebox.showerror("Invalid Input", "Values must be at least 1.")
            return
        if n_proc > 20 or n_res > 20:
            messagebox.showerror("Invalid Input", "Maximum allowed value is 20.")
            return
        self.show_data_entry_screen(n_proc, n_res)

    # ── Screen 2: Data Entry ─────────────────────────────────────────────────

    def show_data_entry_screen(self, n_proc, n_res):
        self._clear_screen()
        self.n_proc = n_proc
        self.n_res = n_res
        self.avail_entries = []
        self.max_entries = []
        self.alloc_entries = []

        outer = ttk.Frame(self.root)
        outer.pack(fill="both", expand=True)
        self.current_frame = outer

        canvas = tk.Canvas(outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = ttk.Frame(canvas, padding=20)
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(_):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        ttk.Label(inner, text="Step 2: Enter System Data", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # Available Resources
        avail_frame = ttk.LabelFrame(inner, text="Available Resources", padding=12)
        avail_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=8)
        for j in range(n_res):
            ttk.Label(avail_frame, text=f"R{j}", style="Header.TLabel").grid(
                row=0, column=j * 2, padx=(8, 2))
            e = ttk.Entry(avail_frame, width=5, font=("Helvetica", 10))
            e.grid(row=0, column=j * 2 + 1, padx=(0, 12))
            e.insert(0, "0")
            self.avail_entries.append(e)

        # Max Matrix
        max_frame = ttk.LabelFrame(inner, text="Maximum Demand Matrix", padding=12)
        max_frame.grid(row=2, column=0, sticky="ew", padx=(0, 10), pady=8)
        self._build_matrix(max_frame, n_proc, n_res, self.max_entries)

        # Allocation Matrix
        alloc_frame = ttk.LabelFrame(inner, text="Current Allocation Matrix", padding=12)
        alloc_frame.grid(row=2, column=1, sticky="ew", pady=8)
        self._build_matrix(alloc_frame, n_proc, n_res, self.alloc_entries)

        # Buttons
        btn_frame = ttk.Frame(inner)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")
        ttk.Button(btn_frame, text="← Back", style="Secondary.TButton",
                   command=self.show_setup_screen).pack(side="left")
        ttk.Button(btn_frame, text="Initialize System →", style="Primary.TButton",
                   command=self._on_data_confirm).pack(side="right")

    def _build_matrix(self, parent, n_proc, n_res, store):
        # Column headers
        for j in range(n_res):
            ttk.Label(parent, text=f"R{j}", style="Header.TLabel").grid(
                row=0, column=j + 1, padx=6)
        # Rows
        for i in range(n_proc):
            ttk.Label(parent, text=f"P{i}", style="Header.TLabel").grid(
                row=i + 1, column=0, padx=(0, 8), sticky="e")
            row_entries = []
            for j in range(n_res):
                e = ttk.Entry(parent, width=4, font=("Helvetica", 10))
                e.grid(row=i + 1, column=j + 1, padx=4, pady=3)
                e.insert(0, "0")
                row_entries.append(e)
            store.append(row_entries)

    def _on_data_confirm(self):
        # Parse available
        available = []
        for j, e in enumerate(self.avail_entries):
            try:
                val = int(e.get())
            except ValueError:
                messagebox.showerror("Invalid Input", f"Available R{j} must be an integer.")
                return
            if val < 0:
                messagebox.showerror("Invalid Input", f"Available R{j} cannot be negative.")
                return
            available.append(val)

        # Parse max and allocation
        processes = []
        for i in range(self.n_proc):
            pmax = []
            alloc = []
            for j in range(self.n_res):
                try:
                    m = int(self.max_entries[i][j].get())
                except ValueError:
                    messagebox.showerror("Invalid Input",
                                         f"Max for P{i} R{j} must be an integer.")
                    return
                try:
                    a = int(self.alloc_entries[i][j].get())
                except ValueError:
                    messagebox.showerror("Invalid Input",
                                         f"Allocation for P{i} R{j} must be an integer.")
                    return
                if m < 0 or a < 0:
                    messagebox.showerror("Invalid Input",
                                         f"P{i} R{j}: values cannot be negative.")
                    return
                if a > m:
                    messagebox.showerror("Invalid Input",
                                         f"P{i} R{j}: allocation ({a}) exceeds maximum demand ({m}).")
                    return
                pmax.append(m)
                alloc.append(a)
            processes.append(process(f"P{i}", pmax, alloc))

        self.pid_list = [f"P{i}" for i in range(self.n_proc)]
        self.system = system(available, processes)
        self._req_count = 0
        self.show_main_screen()

    # ── Screen 3: Main Simulator ─────────────────────────────────────────────

    def show_main_screen(self):
        self._clear_screen()
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        # ── Top bar ──────────────────────────────────────────────────────────
        top = ttk.Frame(frame)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Banker's Algorithm Simulator", style="Title.TLabel").pack(side="left")
        self.status_label = ttk.Label(top, text="", style="Safe.TLabel")
        self.status_label.pack(side="right", padx=(10, 0))

        self.avail_label = ttk.Label(frame, text="", style="Info.TLabel")
        self.avail_label.pack(anchor="w")
        self.seq_label = ttk.Label(frame, text="", style="Info.TLabel")
        self.seq_label.pack(anchor="w", pady=(0, 8))

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=4)

        # ── Middle: table + right panel ───────────────────────────────────────
        mid = ttk.Frame(frame)
        mid.pack(fill="both", expand=True, pady=6)

        # Left: treeview
        left = ttk.Frame(mid)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("pid", "allocation", "max", "need")
        self.tree = ttk.Treeview(left, columns=cols, show="headings",
                                  height=self.n_proc)
        self.tree.heading("pid", text="PID")
        self.tree.heading("allocation", text="Allocation")
        self.tree.heading("max", text="Max Demand")
        self.tree.heading("need", text="Need")
        self.tree.column("pid", width=55, anchor="center", stretch=False)
        self.tree.column("allocation", width=160, anchor="center", minwidth=80, stretch=True)
        self.tree.column("max", width=160, anchor="center", minwidth=80, stretch=True)
        self.tree.column("need", width=160, anchor="center", minwidth=80, stretch=True)
        self.tree.tag_configure("normal_row", background="#ffffff")
        self.tree.tag_configure("alt_row", background="#f4f6f9")

        vsb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Right: request form + log
        right = ttk.Frame(mid, width=310)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        req_frame = ttk.LabelFrame(right, text="Submit a Resource Request", padding=10)
        req_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(req_frame, text="Process:", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", pady=4)
        self.pid_var = tk.StringVar(value=self.pid_list[0])
        pid_combo = ttk.Combobox(req_frame, textvariable=self.pid_var,
                                  values=self.pid_list, state="readonly", width=8)
        pid_combo.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=4)

        ttk.Label(req_frame, text="Request:", style="Header.TLabel").grid(
            row=1, column=0, sticky="w", pady=4)
        req_inner = ttk.Frame(req_frame)
        req_inner.grid(row=1, column=1, sticky="w", padx=(6, 0), pady=4)
        self.req_entries = []
        for j in range(self.n_res):
            ttk.Label(req_inner, text=f"R{j}").pack(side="left")
            e = ttk.Entry(req_inner, width=4, font=("Helvetica", 10))
            e.insert(0, "0")
            e.pack(side="left", padx=(2, 8))
            self.req_entries.append(e)

        ttk.Button(req_frame, text="Submit Request", style="Primary.TButton",
                   command=self._submit_request).grid(
            row=2, column=0, columnspan=2, pady=(10, 4), sticky="ew")

        log_frame = ttk.LabelFrame(right, text="Request Log", padding=8)
        log_frame.pack(fill="both", expand=True)
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=10, state="disabled",
            font=("Courier", 9), wrap="word",
            bg="#f8f9fa", relief="flat")
        self.log_text.pack(fill="both", expand=True)

        # ── Bottom bar ────────────────────────────────────────────────────────
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=6)
        ttk.Button(frame, text="Reset (Start Over)", style="Secondary.TButton",
                   command=self.show_setup_screen).pack(anchor="w")

        self._refresh_main_screen()

    def _refresh_main_screen(self):
        # Repopulate treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, p in enumerate(self.system.processes):
            tag = "alt_row" if idx % 2 else "normal_row"
            self.tree.insert("", "end", values=(
                p.pid,
                self._fmt_vec(p.allocation),
                self._fmt_vec(p.pmax),
                self._fmt_vec(p.need)
            ), tags=(tag,))

        # Safety status
        seq = self.system.get_safe_sequence()
        if seq is not None:
            self.status_label.config(text="  SAFE STATE  ", style="Safe.TLabel")
            self.seq_label.config(
                text="Safe Sequence:  " + "  →  ".join(seq))
        else:
            self.status_label.config(text="  UNSAFE STATE  ", style="Unsafe.TLabel")
            self.seq_label.config(text="Safe Sequence:  N/A  (deadlock risk)")

        self.avail_label.config(
            text="Available Resources:  " + self._fmt_vec(self.system.available))

    def _submit_request(self):
        pid = self.pid_var.get()
        req = []
        for j, e in enumerate(self.req_entries):
            try:
                val = int(e.get())
            except ValueError:
                messagebox.showerror("Invalid Input", f"R{j} must be an integer.")
                return
            if val < 0:
                messagebox.showerror("Invalid Input", f"R{j} cannot be negative.")
                return
            req.append(val)

        self._req_count += 1
        result = self.system.request(pid, req)
        req_str = "[" + ", ".join(map(str, req)) + "]"
        if result:
            self._log(f"#{self._req_count}  {pid} requested {req_str}"
                      f"\n    → GRANTED  (safe state maintained)\n")
        else:
            self._log(f"#{self._req_count}  {pid} requested {req_str}"
                      f"\n    → DENIED   (unsafe or exceeds need / available)\n")
        self._refresh_main_screen()

        # Reset request entries to 0
        for e in self.req_entries:
            e.delete(0, "end")
            e.insert(0, "0")


if __name__ == "__main__":
    app = BankersApp()
    app.root.mainloop()
