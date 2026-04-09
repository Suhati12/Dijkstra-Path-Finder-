import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import math
import random

# ── colour palette ──────────────────────────────────────────────
BG        = "#1e1e2e"
PANEL_BG  = "#2a2a3e"
ACCENT    = "#7c3aed"
BTN_ADD   = "#059669"
BTN_FIND  = "#2563eb"
BTN_CLR   = "#dc2626"
TEXT_CLR  = "#e2e8f0"
NODE_CLR  = "#4f46e5"
NODE_SEL  = "#f59e0b"
EDGE_CLR  = "#475569"
PATH_CLR  = "#10b981"
WEIGHT_CLR= "#fbbf24"

class Graph:
    def __init__(self):
        self.nodes = {}   # name -> [(neighbor, weight)]
        self.edges = []   # (src, dst, weight)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes[node] = []
            return True
        return False

    def add_edge(self, src, dst, weight):
        if src in self.nodes and dst in self.nodes:
            self.nodes[src].append((dst, weight))
            self.nodes[dst].append((src, weight))
            self.edges.append((src, dst, weight))
            return True
        return False

    def remove_node(self, node):
        if node not in self.nodes:
            return
        self.edges = [(s, d, w) for s, d, w in self.edges if s != node and d != node]
        del self.nodes[node]
        for n in self.nodes:
            self.nodes[n] = [(nb, w) for nb, w in self.nodes[n] if nb != node]

    def clear(self):
        self.nodes.clear()
        self.edges.clear()

    def dijkstra(self, start, end):
        if start not in self.nodes or end not in self.nodes:
            return None, float('inf')
        dist = {n: float('inf') for n in self.nodes}
        dist[start] = 0
        prev = {n: None for n in self.nodes}
        pq = [(0, start)]
        visited = set()
        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)
            if u == end:
                break
            for v, w in self.nodes[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        if dist[end] == float('inf'):
            return None, float('inf')
        path, cur = [], end
        while cur:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path, dist[end]


class DijkstraApp:
    NODE_R = 22

    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Dijkstra Path Finder")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.graph      = Graph()
        self.positions  = {}          # node -> (x, y)
        self.path_edges = set()       # highlighted edges
        self.path_nodes = set()       # highlighted nodes
        self.drag_node  = None
        self.drag_offset= (0, 0)

        self._build_ui()

    # ── UI layout ────────────────────────────────────────────────
    def _build_ui(self):
        # left panel
        panel = tk.Frame(self.root, bg=PANEL_BG, width=280)
        panel.pack(side="left", fill="y", padx=(10,0), pady=10)
        panel.pack_propagate(False)

        tk.Label(panel, text="🔍 Dijkstra Path Finder",
                 bg=PANEL_BG, fg=ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(pady=(15,10))

        self._section(panel, "➕ Add Node")
        self.node_var = tk.StringVar()
        self._entry(panel, self.node_var, "Node name (e.g. A)")
        self._btn(panel, "Add Node", self._add_node, BTN_ADD)

        self._section(panel, "🔗 Add Edge")
        self.src_var  = tk.StringVar()
        self.dst_var  = tk.StringVar()
        self.wgt_var  = tk.StringVar()
        self._entry(panel, self.src_var,  "Source node")
        self._entry(panel, self.dst_var,  "Destination node")
        self._entry(panel, self.wgt_var,  "Weight (number)")
        self._btn(panel, "Add Edge", self._add_edge, BTN_ADD)

        self._section(panel, "🚀 Find Shortest Path")
        self.start_var = tk.StringVar()
        self.end_var   = tk.StringVar()
        self._entry(panel, self.start_var, "Start node")
        self._entry(panel, self.end_var,   "End node")
        self._btn(panel, "Find Shortest Path", self._find_path, BTN_FIND)

        self._section(panel, "🗑️ Remove / Reset")
        self.del_var = tk.StringVar()
        self._entry(panel, self.del_var, "Node to delete")
        self._btn(panel, "Delete Node", self._delete_node, BTN_CLR)
        self._btn(panel, "Clear All",   self._clear_all,   BTN_CLR)

        # result box
        self._section(panel, "📋 Result")
        self.result_box = tk.Text(panel, height=7, bg="#0f0f1a", fg=PATH_CLR,
                                  font=("Consolas", 10), relief="flat",
                                  insertbackground=TEXT_CLR, wrap="word")
        self.result_box.pack(fill="x", padx=10, pady=4)

        # canvas (right)
        canvas_frame = tk.Frame(self.root, bg=BG)
        canvas_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(canvas_frame, text="🖱  Drag nodes  |  Canvas",
                 bg=BG, fg="#64748b", font=("Segoe UI", 9)).pack(anchor="ne")

        self.canvas = tk.Canvas(canvas_frame, bg="#0f0f1a",
                                highlightthickness=1,
                                highlightbackground=ACCENT)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>",  self._on_press)
        self.canvas.bind("<B1-Motion>",      self._on_drag)
        self.canvas.bind("<ButtonRelease-1>",self._on_release)

    # ── helpers ──────────────────────────────────────────────────
    def _section(self, parent, text):
        tk.Label(parent, text=text, bg=PANEL_BG, fg=ACCENT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(10,2))

    def _entry(self, parent, var, placeholder):
        e = tk.Entry(parent, textvariable=var, bg="#0f0f1a", fg=TEXT_CLR,
                     insertbackground=TEXT_CLR, relief="flat",
                     font=("Segoe UI", 10))
        e.pack(fill="x", padx=10, pady=2, ipady=5)
        # placeholder
        if not var.get():
            e.insert(0, placeholder)
            e.config(fg="#64748b")
            e.bind("<FocusIn>",  lambda ev, en=e, ph=placeholder, v=var: self._ph_in(ev,en,ph,v))
            e.bind("<FocusOut>", lambda ev, en=e, ph=placeholder, v=var: self._ph_out(ev,en,ph,v))

    def _ph_in(self, ev, entry, ph, var):
        if entry.get() == ph:
            entry.delete(0, tk.END)
            entry.config(fg=TEXT_CLR)

    def _ph_out(self, ev, entry, ph, var):
        if not entry.get():
            entry.insert(0, ph)
            entry.config(fg="#64748b")
            var.set("")

    def _btn(self, parent, text, cmd, color):
        tk.Button(parent, text=text, command=cmd,
                  bg=color, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"),
                  activebackground=color, cursor="hand2",
                  pady=6).pack(fill="x", padx=10, pady=3)

    def _get_var(self, var):
        v = var.get().strip()
        placeholders = {"Node name (e.g. A)", "Source node", "Destination node",
                        "Weight (number)", "Start node", "End node", "Node to delete"}
        return "" if v in placeholders else v

    # ── actions ──────────────────────────────────────────────────
    def _add_node(self):
        name = self._get_var(self.node_var)
        if not name:
            messagebox.showwarning("Input Error", "Enter a node name."); return
        if not self.graph.add_node(name):
            messagebox.showwarning("Duplicate", f"Node '{name}' already exists."); return
        # random position on canvas
        cw = self.canvas.winfo_width()  or 800
        ch = self.canvas.winfo_height() or 600
        x = random.randint(60, max(80, cw-60))
        y = random.randint(60, max(80, ch-60))
        self.positions[name] = (x, y)
        self.node_var.set("")
        self._redraw()

    def _add_edge(self):
        src = self._get_var(self.src_var)
        dst = self._get_var(self.dst_var)
        wgt = self._get_var(self.wgt_var)
        if not src or not dst or not wgt:
            messagebox.showwarning("Input Error", "Fill all edge fields."); return
        try:
            w = float(wgt)
            if w < 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Weight must be a non-negative number."); return
        if src not in self.graph.nodes:
            messagebox.showwarning("Missing Node", f"Node '{src}' not found."); return
        if dst not in self.graph.nodes:
            messagebox.showwarning("Missing Node", f"Node '{dst}' not found."); return
        self.graph.add_edge(src, dst, w)
        self.src_var.set(""); self.dst_var.set(""); self.wgt_var.set("")
        self._redraw()

    def _find_path(self):
        start = self._get_var(self.start_var)
        end   = self._get_var(self.end_var)
        if not start or not end:
            messagebox.showwarning("Input Error", "Enter start and end nodes."); return
        if start not in self.graph.nodes:
            messagebox.showwarning("Missing Node", f"Node '{start}' not found."); return
        if end not in self.graph.nodes:
            messagebox.showwarning("Missing Node", f"Node '{end}' not found."); return

        path, cost = self.graph.dijkstra(start, end)

        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)

        if path is None:
            self.path_edges.clear(); self.path_nodes.clear()
            self.result_box.insert(tk.END, f"❌ No path from '{start}' to '{end}'.")
        else:
            self.path_nodes = set(path)
            self.path_edges = set()
            for i in range(len(path)-1):
                self.path_edges.add((path[i], path[i+1]))
                self.path_edges.add((path[i+1], path[i]))

            arrow = " → ".join(path)
            self.result_box.insert(tk.END,
                f"✅ Shortest Path Found!\n\n"
                f"From : {start}\n"
                f"To   : {end}\n\n"
                f"Path : {arrow}\n\n"
                f"Cost : {cost}"
            )

        self.result_box.config(state="disabled")
        self._redraw()

    def _delete_node(self):
        name = self._get_var(self.del_var)
        if not name:
            messagebox.showwarning("Input Error", "Enter a node name to delete."); return
        if name not in self.graph.nodes:
            messagebox.showwarning("Not Found", f"Node '{name}' doesn't exist."); return
        self.graph.remove_node(name)
        self.positions.pop(name, None)
        self.path_edges.clear(); self.path_nodes.clear()
        self.del_var.set("")
        self._redraw()

    def _clear_all(self):
        if not messagebox.askyesno("Clear All", "Remove all nodes and edges?"): return
        self.graph.clear()
        self.positions.clear()
        self.path_edges.clear(); self.path_nodes.clear()
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.config(state="disabled")
        self._redraw()

    # ── canvas drawing ───────────────────────────────────────────
    def _redraw(self):
        self.canvas.delete("all")
        R = self.NODE_R

        # draw edges
        drawn = set()
        for src, dst, w in self.graph.edges:
            key = tuple(sorted([src, dst]))
            if key in drawn: continue
            drawn.add(key)
            x1,y1 = self.positions.get(src,(0,0))
            x2,y2 = self.positions.get(dst,(0,0))
            is_path = (src,dst) in self.path_edges
            color = PATH_CLR if is_path else EDGE_CLR
            width = 3 if is_path else 1.5
            self.canvas.create_line(x1,y1,x2,y2, fill=color, width=width, smooth=True)
            # weight label
            mx, my = (x1+x2)/2, (y1+y2)/2
            self.canvas.create_oval(mx-12,my-10,mx+12,my+10, fill="#1e1e2e", outline="")
            self.canvas.create_text(mx, my, text=str(int(w) if w==int(w) else w),
                                    fill=WEIGHT_CLR, font=("Segoe UI",8,"bold"))

        # draw nodes
        for name, (x,y) in self.positions.items():
            is_path = name in self.path_nodes
            fill    = PATH_CLR if is_path else NODE_CLR
            outline = NODE_SEL if is_path else ACCENT
            lw      = 3 if is_path else 2
            # shadow
            self.canvas.create_oval(x-R+3,y-R+3,x+R+3,y+R+3, fill="#00000055", outline="")
            self.canvas.create_oval(x-R,y-R,x+R,y+R, fill=fill, outline=outline, width=lw)
            self.canvas.create_text(x, y, text=name,
                                    fill="white", font=("Segoe UI",10,"bold"))

    # ── drag & drop nodes ────────────────────────────────────────
    def _node_at(self, x, y):
        R = self.NODE_R
        for name, (nx,ny) in self.positions.items():
            if math.hypot(x-nx, y-ny) <= R:
                return name
        return None

    def _on_press(self, event):
        self.drag_node = self._node_at(event.x, event.y)
        if self.drag_node:
            nx,ny = self.positions[self.drag_node]
            self.drag_offset = (event.x-nx, event.y-ny)

    def _on_drag(self, event):
        if self.drag_node:
            ox,oy = self.drag_offset
            self.positions[self.drag_node] = (event.x-ox, event.y-oy)
            self._redraw()

    def _on_release(self, event):
        self.drag_node = None


if __name__ == "__main__":
    root = tk.Tk()
    app  = DijkstraApp(root)
    root.mainloop()
