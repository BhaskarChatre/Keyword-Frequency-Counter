"""
Keyword Frequency Counter using a Hash Table (Separate Chaining)
================================================================
Run the GUI :  python keyword_frequency_counter.py
Run console :  python keyword_frequency_counter.py --demo

The hash table is implemented from scratch (Python's built-in dict is NOT
used for counting).  Collisions are resolved by separate chaining and the
table is dynamically resized (rehashed) when the load factor exceeds 0.75.
"""

import re
import sys
import csv

# --------------------------------------------------------------------------
#  PART 1 : HASH TABLE (core data structure)
# --------------------------------------------------------------------------

class Node:
    """One entry of a bucket's chain: (key, count) + pointer to next node."""
    __slots__ = ("key", "count", "next")

    def __init__(self, key, count=1, nxt=None):
        self.key = key
        self.count = count
        self.next = nxt


class HashTable:
    """Hash table that maps keyword -> frequency using separate chaining."""

    MAX_LOAD = 0.75

    def __init__(self, size=8):
        self.size = size                  # number of buckets
        self.buckets = [None] * size      # each bucket = head of linked list
        self.n = 0                        # number of unique keys stored
        # statistics (used for step count / GUI display)
        self.collisions = 0
        self.comparisons = 0
        self.resizes = 0

    # ---- hash function (polynomial rolling hash, base 31) ----------------
    @staticmethod
    def hash_code(key):
        h = 0
        for ch in key:
            h = (h * 31 + ord(ch)) & 0xFFFFFFFF   # keep it 32-bit
        return h

    def index_of(self, key):
        return self.hash_code(key) % self.size

    # ---- insert / update -------------------------------------------------
    def increment(self, key):
        """Add 1 to key's frequency (insert with count 1 if absent)."""
        idx = self.index_of(key)
        cur = self.buckets[idx]
        while cur is not None:
            self.comparisons += 1
            if cur.key == key:            # keyword already present
                cur.count += 1
                return
            cur = cur.next
        # keyword not found -> insert at head of chain
        if self.buckets[idx] is not None:
            self.collisions += 1
        self.buckets[idx] = Node(key, 1, self.buckets[idx])
        self.n += 1
        if self.load_factor() > self.MAX_LOAD:
            self._resize()

    # ---- search ----------------------------------------------------------
    def get(self, key):
        """Return frequency of key (0 if absent)."""
        cur = self.buckets[self.index_of(key)]
        while cur is not None:
            self.comparisons += 1
            if cur.key == key:
                return cur.count
            cur = cur.next
        return 0

    # ---- delete ----------------------------------------------------------
    def delete(self, key):
        idx = self.index_of(key)
        cur, prev = self.buckets[idx], None
        while cur is not None:
            if cur.key == key:
                if prev is None:
                    self.buckets[idx] = cur.next
                else:
                    prev.next = cur.next
                self.n -= 1
                return True
            prev, cur = cur, cur.next
        return False

    # ---- resize / rehash -------------------------------------------------
    def _resize(self):
        old = self.buckets
        self.size *= 2
        self.buckets = [None] * self.size
        self.resizes += 1
        for head in old:
            cur = head
            while cur is not None:
                nxt = cur.next
                idx = self.index_of(cur.key)
                cur.next = self.buckets[idx]
                self.buckets[idx] = cur
                cur = nxt

    # ---- helpers ---------------------------------------------------------
    def load_factor(self):
        return self.n / self.size

    def items(self):
        """Yield (key, count, bucket_index) for every stored keyword."""
        for i, head in enumerate(self.buckets):
            cur = head
            while cur is not None:
                yield cur.key, cur.count, i
                cur = cur.next

    def longest_chain(self):
        best = 0
        for head in self.buckets:
            length, cur = 0, head
            while cur is not None:
                length += 1
                cur = cur.next
            best = max(best, length)
        return best


# --------------------------------------------------------------------------
#  PART 2 : TEXT PROCESSING
# --------------------------------------------------------------------------

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "am", "i",
    "and", "or", "but", "if", "of", "to", "in", "on", "at", "by", "for",
    "with", "as", "it", "its", "this", "that", "these", "those", "from",
    "he", "she", "they", "we", "you", "his", "her", "their", "our", "your",
    "not", "no", "so", "do", "does", "did", "has", "have", "had", "will",
    "can", "than", "then", "there", "which", "who", "what", "into", "also",
}

SAMPLE_TEXT = (
    "Data structures are the foundation of computer science. A hash table is "
    "a data structure that stores data in key value pairs. The hash function "
    "converts the key into an index, so a hash table can search, insert and "
    "delete data in constant time. When two keys map to the same index a "
    "collision occurs, and a good hash table resolves the collision using "
    "chaining or open addressing. Keyword counting is a classic use of a hash "
    "table: every keyword is hashed, and the hash table keeps the frequency "
    "of each keyword."
)


def tokenize(text, ignore_case=True, remove_stop=True):
    words = re.findall(r"[A-Za-z0-9']+", text)
    if ignore_case:
        words = [w.lower() for w in words]
    if remove_stop:
        words = [w for w in words if w.lower() not in STOP_WORDS]
    return words


def count_keywords(text, ignore_case=True, remove_stop=True, init_size=8):
    """Build a HashTable of keyword frequencies. Returns (table, total_words)."""
    table = HashTable(init_size)
    words = tokenize(text, ignore_case, remove_stop)
    for w in words:
        table.increment(w)
    return table, len(words)


def sorted_results(table):
    """List of (keyword, frequency, bucket) sorted by frequency desc, then A-Z."""
    return sorted(table.items(), key=lambda t: (-t[1], t[0]))


# --------------------------------------------------------------------------
#  PART 3 : CONSOLE DEMO
# --------------------------------------------------------------------------

def run_demo():
    table, total = count_keywords(SAMPLE_TEXT)
    print("=" * 56)
    print(" KEYWORD FREQUENCY COUNTER  (Hash Table - Chaining)")
    print("=" * 56)
    print(f"Total keywords processed : {total}")
    print(f"Unique keywords          : {table.n}")
    print(f"Table size (buckets)     : {table.size}")
    print(f"Load factor              : {table.load_factor():.2f}")
    print(f"Collisions               : {table.collisions}")
    print(f"Longest chain            : {table.longest_chain()}")
    print(f"Resizes (rehash)         : {table.resizes}")
    print(f"Key comparisons          : {table.comparisons}")
    print("-" * 56)
    print(f"{'Rank':<6}{'Keyword':<18}{'Frequency':<12}{'Bucket'}")
    print("-" * 56)
    for rank, (k, c, b) in enumerate(sorted_results(table)[:10], 1):
        print(f"{rank:<6}{k:<18}{c:<12}{b}")
    print("-" * 56)
    for q in ("hash", "table", "python"):
        print(f"Search '{q}' -> frequency = {table.get(q)}")


# --------------------------------------------------------------------------
#  PART 4 : GUI (Tkinter)
# --------------------------------------------------------------------------

def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext

    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Keyword Frequency Counter - Hash Table")
            self.geometry("1020x640")
            self.minsize(900, 560)
            self.table = None
            self.configure(bg="#f3f4f6")
            self._build_style()
            self._build_ui()

        # ---------------- styling ----------------
        def _build_style(self):
            s = ttk.Style(self)
            try:
                s.theme_use("clam")
            except tk.TclError:
                pass
            s.configure("Header.TLabel", font=("Segoe UI", 16, "bold"),
                        background="#1e3a8a", foreground="white", padding=10)
            s.configure("TLabelframe", background="#f3f4f6")
            s.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"),
                        background="#f3f4f6", foreground="#1e3a8a")
            s.configure("TFrame", background="#f3f4f6")
            s.configure("TLabel", background="#f3f4f6", font=("Segoe UI", 10))
            s.configure("TCheckbutton", background="#f3f4f6",
                        font=("Segoe UI", 10))
            s.configure("Accent.TButton", font=("Segoe UI", 10, "bold"),
                        background="#2563eb", foreground="white")
            s.map("Accent.TButton", background=[("active", "#1d4ed8")])
            s.configure("Treeview", rowheight=24, font=("Segoe UI", 10))
            s.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        # ---------------- layout ----------------
        def _build_ui(self):
            ttk.Label(self, text="  Keyword Frequency Counter  "
                      "|  Hash Table (Separate Chaining)",
                      style="Header.TLabel", anchor="w").pack(fill="x")

            body = ttk.Frame(self, padding=10)
            body.pack(fill="both", expand=True)
            body.columnconfigure(0, weight=1)
            body.columnconfigure(1, weight=1)
            body.rowconfigure(0, weight=1)

            # ---- LEFT : input ----
            left = ttk.LabelFrame(body, text="1. Input Text", padding=8)
            left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
            left.rowconfigure(0, weight=1)
            left.columnconfigure(0, weight=1)

            self.txt = scrolledtext.ScrolledText(left, wrap="word",
                                                 font=("Consolas", 10), height=14)
            self.txt.grid(row=0, column=0, columnspan=4, sticky="nsew")

            ttk.Button(left, text="Open File...", command=self.open_file)\
                .grid(row=1, column=0, pady=(8, 0), sticky="w")
            ttk.Button(left, text="Load Sample", command=self.load_sample)\
                .grid(row=1, column=1, pady=(8, 0), sticky="w", padx=4)
            ttk.Button(left, text="Clear", command=self.clear_all)\
                .grid(row=1, column=2, pady=(8, 0), sticky="w")

            opt = ttk.LabelFrame(left, text="Options", padding=6)
            opt.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(10, 0))
            self.var_case = tk.BooleanVar(value=True)
            self.var_stop = tk.BooleanVar(value=True)
            ttk.Checkbutton(opt, text="Ignore case",
                            variable=self.var_case).grid(row=0, column=0, padx=4)
            ttk.Checkbutton(opt, text="Remove stop-words",
                            variable=self.var_stop).grid(row=0, column=1, padx=4)
            ttk.Label(opt, text="Show top:").grid(row=0, column=2, padx=(12, 2))
            self.var_top = tk.IntVar(value=15)
            ttk.Spinbox(opt, from_=1, to=500, width=5,
                        textvariable=self.var_top).grid(row=0, column=3)

            ttk.Button(left, text="COUNT KEYWORDS", style="Accent.TButton",
                       command=self.analyze)\
                .grid(row=3, column=0, columnspan=4, sticky="ew", pady=(10, 0))

            # ---- RIGHT : results ----
            right = ttk.LabelFrame(body, text="2. Results", padding=8)
            right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
            right.rowconfigure(1, weight=1)
            right.columnconfigure(0, weight=1)

            sf = ttk.Frame(right)
            sf.grid(row=0, column=0, sticky="ew", pady=(0, 6))
            ttk.Label(sf, text="Search keyword:").pack(side="left")
            self.var_search = tk.StringVar()
            e = ttk.Entry(sf, textvariable=self.var_search, width=18)
            e.pack(side="left", padx=4)
            e.bind("<Return>", lambda _e: self.search())
            ttk.Button(sf, text="Search", command=self.search).pack(side="left")
            ttk.Button(sf, text="Delete", command=self.delete).pack(side="left", padx=4)
            ttk.Button(sf, text="Export CSV", command=self.export_csv)\
                .pack(side="right")

            nb = ttk.Notebook(right)
            nb.grid(row=1, column=0, sticky="nsew")

            f1 = ttk.Frame(nb)
            nb.add(f1, text="Frequency Table")
            cols = ("rank", "keyword", "freq", "bucket")
            self.tree = ttk.Treeview(f1, columns=cols, show="headings", height=12)
            for c, t, w in (("rank", "Rank", 50), ("keyword", "Keyword", 150),
                            ("freq", "Frequency", 90), ("bucket", "Bucket #", 80)):
                self.tree.heading(c, text=t)
                self.tree.column(c, width=w, anchor="center")
            sb = ttk.Scrollbar(f1, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=sb.set)
            self.tree.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")
            self.tree.tag_configure("odd", background="#e8eefc")
            self.tree.tag_configure("hit", background="#fde68a")

            f2 = ttk.Frame(nb)
            nb.add(f2, text="Hash Table Buckets")
            self.bucket_txt = scrolledtext.ScrolledText(
                f2, font=("Consolas", 10), state="disabled", height=12)
            self.bucket_txt.pack(fill="both", expand=True)

            # ---- stats ----
            st = ttk.LabelFrame(right, text="Hash Table Statistics", padding=6)
            st.grid(row=2, column=0, sticky="ew", pady=(8, 0))
            self.stat_vars = {}
            labels = ["Total words", "Unique keywords", "Table size",
                      "Load factor", "Collisions", "Longest chain"]
            for i, name in enumerate(labels):
                v = tk.StringVar(value="-")
                self.stat_vars[name] = v
                r, c = divmod(i, 3)
                ttk.Label(st, text=name + ":").grid(row=r, column=c * 2,
                                                    sticky="e", padx=(6, 2))
                ttk.Label(st, textvariable=v, font=("Segoe UI", 10, "bold"),
                          foreground="#1e3a8a").grid(row=r, column=c * 2 + 1,
                                                     sticky="w", padx=(0, 10))

            self.status = tk.StringVar(value="Ready. Enter text or open a file.")
            tk.Label(self, textvariable=self.status, anchor="w", bg="#d1d5db",
                     font=("Segoe UI", 9), padx=8).pack(fill="x", side="bottom")

        # ---------------- actions ----------------
        def open_file(self):
            path = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt *.py *.c *.java *.md"),
                           ("All files", "*.*")])
            if path:
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        self.txt.delete("1.0", "end")
                        self.txt.insert("1.0", f.read())
                    self.status.set(f"Loaded: {path}")
                except OSError as ex:
                    messagebox.showerror("Error", str(ex))

        def load_sample(self):
            self.txt.delete("1.0", "end")
            self.txt.insert("1.0", SAMPLE_TEXT)
            self.status.set("Sample text loaded.")

        def clear_all(self):
            self.txt.delete("1.0", "end")
            self.tree.delete(*self.tree.get_children())
            self._set_buckets("")
            for v in self.stat_vars.values():
                v.set("-")
            self.table = None
            self.status.set("Cleared.")

        def analyze(self):
            text = self.txt.get("1.0", "end").strip()
            if not text:
                messagebox.showwarning("No input", "Please enter or load some text.")
                return
            self.table, total = count_keywords(
                text, self.var_case.get(), self.var_stop.get())
            self.refresh(total)
            self.status.set(f"Processed {total} words -> "
                            f"{self.table.n} unique keywords.")

        def refresh(self, total=None, highlight=None):
            t = self.table
            self.tree.delete(*self.tree.get_children())
            try:
                top = max(1, int(self.var_top.get()))
            except (tk.TclError, ValueError):
                top = 15
            for i, (k, c, b) in enumerate(sorted_results(t)[:top], 1):
                tag = "hit" if k == highlight else ("odd" if i % 2 else "")
                self.tree.insert("", "end", values=(i, k, c, b), tags=(tag,))
            if total is not None:
                self.stat_vars["Total words"].set(total)
            self.stat_vars["Unique keywords"].set(t.n)
            self.stat_vars["Table size"].set(t.size)
            self.stat_vars["Load factor"].set(f"{t.load_factor():.2f}")
            self.stat_vars["Collisions"].set(t.collisions)
            self.stat_vars["Longest chain"].set(t.longest_chain())
            lines = []
            for i, head in enumerate(t.buckets):
                chain, cur = [], head
                while cur:
                    chain.append(f"[{cur.key}:{cur.count}]")
                    cur = cur.next
                lines.append(f"{i:>3} | " + (" -> ".join(chain) if chain else "-"))
            self._set_buckets("\n".join(lines))

        def _set_buckets(self, s):
            self.bucket_txt.configure(state="normal")
            self.bucket_txt.delete("1.0", "end")
            self.bucket_txt.insert("1.0", s)
            self.bucket_txt.configure(state="disabled")

        def _need_table(self):
            if self.table is None:
                messagebox.showinfo("Info", "Click 'COUNT KEYWORDS' first.")
                return False
            return True

        def search(self):
            if not self._need_table():
                return
            key = self.var_search.get().strip()
            if self.var_case.get():
                key = key.lower()
            if not key:
                return
            c = self.table.get(key)
            if c:
                b = self.table.index_of(key)
                self.status.set(f"'{key}' found: frequency = {c}, bucket = {b}")
                self.var_top.set(max(self.var_top.get(), self.table.n))
                self.refresh(highlight=key)
            else:
                self.status.set(f"'{key}' not found in the hash table.")
                messagebox.showinfo("Search", f"'{key}' not found.")

        def delete(self):
            if not self._need_table():
                return
            key = self.var_search.get().strip()
            if self.var_case.get():
                key = key.lower()
            if self.table.delete(key):
                self.status.set(f"'{key}' deleted from the hash table.")
                self.refresh()
            else:
                messagebox.showinfo("Delete", f"'{key}' not found.")

        def export_csv(self):
            if not self._need_table():
                return
            path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV", "*.csv")])
            if path:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["Rank", "Keyword", "Frequency", "Bucket"])
                    for i, (k, c, b) in enumerate(sorted_results(self.table), 1):
                        w.writerow([i, k, c, b])
                self.status.set(f"Exported to {path}")

    App().mainloop()


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        run_gui()
