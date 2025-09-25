import sys

def solve():
    try:
        try:
            n_line = sys.stdin.readline()
            if not n_line:
                return
            n = int(n_line.strip())
        except EOFError:
            return
        except ValueError:
            return
        a = list(map(int, sys.stdin.readline().split()))
        b = list(map(int, sys.stdin.readline().split()))
        
    except EOFError:
        return
    except Exception:
        return

    s_excess = 0  
    s_deficit = 0 
    
    for i in range(n):
        diff = a[i] - b[i]
        
        if diff > 0:
            # a[i] > b[i]
            s_excess += diff
        elif diff < 0:
            s_deficit += abs(diff)
    result = max(s_excess, s_deficit)
    
    print(result)

def main():
    try:
        # Read the number of test cases t
        t_line = sys.stdin.readline()
        if not t_line:
            return
        t = int(t_line.strip())
    except EOFError:
        return
    except ValueError:
        return

    for _ in range(t):
        solve()

pass