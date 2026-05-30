def is_work_safe(work):
    for p in work:
        if p.is_finished == False:
            return False
    return True

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