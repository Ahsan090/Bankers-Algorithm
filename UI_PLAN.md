# Plan: Complete the Banker's Algorithm UI

## Context
The project has a fully working Python backend (Process.py, Safety.py, System.py) implementing the Banker's deadlock-avoidance algorithm. The UI (ui.py) is a skeleton with only two entry fields and a Confirm button that just prints to console. The goal is to build a complete, functional Tkinter UI that lets users configure the system, enter all matrix data, visualize system state, and interactively submit resource requests.

---

## Files to Modify

| File | Change |
|------|--------|
| `Safety.py` | Return `(bool, sequence_list)` instead of just `bool` |
| `System.py` | Unpack new tuple; add `get_safe_sequence()` method |
| `ui.py` | Complete rewrite as `BankersApp` class |

`Process.py` and `main.py` — no changes needed.

---

## Backend Changes

### Safety.py
Add `sequence = []` before the while loop. After `p.is_finished = True`, append `sequence.append(p.pid)`. Change the return to `return is_work_safe(work), sequence`.

```python
def safety(Processes, available):
    work = Processes.copy()
    for p in work:
        p.is_finished = False
    sequence = []
    while True:
        progress = False
        for p in work:
            if all(p.need[j] <= available[j] for j in range(len(available))):
                available = [available[j] + p.allocation[j] for j in range(len(available))]
                p.is_finished = True
                sequence.append(p.pid)
                work.remove(p)
                progress = True
                break
        if not progress:
            break
    return is_work_safe(work), sequence
```

### System.py
- In `request()`: change `is_safe = safety(...)` to `is_safe, _ = safety(...)`
- Add new method:
```python
def get_safe_sequence(self):
    is_safe, sequence = safety(self.processes, self.available[:])
    return sequence if is_safe else None
```

---

## UI Architecture — BankersApp class

Single class owns the `tk.Tk` root. Screens are `ttk.Frame` instances destroyed and recreated on transitions. State lives on `self`.

```
BankersApp
├── __init__()              # root setup, style config, show_setup_screen()
├── _clear_screen()         # destroy self.current_frame
├── _fmt_vec(v)             # " ".join(map(str, v))
├── _log(message)           # append to ScrolledText log
├── show_setup_screen()     # Screen 1
├── _on_setup_confirm()     # validate → show_data_entry_screen()
├── show_data_entry_screen()# Screen 2
├── _on_data_confirm()      # validate → build system → show_main_screen()
├── show_main_screen()      # Screen 3
├── _refresh_main_screen()  # update treeview + labels
└── _submit_request()       # call system.request() → log → refresh
```

---

## Screen Designs

### Screen 1 — Setup
```
┌──────────────────────────────────────┐
│    Banker's Algorithm Simulator       │
│                                       │
│  Number of Processes:   [ 3 ]        │
│  Number of Resource Types: [ 3 ]     │
│                                       │
│          [ Configure System ]         │
└──────────────────────────────────────┘
```

### Screen 2 — Data Entry
```
┌─ Available Resources ─────────────────┐
│  R0 [ ] R1 [ ] R2 [ ]                │
└───────────────────────────────────────┘
┌─ Maximum Demand Matrix ───────────────┐
│      R0  R1  R2                       │
│  P0 [ ] [ ] [ ]                      │
│  P1 [ ] [ ] [ ]                      │
└───────────────────────────────────────┘
┌─ Allocation Matrix ───────────────────┐
│      R0  R1  R2                       │
│  P0 [ ] [ ] [ ]                      │
│  P1 [ ] [ ] [ ]                      │
└───────────────────────────────────────┘
[ ← Back ]              [ Initialize System ]
```

### Screen 3 — Main Simulator
```
┌─────────────────────────────────────────────────────────┐
│ Banker's Algorithm Simulator    [● SAFE STATE]          │
│ Available: 3 3 2                                         │
│ Safe Sequence: P1 → P3 → P0                             │
├──────────────────────────────────┬──────────────────────┤
│  PID  Allocation   Max    Need   │ Submit a Request:    │
│  P0   0 1 0      7 5 3  7 4 3   │ Process: [P1 ▼]      │
│  P1   2 0 0      3 2 2  1 2 2   │ R0[ ] R1[ ] R2[ ]    │
│  P2   3 0 2      9 0 2  6 0 0   │ [Submit Request]     │
│                                  ├──────────────────────┤
│                                  │ Request Log:         │
│                                  │ #1 P1 req [1,0,2]   │
│                                  │    → GRANTED         │
└──────────────────────────────────┴──────────────────────┘
[ Reset (Start Over) ]
```

- Status label: green `#27ae60` for SAFE, red `#e74c3c` for UNSAFE
- Treeview columns: PID | Allocation | Max | Need
- Log: read-only ScrolledText, auto-scrolls to bottom

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Non-integer in any entry | `messagebox.showerror`, stay on screen |
| Value < 0 | Same |
| n_proc/n_res > 20 | Same |
| allocation > max for any cell | `messagebox.showerror` naming P{i} R{j} |
| `system.request()` → False | Log "DENIED", refresh display |

---

## Verification

1. Run `python ui.py`
2. Enter 3 processes, 3 resources → click Configure
3. Enter test data from main.py (Available=[3,3,2])
4. Click Initialize — table populates, status shows SAFE, sequence shown
5. Submit P1=[1,0,2] → GRANTED in log, state updates
6. Submit unsafe request → DENIED in log, state unchanged
7. Click Reset → returns to Screen 1
